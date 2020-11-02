'''
This file works with the mnlgxdlib zip file container for minilogue xd library files.
'''
import xml.etree.ElementTree as ET
import zipfile, traceback
import os
import re

'''
def test(file_path):
  zip_file = zipfile.ZipFile(file_path, mode='r')
  out = zipfile.ZipFile(file_path + '_copy.mnlgxdlib', mode='w')

  with zip_file as file, out as o:
    for f in zip_file.namelist():
      data = zip_file.read(f)
      o.writestr(f, data)
'''

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

def write_single_patch(patch_bin, file_path):
  with zipfile.ZipFile(file_path, mode='w') as zip_file:
    zip_file.write(os.path.join('assets','patch_template', 'Prog_000.prog_info'), 'Prog_000.prog_info')
    zip_file.write(os.path.join('assets','patch_template', 'FileInformation.xml'), 'FileInformation.xml')
    zip_file.writestr('Prog_000.prog_bin', patch_bin)
