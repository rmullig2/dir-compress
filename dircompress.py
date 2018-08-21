#!/usr/bin/python
def display_message(message):
  """
  This runction displays status messages to the screen.
  """
  program_log = open("/tmp/dircompress.txt", 'a')
  program_log.write(time.ctime() + " " + message + "\n")
  program_log.close

try:
  import os, argparse, sys, re, magic, gzip, time, smtplib, socket, signal
  from email.mime.multipart import MIMEMultipart
  from email.mime.text import MIMEText
except ImportError:
  display_message("One or more modules is unavailable, please make sure these libraries are avaiable: os, argparse, sys, re, magic, gzip, time, smtplib, email, socket, signal")
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
    display_message("Invalid path name: " + dir_name)
    sys.exit(2)
  if re.match("[^@]+@[^@]+\.[^@]+", email) == None:
    display_message('Invalid email address: ' + email)
    sys.exit(2)
  if re.match("[0-9]+\.?[0-9MmGgKk]*$", file_size) == None:     # This allows floating point values with K, M, G suffix
    display_message("Invalid file size, must be integer or floating point value followed by optional suffix (K, M, G)")
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
      time.sleep(5)
    input_file.close()
    output_file.close()
    if dryrun:                                      # For dry runs we keep the file and delete the compressed file
      os.remove(zip_name)                           # For regular runs we keep  the compressed file and delete the file
    else:
      os.remove(filename)
  return [compressed_files, saved_space]

def create_report(compressed_files, saved_space, small_ratio_files, dir_name):
  """
  This function will generate the report to be emailed.
  The report will display a list of files that were compressed, files that were skipped due to small compression ration, and the total amount of saved space.
  """
  kilo = 1024.0
  mega = 1048576.0
  giga = 1073741824.0
  report_name = "/tmp/report.txt"
  report_file = open(report_name, "w")
  report_file.write("Results for compression of " + dir_name + " at " + time.ctime() + "\n\n")
  report_file.write("Compressed files\n")
  for filename in compressed_files:         # Loop through and write out list of compressed files
    report_file.write(filename + "\n")
  report_file.write("\n")
  report_file.write("Files skipped because of a small compression ratio\n")
  for filename in small_ratio_files:        # Loop through and write list of file with small compression ratio
    report_file.write(filename + "\n")
  report_file.write("\n")
  if saved_space > giga:                     # These lines will format the space saved
    report_file.write("Space saved: " + '%5.2f' % (saved_space / giga) + "G\n")
  elif saved_space > mega:
    report_file.write("Space saved: " + '%3.1f' % (saved_space / mega) + "M\n")
  elif saved_space > kilo:
    report_file.write("Space saved: " + '%3.2f' % (saved_space / kilo) + "K\n")
  else:
    report_file.write("Space save: " +  str(saved_space) + "\n")
  report_file.close()

def send_report(email):
  """
  This function will create an email and send it to the address specified when calling the file.
  You should modify the username, password, and server settings to match your environment.
  Example settings are hard-coded for demonstration purposes.
  """
  username = "your_username"                           # Change the username, password, and server settings
  password = "your_password"
  mailserver = "mail.optonline.net"
  server = smtplib.SMTP(mailserver, 587)
  hostname = socket.gethostname()
  report = open("/tmp/report.txt", "r")
  message = MIMEMultipart()
  message['From'] = hostname
  message["To"] = email
  message["Date"] = time.strftime("%b %d %Y")
  message["Subject"] = "Directory compression results"
  message.attach(MIMEText(report.read()))
  report.close()
  try:                                                # Print error message if sending failed
    server.starttls()
    server.login(username, password)
    server.sendmail(hostname, email, message.as_string())
  except:
    display_message("Failed when attempting to send the email")
    
def createDaemon():
  """
  This function allows the script to run as a daemon by detaching it from a terminal
  """
  UMASK = 0         # Do not restrict the permissions of files created by script
  WORKDIR = "/"     # This is used to ensure that a volume umount will not be prevented by this script
  MAXFD = 1024      # Default maximum for the number of available file descriptors

  if (hasattr(os, "devnull")):    # This is used to redirect standard I/O
    REDIRECT_TO = os.devnull
  else:
    REDIRECT_TO = "/dev/null"

  try:
    pid = os.fork()
  except OSError, e:
    raise Exception, "%s [%d]" % (e.strerror, e.errno)    # Serious system problem if fork command fails

  if (pid == 0):	# Fork one child process
    os.setsid()
    try:
       pid = os.fork()	# Fork a second child process
    except OSError, e:
       raise Exception, "%s [%d]" % (e.strerror, e.errno)

    if (pid == 0):	# The second child.
      os.chdir(WORKDIR)
      os.umask(UMASK)
    else:
      os._exit(0)	# Exit parent (the first child) of the second child.
  else:
    os._exit(0)	# Exit parent of the first child.
  import resource		# Resource usage information.
  maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
  if (maxfd == resource.RLIM_INFINITY):
    maxfd = MAXFD
  
  for fd in range(0, maxfd):      # Closing all open files
    try:
      os.close(fd)
    except OSError:	# Ignore file descriptors that are not open
      pass

  os.open(REDIRECT_TO, os.O_RDWR)	# standard input (0)
  os.dup2(0, 1)			# standard output (1)
  os.dup2(0, 2)			# standard error (2)

  return(0)

def user_stoppage(sig, frame):
  display_message("Stopping program on user request")
  exit(3)

def main():
  """
  The main function follows these steps after daemon is created:
  1. Parse the arguments passed in with the script execution.
  2. Strip trailing / from path name if specified.
  3. Save the arguments passsed into varialbes.
  4. Verify the validity of the passed arguments.
  5. Convert the minimum file size given into an integer value.
  6. Prepare a list of files from the destination directory.
  7. Determine if the files are below the specified file size or have a compression ratio too low to process.
  8. Compress the suitable files in the given directory.
  9. Create the report containing the compressed file, files with a low compression ratio, and tht total space saved.
  10. Email the report to the passed email address.
  """
  createDaemon()                                  # Allow program to run as a daemon
  signal.signal(signal.SIGTERM, user_stoppage)    # Handles the sigterm signal sent
  display_message("")
  display_message("Starting directory compression")
  display_message("-------------------------------")
  args = parse_arguments()                        # Step 1
  dir_name = args.parse_args().dir_name
  if dir_name[-1] == '/':                         # Step 2
    dir_name = dir_name[:-1]
  email = args.parse_args().email
  file_size = args.parse_args().file_size         # Step 3
  DRYRUN = args.parse_args().dry_run
  check_arguments(dir_name, email, file_size)     # Step 4
  file_size = convert_size(file_size)             # Step 5
  filelist = get_files(dir_name)                  # Step 6
  [too_small_files, small_ratio_files, good_files] = create_lists(filelist, file_size)        # Step 7
  [compressed_files, saved_space] = zip_files(good_files, DRYRUN)                             # Step 8
  create_report(compressed_files, saved_space, small_ratio_files, dir_name)                   # Step 9
  send_report(email)                              # Step 10
  
if __name__ == '__main__':
  main()
