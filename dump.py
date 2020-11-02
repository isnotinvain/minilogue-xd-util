import sys, zipfile, traceback
import xd_prog_bin
import mnlgxdprog

USAGE = '\n'.join([
  'Usage:',
  'python dump.py my_patch.mnlgxdprog',
  'python dump.py my_lib.mnlgxdprog <patch_number>',
  'Where <patch_number> is the patch to dump, starting at 1 for the first patch'
])

if len(sys.argv) < 2:
  raise ValueError(Usage)

file_path = sys.argv[1]

patch_number = 0

if file_path.endswith('mnlgxdlib'):
  patch_number = int(sys.argv[2])

patch = mnlgxdprog.extract_patch(file_path, patch_number)

print patch.nice_string()