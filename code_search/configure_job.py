"""Configure XXX.yaml file with the parameters defined in params_file.

Copy file XXX.yaml to jobs/XXX.yaml and replace {{KEY}} with VALUE, where KEYs and VALUEs are the keys and values inside the the field current defined in params_file.
"""

import json
import os
import sys

params_file = 'params.json'
out_dir = 'jobs'

def configure(path):
  if not os.path.isdir(out_dir):
    os.system('mkdir {0}'.format(out_dir))

  start = path.rfind('/') + 1
  filename = path[start:]
  os.system('cp {0} {1}/{2}'.format(path, out_dir, filename))
  with open(params_file) as json_file:
    data = json.load(json_file)
    params = data['current']
    for key in params:
      command = 'sed -i\'\' "s,{{{{{0}}}}},{1}," {2}/{3}'.format(key.upper(), params[key], out_dir, filename)
      os.system(command)

  os.system('cat {0}/{1}'.format(out_dir, filename))

if __name__ == '__main__':
  configure(sys.argv[1])
