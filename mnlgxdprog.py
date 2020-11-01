'''
This file works with the mnlgxdprog zip file container for minilogue xd patch files.
mnlgxdprog files are essentially mnlgxdlib files with fewer items in them, so mostly
delegates to mnlgxdlib.py
'''

import zipfile, traceback
import xd_prog_bin
import mnlgxdlib

def extract_patch_bin(file_path):
  return mnlgxdlib.extract_patch_bin(file_path, 0)

def extract_patch(file_path):
  return xd_prog_bin.deserialize(extract_patch_bin(file_path))

def write(patch, file_path):
  patch_bin = xd_prog_bin.serialize(patch)
  mnlgxdlib.write_single_patch(patch_bin, file_path)
