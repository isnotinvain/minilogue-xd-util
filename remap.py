import sys
import xd_prog_bin
import mnlgxdprog
import json

USAGE = '\n'.join([
  'Usage:',
  'python remap.py my_patch.mnlgxdprog <remap_json>',
  'python remap.py my_lib.mnlgxdlib <patch_number> <remap_json>',
  'Where <patch_number> is the patch to remap, starting at 1 for the first patch'
])

'''
{"osc": [[1,2], [3,4]]}
'''

if len(sys.argv) < 3:
  raise ValueError(Usage)

file_path = sys.argv[1]

if file_path.endswith('mnlgxdlib'):
  patch_number = int(sys.argv[2])
  remap_json = sys.argv[3]
else:
  patch_number = 0
  remap_json = sys.argv[2]

remap = json.loads(remap_json)

patch = mnlgxdprog.extract_patch(file_path, patch_number)

if 'osc' in remap:
  osc = dict(remap['osc'])
  curr = patch['multi_user_osc']
  if curr in osc:
    patch['multi_user_osc'] = osc[curr]

print patch.nice_string()