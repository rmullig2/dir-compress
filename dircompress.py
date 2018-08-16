#!/usr/bin/python

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-d', action='store', dest='dir_name', help='Specifies the directory for compression')
parser.add_argument('-e', action='store', dest='email', help='Specifies the email address')
parser.add_argument('-s', action='store', dest='file_size', help='Specifies the minimum file size to compress')
#parser.add_argument('--dry-run', action='store_true', default=False,
#                    dest='dry_run',
#                    help='Add this switch to show saved space without compressing')

print parser.parse_args()