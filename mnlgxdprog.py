'''
This file works with the mnlgxdprog zip file container for minilogue xd patch files.
mnlgxdprog files are essentially mnlgxdlib files with fewer items in them, so mostly
delegates to mnlgxdlib.py
'''

import zipfile, traceback
import xd_prog_bin
import mnlgxdlib

def extract_patch_bin(file_path, patch_number = 0):
  return mnlgxdlib.extract_patch_bin(file_path, patch_number)

def extract_patch(file_path, patch_number = 0):
  return xd_prog_bin.parse(extract_patch_bin(file_path, patch_number))

def write(patch, file_path):
  patch_bin = patch.serialize()
  mnlgxdlib.write_single_patch(patch_bin, file_path)
