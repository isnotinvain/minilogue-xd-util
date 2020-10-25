import sys, zipfile, traceback
import parser

if len(sys.argv) != 2:
  raise ValueError('Usage: python go.py file_to_parse.mnlgxdprog')

filePath = sys.argv[1]

if not filePath.endswith('.mnlgxdprog'):
  raise ValueError('Must pass a .mnlgxdprog file, found "%s"' % filePath)

try:
  zip_file = zipfile.ZipFile(filePath, mode='r')
except zipfile.BadZipfile:
  traceback.print_exc()
  raise ValueError('File does not appear to be a mnlgxdprog file (it is not a valid zip file)')

with zip_file as file:
  file_content = file.read('Prog_%03d.prog_bin'  % (0,))
  res = parser.parse(file_content)

  print "File contents:"
  for k,v in res.iteritems():
    print "%s => %s" % (k, v)

  packed = parser.write(res)

  if packed != file_content:
    print "Files don't match"
  else:
    print "Files match!"