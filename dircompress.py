#!/usr/bin/python
import os
import argparse
import sys
import re

def parse_arguments():
  parser = argparse.ArgumentParser(version="Version 1.0")
  parser.add_argument('-d', action='store', dest='dir_name', help='Specifies the directory for compression')
  parser.add_argument('-e', action='store', dest='email', help='Specifies the email address')
  parser.add_argument('-s', action='store', dest='file_size', help='Specifies the minimum file size to compress')
  parser.add_argument('--dry-run', action='store_true', default=False, dest='dry_run',
                    help='Add this switch to show saved space without compressing')
  return parser

def check_arguments(dir_name, email, file_size):
  if not os.path.isdir(dir_name):
    print "Invalid path name: " + dir_name
    sys.exit(2)
  if re.match("[^@]+@[^@]+\.[^@]+", email) == None:
    print 'Invalid email address: ' + email
    sys.exit(2)
  else:
    print "Good"
  return True

args = parse_arguments()
#print args.parse_args()
dir_name = args.parse_args().dir_name
email = args.parse_args().email
file_size = args.parse_args().file_size
DRYRUN = args.parse_args().dry_run
check_arguments(dir_name, email, file_size)
# print dir_name + " | " + email + " | " + file_size + " | "
# print DRYRUN