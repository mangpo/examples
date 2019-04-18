import apache_beam as beam

import code_search.dataflow.do_fns.retrieve_functions as retrieve_funcs

class FunctionsRetrieval(beam.PTransform):
  """Retrieve top k functions given a natural language query."""

  def __init__(self, index_file, lookup_data, k):
    self.index_file = index_file
    self.lookup_data = lookup_data
    self.k = k

  def expand(self, embeddings):
    batch_functions = (embeddings
      | "Retrieve most relevant functions" >> beam.ParDo(retrieve_funcs.RetrieveFunctions(self.index_file, self.lookup_data, self.k)))

    return batch_functions


class FRank(beam.PTransform):
  """Find the rank of the original function."""

  def expand(self, org_results_pair):
    frank = (org_results_pair,
      | "Compute FRank" >> beam.ParDo(retrieve_funcs.FRank()))

    return frank


class WithinTop(beam.PTransform):
  """Determine if the frank is within a given list of cutoffs."""

  def __init__(self, cutoffs):
    self.cutoffs = cutoffs

  def expand(self, frank):
    answers = (frank,
      | "Check FRank Within Cutoffs" >> beam.ParDo(retrieve_funcs.WithinCutoffs(self.cutoffs)))

    return answers
