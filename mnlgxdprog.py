'''
This file works with the mnlgxdprog zip file container for minilogue xd patch files
'''

import zipfile, traceback
import xd_prog_bin

def extract_patch(file_path):
  return xd_prog_bin.deserialize(extract_patch_bin(file_path))

def extract_patch_bin(file_path):

  if not file_path.endswith('.mnlgxdprog'):
    raise ValueError('Must pass a .mnlgxdprog file, found "%s"' % file_path)

  try:
    zip_file = zipfile.ZipFile(file_path, mode='r')
  except zipfile.BadZipfile:
    traceback.print_exc()
    raise ValueError('File does not appear to be a mnlgxdprog file (it is not a valid zip file)')

  with zip_file as file:
    return file.read('Prog_%03d.prog_bin'  % 0)

def write(patch, file_path):
  patch_bin = xd_prog_bin.serialize(patch)
  write_bin(patch_bin, file_path)

def write_bin(patch_bin, file_path):
  if not file_path.endswith('.mnlgxdprog'):
    raise ValueError('Must pass a .mnlgxdprog file path')

  with zipfile.ZipFile(file_path, mode='w') as zip_file:
    zip_file.write('assets/Prog_000.prog_info', 'Prog_000.prog_info')
    zip_file.write('assets/FileInformation.xml', 'FileInformation.xml')
    zip_file.writestr('Prog_000.prog_bin', patch_bin)