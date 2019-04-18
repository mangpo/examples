"""Beam DoFns specific to `code_search.dataflow.transforms.retrieve_functions`."""

import apache_beam as beam
import nmslib

from code_search.nmslib.search_engine as search_engine


class RetrieveFunctions(beam.DoFn):
  """Retrieve top k functions given a natural language query."""

  def __init__(self, index_file, lookup_data, k):
    self.index = search_engine.CodeSearchEngine.nmslib_init()
    self.index.loadIndex(index_file)
    self.lookup_data = lookup_data
    self.k = k

  def process(self, element, *_args, **_kwargs):
    """
    Args:
      element: A Python dict of the form,
        {
          "nwo": "STRING",
          "path": "STRING",
          "function_name": "STRING",
          "lineno": "STRING",
          "original_function": "STRING",
          "docstring_embedding": "STRING",
        }

    Yields:
      A pair of the input element and a list of top k functions.
    """

    idxs, dists = self.index.knnQuery(element, k=self.k)

    results = [dict(zip(self.DICT_LABELS, self.lookup_data[id])) for id in idxs]
    for i, dist in enumerate(dists):
      results[i]['score'] = str(dist)
    yield (element, results)


class FRank(beam.DoFn):
  """Find the rank of the original function."""

  def process(self, org_results_pair, *_args, **_kwargs):
    org = org_results_pair[0]
    results = org_results_pair[1]
    rank = 100
    for i in range(len(results)):
      if org['original_function'] == results[i]['original_function']:
        rank = i
        break

    return rank


class WithinCutoffs(beam.DoFn):
  """Determine if the number is within a given list of cutoffs."""

  def __init__(self, cutoffs):
    self.cutoffs = cutoffs

  def process(self, x, *_args, **_kwargs):
    yield [x < cutoff for cutoff in self.cutoffs]
