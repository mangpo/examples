"""Dataflow job to evaluate the model for retrieving code from natural language queary."""
import logging
import csv
import os
import tensorflow as tf
import apache_beam as beam

import code_search.dataflow.cli.arguments as arguments
import code_search.dataflow.do_fns.dict_to_csv as dict_to_csv
import code_search.dataflow.transforms.function_embeddings as function_embed
import code_search.dataflow.transforms.retrieve_functions as retrieve_functions

num_test = 10
k = 10

def evaluate_model(argv=None):
  pipeline_opts = arguments.prepare_pipeline_opts(argv)
  args = pipeline_opts._visible_options  # pylint: disable=protected-access

  pipeline = beam.Pipeline(options=pipeline_opts)

  if args.token_pairs_table:
    token_pairs_query = gh_bq.ReadTransformedGithubDatasetQuery(
      args.token_pairs_table)
    token_pairs_query.limit = num_test
    token_pairs_source = beam.io.BigQuerySource(
      query=token_pairs_query.query_string, use_standard_sql=True)
    token_pairs = (pipeline
      | "Read Transformed Github Dataset" >> beam.io.Read(token_pairs_source)
    )
  else:
    read_dataset = gh_bq.ReadGithubDataset(args.project)
    read_dataset.limit = num_test
    token_pairs = (pipeline
      | "Read Github Dataset" >> read_dataset
      | "Transform Github Dataset" >> github_dataset.TransformGithubDataset(None, None)
    )

  # Emded string queries.
  embeddings = (token_pairs
    | "Compute Docstring Embeddings" >> function_embed.FunctionEmbeddings(args.problem,
                                                                       args.data_dir,
                                                                       args.saved_model_dir,
                                                                       False)
  )

  # For each query, find the top K most relevant functions according to the model.
  if not os.path.isdir(args.tmp_dir):
    os.makedirs(args.tmp_dir)

  logging.info('Reading %s', args.lookup_file)
  lookup_data = []
  with tf.gfile.Open(args.lookup_file) as lookup_file:
    reader = csv.reader(lookup_file)
    for row in reader:
      lookup_data.append(row)

  tmp_index_file = os.path.join(args.tmp_dir, os.path.basename(args.index_file))

  logging.info('Reading %s', args.index_file)
  if not os.path.isfile(tmp_index_file):
    tf.gfile.Copy(args.index_file, tmp_index_file)

  top_k_functions = (embeddings
    | "Retreive Top K Functions" >> retrieve_functions.FunctionsRetrieval(
        index_file, lookup_data, k)
  )

  # frank = (top_k_functions
  #   | "Compute FRank" >> retrieve_functions.FRank())

  # mean_frank = (frank
  #  | "Compute average FRank" >> beam.CombineValues(beam.combiners.MeanCombineFn()))
  # logging.info(mean_frank)

  # with_top_1 = (
  #   | "Compute Within Top K" >> retrieve_functions.WithinTop([1, 5, 10]))

  (top_k_functions  # pylint: disable=expression-not-assigned
    | "Format for CSV Write" >> beam.ParDo(dict_to_csv.TopFunctionsToCSVString(10))
    | "Write CSV" >> beam.io.WriteToText('{}/top-functions'.format(args.eval_dir),
                                         file_name_suffix='.csv',
                                         num_shards=1)
  )

  result = pipeline.run()
  logging.info("Submitted Dataflow job: %s", result)
  if args.wait_until_finished:
    result.wait_until_finish()

  return result


if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO,
                      format=('%(levelname)s|%(asctime)s'
                              '|%(pathname)s|%(lineno)d| %(message)s'),
                      datefmt='%Y-%m-%dT%H:%M:%S',
                      )
  logging.getLogger().setLevel(logging.INFO)
  evaluate_model()
