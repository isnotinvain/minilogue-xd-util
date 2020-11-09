'''
# TODO: use a test framework / runner
'''
import os
import mnlgxdprog
import mnlgxdlib
import xd_prog_bin

def round_trip(patch_bin):
    parsed = xd_prog_bin.parse(patch_bin)
    print 'Patch name: {}'.format(parsed['name'])
    serialized = parsed.serialize()

    if serialized != patch_bin:
      raise ValueError('Patch {} did not round trip successfully'.format(parsed['name']))
    else:
      print 'Successfully round tripped: {}'.format(parsed['name'])
      print

def test_patches_round_trip():
  root = 'tests/patches/valid'
  patch_files = os.listdir(root)

  for f in patch_files:
    print 'round trip patch: {}'.format(f)
    patch_bin = mnlgxdprog.extract_patch_bin(os.path.join(root, f))
    round_trip(patch_bin)

def test_libraries_round_trip():
  root = 'tests/libraries/'
  library_files = os.listdir(root)

  for f in library_files:
    print 'round trip library: {}'.format(f)
    for p_file, p_bin in mnlgxdlib.extract_all_patch_bins(os.path.join(root, f)):
      print '-> {}'.format(p_file)
      round_trip(p_bin)

def test_patches_pp():
  root = 'tests/patches/valid'
  patch_files = os.listdir(root)

  for f in patch_files:
    print 'pp: {}'.format(f)
    patch_bin = mnlgxdprog.extract_patch_bin(os.path.join(root, f))
    parsed = xd_prog_bin.parse(patch_bin)
    ignored = parsed.pretty_print()

def test_libraries_pp():
  root = 'tests/libraries/'
  library_files = os.listdir(root)

  for f in library_files:
    print 'pp library: {}'.format(f)
    for p_file, p_bin in mnlgxdlib.extract_all_patch_bins(os.path.join(root, f)):
      print '-> {}'.format(p_file)
      parsed = parsed = xd_prog_bin.parse(p_bin)
      ignored = parsed.pretty_print()

test_patches_round_trip()
print '-----------'
test_libraries_round_trip()
print '-----------'
test_patches_pp()
print '-----------'
test_libraries_pp()
