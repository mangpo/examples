"""Dataflow job to evaluate the model for retrieving code from natural language queary."""
import logging

import apache_beam as beam

import code_search.dataflow.cli.arguments as arguments
import code_search.dataflow.transforms.string_embeddings as string_embed

num_test = 100000

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
    | "Compute Docstring Embeddings" >> string_embed.FunctionEmbeddings(args.problem,
                                                                       args.data_dir,
                                                                       args.saved_model_dir,
                                                                       False)
  )

  # For each query, find the top K most relevant functions according to the model.


if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO,
                      format=('%(levelname)s|%(asctime)s'
                              '|%(pathname)s|%(lineno)d| %(message)s'),
                      datefmt='%Y-%m-%dT%H:%M:%S',
                      )
  logging.getLogger().setLevel(logging.INFO)
  evaluate_model()
