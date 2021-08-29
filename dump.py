import sys

import mnlgxdprog
import cmdline_util

USAGE = '\n'.join([
  'Usage:',
  'python dump.py my_patch.mnlgxdprog',
  'python dump.py my_lib.mnlgxdlib <patch_expr>',
  'Where <patch_expr> is the patch to dump, starting at 1 for the first patch, or a range in the form 1:100 (inclusive)'
])

if len(sys.argv) < 2:
  raise ValueError(Usage)

file_path = sys.argv[1]

if file_path.endswith('mnlgxdlib'):
  if len(sys.argv) < 3:
    raise ValueError(Usage)
  patch_numbers = cmdline_util.patch_number_expr(sys.argv[2])
else:
  patch_numbers = range(0 , 1)

for patch in patch_numbers:
  patch = mnlgxdprog.extract_patch(file_path, patch)
  print(patch.pretty_print())
  print()
