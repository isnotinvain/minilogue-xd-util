'''
This file works with the mnlgxdlib zip file container for minilogue xd library files.
'''

import os
import re
import tempfile
import traceback
import zipfile

import fileinformation

ACCEPTED_FILE_SUFFIXES = ['.mnlgxdprog', '.mnlgxdlib']

def validate_and_open_file(file_path):
  valid_suffix = next((True for x in ACCEPTED_FILE_SUFFIXES if file_path.endswith(x)), False)
  if not valid_suffix:
    raise ValueError('Must pass a file that ends with oneof: {} found {}'.format(ACCEPTED_FILE_SUFFIXES, file_path))

  try:
    zip_file = zipfile.ZipFile(file_path, mode='r')
  except zipfile.BadZipfile:
    traceback.print_exc()
    raise ValueError('File does not appear to be a valid file (it is not a valid zip file)')

  return zip_file

def extract_patch_bin(file_path, patch_number):
  with validate_and_open_file(file_path) as file:
    return file.read('Prog_%03d.prog_bin'  % patch_number)

def extract_all_patch_bins(file_path):
  res = []

  with validate_and_open_file(file_path) as file:
    for n in file.namelist():
      if re.match(fileinformation.PROG_BIN_RE, n):
          res.append((n, file.read(n)))

  return res

def overwrite_files(file_path, new_files, new_out_file):
  if os.path.exists(new_out_file):
    raise ValueError('File already exists: {}'.format(new_out_file))

  temp = tempfile.mkdtemp()
  copy = os.path.join(temp, 'copy')
  os.mkdir(copy)

  # explode the input zip into temp/copy/*
  with zipfile.ZipFile(file_path, mode='r') as orig:
    orig.extractall(copy)

  # overwrite each file in temp/copy/* that we were asked to overwrite
  for f,f_bin in new_files.iteritems():
    with open(os.path.join(copy, f), 'w') as new_f:
      new_f.write(f_bin)

  # now make a new zip, at temp/zipped.zip
  new_zip_path = os.path.join(temp, 'zipped.zip')

  with zipfile.ZipFile(new_zip_path, mode='w') as new_zip:
    for f in os.listdir(copy):
      new_zip.write(os.path.join(copy, f), f)

  # move zipped.zip to the expected output file
  os.rename(new_zip_path, new_out_file)

# shortcut for writing a patch file, which is actually a library file w/ only 1 patch in it
# copies a static FileInformation and prog_info file into the library and then writes the
# given prog_bin
def write_single_patch(patch_bin, file_path):
  with zipfile.ZipFile(file_path, mode='w') as zip_file:
    zip_file.write(os.path.join('assets','patch_template', 'Prog_000.prog_info'), 'Prog_000.prog_info')
    zip_file.write(os.path.join('assets','patch_template', 'FileInformation.xml'), 'FileInformation.xml')
    zip_file.writestr('Prog_000.prog_bin', patch_bin)
