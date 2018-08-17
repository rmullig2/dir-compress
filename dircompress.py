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
  parser.add_argument('-s', action='store', dest='file_size', help='Specifies the minimum file size to compress', required=True)
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
  if re.match("[0-9]*[0-9MmGgKk]?$", file_size) == None:
    print "Invalid file size"
    sys.exit(2)
  return

args = parse_arguments()
#print args.parse_args()
dir_name = args.parse_args().dir_name
email = args.parse_args().email
file_size = args.parse_args().file_size
DRYRUN = args.parse_args().dry_run
check_arguments(dir_name, email, file_size)
# print dir_name + " | " + email + " | " + file_size + " | "
# print DRYRUN