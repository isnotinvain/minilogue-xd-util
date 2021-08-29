'''
This file works with the FileInformation.xml file in mnlgxdlib / mnlgxdprog files.

It's sort of a strange format given that I think all libraries have all 500 patch files,
and all the tune and scale files, or just 1 patch file and that's it. Also all the _info
file seem to be empty. So I'm not really sure how necessary this file is, but here it
is anyway. Not sure why sound librarian needs this file and can't just scan the zip
for what's there...
'''

import os
import re
import xml.etree.ElementTree as ET

PROG_BIN_RE = 'Prog_(\d{3})\.prog_bin'
PROG_INFO_RE = 'Prog_(\d{3})\.prog_info'

TUNS_BIN_RE = 'TunS_(\d{3})\.TunS_bin'
TUNS_INFO_RE = 'TunS_(\d{3})\.TunS_info'

TUNO_BIN_RE = 'TunO_(\d{3})\.TunO_bin'
TUNO_INFO_RE = 'TunO_(\d{3})\.TunO_info'

def look_for(f, files, kind, suffix = None):

  if not suffix:
    suffix = kind

  base = kind + '_' + '(\d{3})\.' + suffix
  bin_re = base + '_bin'
  info_re = base + '_info'

  base_fmt = kind + '_{i:03d}' + suffix
  bin_fmt = base_fmt + kind + '_bin'
  info_fmt = base_fmt + kind + '_info'

  found = False

  m = re.match(bin_re, f)
  if m:
    found = True
    id = m.group(1)
    info = info_fmt.format(id)
    if not info in files:
      print('Warning! Missing: {}'.format(info))

  m = re.match(info_re, f)
  if m:
    id = m.group(1)
    binf = bin_fmt.format(id)
    if not binf in files:
      print('Warning! Missing: {}'.format(binf))

  return found

def mk_file_info_xml_from_dir(dir_path):
  patch_files = 0
  has_fave_data = False
  tune_scale_data = 0
  tune_oct_data = 0
  files = set(os.listdir(dir_path))

  for f in files:

    if f == 'FavoriteData.fav_data':
        has_fave_data = True

    if f == 'FileInformation.xml':
      pass

    elif look_for(f, files, 'Prog', 'prog'):
      patch_files = patch_files + 1

    elif look_for(f, files, 'TunS'):
      tune_scale_data = tune_scale_data + 1

    elif look_for(f, files, 'TunO'):
      tune_oct_data = tune_oct_data + 1

    else:
      print('Warning! Unexpected file: {}'.format(f))

  return mk_file_info_xml(patch_files, has_fave_data, tune_scale_data, tune_oct_data)

def mk_file_info_xml(patch_files=0, has_fave_data=False, tune_scale_data=0, tune_oct_data=0):
  root = ET.Element('KorgMSLibrarian_Data')
  product = ET.SubElement(root, 'Product')
  product.text = 'minilogue xd'
  contents = ET.SubElement(root, 'Contents')

  contents.set('NumProgramData', str(patch_files))
  contents.set('NumPresetInformation', '0')
  contents.set('NumTuneScaleData', str(tune_scale_data))
  contents.set('NumTuneOctData', str(tune_oct_data))

  if has_fave_data:
    contents.set('NumFavoriteData', '1')
    fave_data = ET.SubElement(contents, 'FavoriteData')
    fave_file = ET.SubElement(fave_data, 'File')
    fave_file.text = 'FavoriteData.fav_data'
  else:
    contents.set('NumFavoriteData', '0')

  for i in xrange(0, patch_files):
    data = ET.SubElement(contents, 'ProgramData')
    info = ET.SubElement(data, 'Information')
    info.text = 'Prog_{i:03d}.prog_info'.format(i)
    binary = ET.SubElement(data, 'ProgramBinary')
    binary.text = 'Prog_{i:03d}.prog_bin'.format(i)

  for i in xrange(0, tune_scale_data):
    data = ET.SubElement(contents, 'TuneScaleData')
    info = ET.SubElement(data, 'Information')
    info.text = 'TunS_{i:03d}.TunS_info'.format(i)
    binary = ET.SubElement(data, 'TuneScaleBinary')
    binary.text = 'TunS_{i:03d}.TunS_bin'.format(i)

  for i in xrange(0, tune_oct_data):
    data = ET.SubElement(contents, 'TuneOctData')
    info = ET.SubElement(data, 'Information')
    info.text = 'TunO_{i:03d}.TunO_info'.format(i)
    binary = ET.SubElement(data, 'TuneScaleBinary')
    binary.text = 'TunO_{i:03d}.TunO_bin'.format(i)

  str = ET.tostring(root)
  # there's probably a better way to do this but...
  header = '<?xml version="1.0" encoding="UTF-8"?>\n\n'
  str = header + str
