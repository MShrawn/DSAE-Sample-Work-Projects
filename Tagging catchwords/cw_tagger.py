# Author:		MS. Kingon
# Date:			24/10/2016
# Description:	Script to parse the flat file system db and tag CW in QuotText's without.
# Requirments:	Re
#				amara
# ========================================= #
# Imports									# 
# ========================================= #
import amara;												# import amara xml parsing functionality
from amara import tree;										#
import subprocess; 											# to run cmd-line commands from within python.
from xml.sax._exceptions import SAXParseException; 			# used by amara	
import codecs;
import re;
import time;
from datetime import datetime;
import os;
# ========================================= #
# Global Variables							# 
# ========================================= #
path_to_inputDB  = r"Output\quots";
path_to_outputDB = r"Test bed\quots";
# path_to_outputDB = r"Sample files";
path_to_logfile	 = r"Logs\logfile.log";
path_to_lookup_file = r"Logs\Lookup Table.log";
miss_CW_tag = 0;
Total_CW = 0.0;

# ========================================= #
# Functions									# 
# ========================================= #
# simple function to determin if there is a catchword tag in the provided file
# input: root and file
# output: Boolen 
def containsCWTag(root, file):

	writeable_file = codecs.open(os.path.join(root, file), 'r', 'utf-8');
	cw_tags = re.findall('<catchword>.*?</catchword>', writeable_file.read(), re.DOTALL)
	if (cw_tags != []):
		return True;
	return False;

# this is the function that would get extended with an algorithim that can better find the word that should get tagged.
# input: 	file to check, 
#			Parent Headword to match against, 
#			lookup table to append to.
# Sideeffects: updates lookup table with CW | CWtagged	
def findCW(path, parent_HW, lookup_table):
	writable_file = codecs.open(path, 'r', 'utf-8').read();
	parent_HW = re.sub('\(.*\)', '',  parent_HW);
	
	# for now handle the simple case of word parent word as is apearing in the text.
	# (as an aside, as of the last run of the program nearly 75% of the problem cases was this 'simple' case.)
	quots		= re.findall('<quotText>.*</quotText>', writable_file, re.DOTALL);	
	word_to_tag = re.findall('[(\'"> ](' + parent_HW + ')[,\.<\'" ]', quots[0]);
	
	for word in word_to_tag:
		outtext = word + ' | <catchword>' + word.strip() + '</catchword>' + '\n'#| ' + quots[0].strip('\n');
		# print outtext.encode('utf-8', 'ignore');
		lookup_table.write(outtext.encode('utf-8', 'ignore'));
	
# Input: 		takes a directory and locates all QV-DB wrapper files
# sideeffects: 	creates a lookup table to do a global replacment of untagged words
def findWrapperfiles(dir):
	paths = [];
	global miss_CW_tag;
	global Total_CW;
	lookup_table = codecs.open(path_to_lookup_file, 'w');	
	
	# locate all files, the directories they are in and the root
	for root, dirs, files in os.walk(dir):
	 	for file in files:
			# only access the wrapper files
	 		if(re.search('^[0-9]*\.xml', file)):
				# open the wrapper, then fetch:
				# path to writeable form and the Parent HW
				file_wrapper 		= codecs.open(os.path.join(root, file), 'r', 'utf8').read();
				path_to_writeable 	= re.findall('href=\"(Writable_[0-9]*\.xml)\"', file_wrapper);
				parent_HW			= re.findall('parentHeadword="(.*?)"',file_wrapper);
				
				# bit of safty code to confirm we found a writeable file and parent HW as 
				# missing either would result in undefined behaviour
				if ((path_to_writeable != []) and (parent_HW != [])):
					Total_CW += 1.0;
					
					# determine if the quot has its CW tagged, if not, try find it and tag it.
					if not(containsCWTag(root, path_to_writeable[0])):
						miss_CW_tag += 1;
						findCW(os.path.join(root, path_to_writeable[0]), parent_HW[0], lookup_table);
	lookup_table.close();	
	
# ========================================= #
# Entry point								# 
# ========================================= #
if __name__ == "__main__":
	# stage 1: Identify writeable files without tagged CW
	# stage 2: Setup Logfile to display this information
	# stage 3: Extract ParentHW from wrapper file
	# stage 4: Edit logfile to only print out ParentHW and Accosiated QuotText for Quotes with no existing CW
	# stage 5: Handle simple case's (where CW == parentHW exactly),  Create Lookup table with: <cw> | <replacment>

	st_time = time.time();
	print ('Start Time: ' + str(st_time));
	files = findWrapperfiles(path_to_outputDB);
	end_time = time.time();
	dtime = end_time - st_time;

	msg = "Time to Compute: {0}\nThere where: {1} Problem Files\nThis Comprises: {2}% of all files.".format(dtime, miss_CW_tag, miss_CW_tag/Total_CW);
	print (msg);
	