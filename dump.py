import sys
import mnlgxdprog

USAGE = '\n'.join([
  'Usage:',
  'python dump.py my_patch.mnlgxdprog',
  'python dump.py my_lib.mnlgxdlib <patch_number>',
  'Where <patch_number> is the patch to dump, starting at 1 for the first patch'
])

if len(sys.argv) < 2:
  raise ValueError(Usage)

file_path = sys.argv[1]

patch_number = 0

if file_path.endswith('mnlgxdlib'):
  if len(sys.argv) < 3:
    raise ValueError(Usage)
  pn = int(sys.argv[2])
  if pn <= 0:
    raise ValueError('Patch number must be >= 1')
  patch_number = pn - 1

patch = mnlgxdprog.extract_patch(file_path, patch_number)

print patch.pretty_print()