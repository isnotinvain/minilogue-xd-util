import os
import mnlgxdprog
import xd_prog_bin

root = 'tests/patches/valid'
patch_files = os.listdir(root)

for f in patch_files:
  print 'testing {}'.format(f)
  original = mnlgxdprog.extract_patch_bin(os.path.join(root, f))
  parsed = xd_prog_bin.deserialize(original)
  print 'Patch name: {}'.format(parsed['name'])
  serialized = parsed.serialize()

  if serialized != original:
    raise ValueError('File {} did not round trip successfully'.format(f))
  else:
    print 'Successfully round tripped: {}'.format(f)
    print