import sys, zipfile, traceback
import xd_prog_bin
import mnlgxdprog


if len(sys.argv) != 2:
  raise ValueError('Usage: python dump.py file.mnlgxdprog')

file_path = sys.argv[1]

patch = mnlgxdprog.extract_patch(file_path)

for k,v in patch.iteritems():
  print "%s => %s" % (k, v)