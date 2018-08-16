# dir-compress
This program is designed to compress each file in a given directory and email a report to a given address.  

It takes these required inputs:  
  -d directory_name  
  -e email_address  
  -s minimum file size  
 
It will only compress files larger than the given file size. The directory name given must be a valid directory and the email address given must be in a valid email format.  

The program also takes in these option inputs:  
  -v, --version prints the version of the script  
  -h prints out the help  
  --dry-run creates the report and email it without doing the compression  
  
### Copyright 2018 by Ray Mulligan ###
