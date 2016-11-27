# Author:					MS. Kingon
# Main development period:	2016-05-16
# Description:  			crawls the file system: 
#							\\zef\apache$\htdocs\wiki\dsaehist\data\pages\entries\
#							- from each .txt file, pulls the ID
#							- It then uses that ID to count the No of occurances in the FUll DB xml file
#							- it then updates the Wiki file with the Current Count of these quotations.
# ========================================================================== #
# IMPORTS
# ========================================================================== #
import os;			# for filesystem crawling
import subprocess; 	# to run cmd-line commands from within python.
import re;			# for efficent string search
import codecs;		# for File IO
import datetime																 # for logging 
import time	
import sys;

# ========================================================================== #
# GLOBAL VARIABLES
# ========================================================================== #
# Path's to specific folder/files.
path_to_quote_DB = "//zef/databases$/Intake/system/build/intake/Intake_compiled.xml"
path_to_entries = "//zef/apache$/htdocs/wiki/dsaehist/data/pages/entries/"; # dummy place holder till needed
path_to_logfile = "//zef/databases$/Intake/system/logs/wiki_count.log";			 	 # path to log file
path_to_test_bed = "M:/quotation counts/Test_bed/"
date = datetime.date.today().isoformat()

# ========================================================================== #
# FUNCTIONS
# ========================================================================== #
# Description:	Runs through a compiled xml file and extracts all instances of DSAEHIST1ID
# Input:		file to check
# Output:		string containing a list of all ID's found in the file.		
# Side effects:	Writes relevant information to a log file 
def run_quote_ID_extraction(filename):
	# takes a file and runs Xpath cmand on that file to extract meaningfull 
	# data for later use.
	try:
		id_list = subprocess.check_output(['xmllint', '--xpath', '//@DSAEHIST1ID', filename]);
	except exception:
		logfile.write("Error: failed to read \r\n{0}".format(filename) )
		logfile.write("Forcing premature cancelation of script.\r\n")
		logfile.write(r'='*80 + "\r\n")
		logfile.close();
		sys.exit()
	return id_list

# Description:	Crawls a provided directory structure for all quote's only edits .txt files that make up the dsaehist web database
# Input:		path to root of directory, alphabetical folders to crawl through, a string of all ID's pulled from the compiled file
# Output:		N/A
# Side effects:	Edits the individual .txt files that make up the dsaehist website database by editing the Workflow segment with the updated quot counts.
def crawl_quotes(path_to_folder, alp_folder, quote_IDs):
	# crawls through a folder, appending all .txt files to a list of routes
	path_to_source = path_to_folder + alp_folder;
	# path_to_bak_dest = path_to_backups + alp_folder;
	
	for quote in os.listdir(path_to_source):
		if quote.endswith(".txt"):
			# TO DO:
			# - Open the file, search it for its ID
			read_cur_file  = codecs.open(path_to_source + quote, "r").read();
			# write_backup_orig = codecs.open(path_to_bak_dest + quote, 'w')
			
			ID = re.findall('\| *(e\d+) *\|', read_cur_file);
			
			# - Take that ID and search for No. of occurances in the Extracted 
			#   ID file.
			quotes = re.findall(ID[0], quote_IDs)
			
			# - backup Orig file
			# write_backup_orig.write(read_cur_file);
			# write_backup_orig.close();
			
			# - Edit the file with the new Quote Count
			updated_seg = '===== Workflow =====\nThere has been a Total of: {0} Quotes collected\n===== Quot notes ====='.format(len(quotes))
			updated_quotes = re.sub('===== Workflow =====.*===== Quot notes =====', updated_seg, read_cur_file, 0, re.DOTALL);
			
			# - write back to the file + backup
			overwrite_cur_file = codecs.open(path_to_source + quote, "w");
			overwrite_cur_file.write(updated_quotes);
			overwrite_cur_file.close();

# ========================================================================== #
# PROGRAM START HERE
# ========================================================================== #
if __name__ == "__main__":
	# ToDo:
	# - pull all alphabet folder names A -- Z
	quote_folders = ['A/','B/','C/','D/','E/','F/','G/','H/','I/','J/',
					 'K/','L/','M/','N/','O/','P/','Q/','R/','S/','T/',
					 'U/','V/','W/','X/','Y/','Z/'];
	
	# run the cmd-line ID extraction to "quote_ID_count.log"
	quote_ID_string = run_quote_ID_extraction(path_to_quote_DB);
	logfile = codecs.open(path_to_logfile, "a", 'utf-8');
	
	# write logfile header
	logfile.write(r'='*80 + "\r\n")
	logfile.write("Started \"wiki counter\" application, %s\r\n" % date)
	
	# - crawl through each folder, for each .txt file:	
	for folder in quote_folders:
		crawl_quotes(path_to_entries, folder, quote_ID_string)

	logfile.write("Succesfully completed \"wiki counter\", %s\r\n" % date)
	logfile.write(r'='*80 + "\r\n")
	logfile.close();