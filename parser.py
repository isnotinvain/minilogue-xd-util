import traceback
import file_format

def assert_header(file_content):
  try:
    magic = file_format.unpack(file_content[:4], [file_format.HEADER_SCHEMA])
  except:
    traceback.print_exc()
    raise ValueError('Could not unpack magic hader from file, is this in invalid file?')

  if magic['magic'] != 'PROG':
    raise ValueError('File does not begin with magic header PROG')

def parse(file_content):

  # first look for magic header as sanity check
  assert_header(file_content)

  unpacked = file_format.unpack(file_content, file_format.FILE_SCHEMA)

  # seems unlikely but check the magic field again anyway
  if (unpacked['magic'] != 'PROG'):
    raise ValueError("This doesn't look like a valid file, magic PROG header incorrect")



  for k,v in unpacked.iteritems():
    print "%s => %s" % (k,v)
