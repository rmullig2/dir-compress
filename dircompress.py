#!/usr/bin/python
import os
import argparse
import sys
import re

def parse_arguments():
  """
  This function utilizes the argparse library to parse the incoming arguments.
  There are four defined arguments: directory name, email address, minimum file size, and dry run option.
  The library automatically generates the help option and version information.
  """
  parser = argparse.ArgumentParser(version="Version 1.0")
  parser.add_argument('-d', action='store', dest='dir_name', help='Specifies the directory for compression', required=True)
  parser.add_argument('-e', action='store', dest='email', help='Specifies the email address', required=True)
  parser.add_argument('-s', action='store', dest='file_size', help='Specifies the minimum file size to compress: NUMBER[K|M|G]', required=True)
  parser.add_argument('--dry-run', action='store_true', default=False, dest='dry_run',
                    help='Add this switch to show saved space without compressing')
  return parser

def check_arguments(dir_name, email, file_size):
  """
  This function will validate the parameters passed for directory name, email address, and minimum file size.
  The os library is used to check for a valid directory.
  Regular expressions are defined for checking the email address and minimum file size.
  """
  if not os.path.isdir(dir_name):
    print "Invalid path name: " + dir_name
    sys.exit(2)
  if re.match("[^@]+@[^@]+\.[^@]+", email) == None:
    print 'Invalid email address: ' + email
    sys.exit(2)
  if re.match("[0-9]+\.?[0-9MmGgKk]*$", file_size) == None:     # This allows floating point values with K, M, G suffix
    print "Invalid file size, must be integer or floating point value followed by optional suffix (K, M, G)"
    sys.exit(2)
  return

def convert_size(file_size):
  """
  This function will take the file size entered by the user and stored in a string.
  It will determine if the value is in bytes, kilobytes, megabytes, or gigabytes.
  Then it will calculate the file size in bytes and return an integer.
  """
  last_char = file_size[-1].upper()
  if last_char == 'K':
    multiplier = 1024.0
  elif last_char == 'M':
    multiplier = 1048576.0
  elif last_char == 'G':
    multiplier = 1073741824.0
  else:
    multiplier = 1
  return int(float(re.match('[0-9]*\.?[0-9]*', file_size).group(0)) * multiplier)   # Return byte size as integer

def get_files(dir_name):
  """
  This function will recursively generate a list of files from the directory that was passed in.
  It returns this list as an array.
  The walk module from the os library is utilized to retreive the file names.
  """
  filelist = []
  for root, dirs, files in os.walk(dir_name):
    for subdir in dirs:
      filelist.append(os.path.join(root, subdir))
    for file in files:
      filelist.append(os.path.join(root,file))
  return filelist

args = parse_arguments()
dir_name = args.parse_args().dir_name
email = args.parse_args().email
file_size = args.parse_args().file_size
DRYRUN = args.parse_args().dry_run
check_arguments(dir_name, email, file_size)
file_size = convert_size(file_size)
filelist = get_files(dir_name)
