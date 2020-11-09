import collections
import os
import sys

import cmdline_util
import mnlgxdprog
import mnlgxdlib

USAGE = '\n'.join([
  'Usage:',
  'python remap.py my_patch.mnlgxdprog <remap_expr> <remap_expr> <remap_expr>....',
  'python remap.py my_lib.mnlgxdlib <patch_expr> <remap_expr>',
  'Where <patch_expr> is the patch to remap, starting at 1 for the first patch, or a range in the form 1:100 (inclusive)',
  'And <remap_expr> is in the form osc:1:2 to map user oscillator 1 to 2, or rev:1:2, or del:1:2, or mod:1:2'
])

def remap_patch(patch, remaps):
  did_remap = False

  for f,t in remaps['osc'].iteritems():
    if not 1 <= t <= 16:
      raise ValueError('User oscillators must be between 1 and 16')

    if patch['multi_user_osc'] == f:
      print 'Remapping user oscillator {} to {} for {}'.format(f, t, patch['name'])
      patch['multi_user_osc'] = t
      did_remap = True

  for f,t in remaps['rev'].iteritems():
    if not 1 <= t <= 8:
      raise ValueError('Reverb must be between 1 and 8')

    current = patch['reverb_type']
    if current.startswith('USER'):
      current_i = int(current[len('USER'):])
      if current == f:
        print 'Remapping user reverb {} to {} for {}'.format(f, t, patch['name'])
        patch['reverb_type'] = 'USER{}'.format(t)
        did_remap = True

  for f,t in remaps['del'].iteritems():
    if not 1 <= t <= 8:
      raise ValueError('Delay must be between 1 and 8')

    current = patch['delay_type']
    if current.startswith('USER'):
      current_i = int(current[len('USER'):])
      if current == f:
        print 'Remapping user delay {} to {} for {}'.format(f, t, patch['name'])
        patch['delay_type'] = 'USER{}'.format(t)
        did_remap = True

  for f,t in remaps['mod'].iteritems():
    if not 1 <= t <= 8:
      raise ValueError('Mod must be between 1 and 8')

    if patch['mod_fx_user'] == f:
      print 'Remapping user mod fx {} to {} for {}'.format(f, t, patch['name'])
      patch['mod_fx_user'] = t
      did_remap = True

  return did_remap

if len(sys.argv) < 3:
  raise ValueError(Usage)

file_path = sys.argv[1]

is_library = file_path.endswith('mnlgxdlib')

if is_library:
  if len(sys.argv) < 4:
    raise ValueError(Usage)
  patch_numbers = cmdline_util.patch_number_expr(sys.argv[2])
  remap_exprs = sys.argv[3:]
else:
  remap_exprs = sys.argv[2:]

remaps = collections.OrderedDict()
remaps['osc'] = collections.OrderedDict()
remaps['rev'] = collections.OrderedDict()
remaps['del'] = collections.OrderedDict()
remaps['mod'] = collections.OrderedDict()

for e in remap_exprs:
  (kind, old, new) = e.split(':', 2)
  old = int(old)
  new = int(new)
  remaps[kind][old] = new

print 'Will make the following remappings:'
for kind,r in remaps.iteritems():
  print '{}:'.format(kind)
  for f,t in r.iteritems():
    print '\t{} to {}'.format(f, t)

if is_library:
  rewritten = {}
  for pi in patch_numbers:
    patch = mnlgxdprog.extract_patch(file_path, pi)
    if remap_patch(patch, remaps):
      bin_file = 'Prog_{:03d}.prog_bin'.format(pi)
      rewritten[bin_file] = patch.serialize()

  if len(rewritten) > 0:
    new_path = file_path[:-len('.mnlgxdlib')] + '_remapped.mnlgxdlib'
    mnlgxdlib.overwrite_files(file_path, rewritten, new_path)
    print 'Remapped written to {}'.format(new_path)
  else:
    print 'Didn\'t find anything to remap!'

else:
  patch = mnlgxdprog.extract_patch(file_path, patch_number)
  if remap_patch(patch, remaps):
    new_path = file_path[:-len('.mnlgxdprog')] + '_remapped.mnlgxdprog'
    if os.path.exists(new_path):
      raise ValueError('File already exists: {}'.format(new_path))
    mnlgxdprog.write(patch, new_path)
    print 'Remapped written to {}'.format(new_path)
  else:
    print 'Didn\'t find anything to remap!'
