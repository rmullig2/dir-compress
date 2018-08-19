#!/usr/bin/python
try:
  import os, argparse, sys, re, magic, gzip
except ImportError:
  print "One or more modules is unavailable, please make sure these libraries are avaiable: os, argparse, sys, re, magic, gzip"
  sys.exit(1)


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
  display_message("Generating a list of all files in the target directory.")
  filelist = []
  for root, dirs, files in os.walk(dir_name):
    for subdir in dirs:
      filelist.append(os.path.join(root, subdir))
    for file in files:
      filelist.append(os.path.join(root,file))
  return filelist

def create_lists(filelist, file_size):
  """
  This function will create arrays containing:
  files that are smaller than the minimum file size
  files that will not be compressed due to expected small compression ratio
  files to be compressed.
  The pyton magic library is used to determine each file's type
  """
  display_message("Determining which files can be compressed.")
  too_small_files = []
  small_ratio_files = []
  good_files = []
  
  m = magic.open(magic.MAGIC_NONE)    # Set up a variable for the magic library
  m.load()
  
  excluded_files = 'JPG|PNG|GIF|special|BitTorrent|Zip|gzip|MPEG|ISO|img'    # Specify file types that are not to be compressed
  
  for filename in filelist:
    if m.file(filename) == 'directory':       # If it is a directory and not a file then ignore it
      continue
    elif re.search(excluded_files, m.file(filename)) != None:     # Check if file type should be excluded
      small_ratio_files.append(filename)
    elif os.path.getsize(filename) < file_size:
      too_small_files.append(filename)
    else:
      good_files.append(filename)
  
  return [too_small_files, small_ratio_files, good_files]

def zip_files(filelist, dryrun=False):
  """
  This function takes in a list of files to be zipped and attempts to compress them.
  If dry run is indicated then the files will be copied to /tmp, zipped, and deleted after the compressed size is recorded.
  It returns an array of zipped files and the total space saved.
  """
  if dryrun:
    display_message("Dryrun mode selected, files will not be modified.")
  compressed_files = []
  saved_space = 0
  for filename in filelist:
    display_message("Attempting to open " + filename)
    try:
      input_file = open(filename, "r+")             # Must be able to open each file in read-write mode
    except:
      display_message("Cannot compress " + filename)
      continue                                      # Skip file if it is unable to open as read-write
    input_size = os.path.getsize(filename)          # Calculate the file size before compression
    content = input_file.read()                     # Read in the contents of the input file
    zip_name = (filename, "gz")                     
    zip_name = ".".join(zip_name)                   # This line creates a .gz file using the same file name
    output_file = gzip.open(zip_name, 'wb')         # Open the .gz file as read-write block file
    try:
      output_file.write(content)                    # Attempt to compress the contents of the input file
    finally:
      display_message("Successfully compressed " + filename)
      output_size = os.path.getsize(zip_name)       # Calculate the file size of the newly compressed file
      compressed_files.append(filename)                    # Add to list of successfully compressed files
      saved_space += input_size - output_size
    input_file.close()
    output_file.close()
    if dryrun:                                      # For dry runs we keep the file and delete the compressed file
      os.remove(zip_name)                           # For regular runs we keep  the compressed file and delete the file
    else:
      os.remove(filename)
  return [compressed_files, saved_space]

def display_message(message):
  """
  This runction displays status messages to the screen.
  """
  print time.ctime() + " " + message


args = parse_arguments()
dir_name = args.parse_args().dir_name
email = args.parse_args().email
file_size = args.parse_args().file_size
DRYRUN = args.parse_args().dry_run
check_arguments(dir_name, email, file_size)
file_size = convert_size(file_size)
filelist = get_files(dir_name)
[too_small_files, small_ratio_files, good_files] = create_lists(filelist, file_size)
[compressed_files, saved_space] = zip_files(good_files, DRYRUN)
