"""Beam DoFns specific to `code_search.dataflow.transforms.retrieve_functions`."""

import apache_beam as beam
import nmslib

from code_search.nmslib.search_engine as search_engine


class RetrieveFunctions(beam.DoFn):
  """TODO(mangpo): comment"""

  def __init__(self, index_file, lookup_data, k):
    self.index = search_engine.CodeSearchEngine.nmslib_init()
    self.index.loadIndex(index_file)
    self.lookup_data = lookup_data
    self.k = k

  def process(self, embedding, *_args, **_kwargs):
    idxs, dists = self.index.knnQuery(embedding, k=self.k)

    results = [dict(zip(self.DICT_LABELS, self.lookup_data[id])) for id in idxs]
    for i, dist in enumerate(dists):
      results[i]['score'] = str(dist)
    return results
