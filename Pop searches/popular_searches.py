# Author:		MS. Kingon
# Date:			10/10/2016 - 20/10/2016
# Description:	Script to parse web logs and determine the most 
#				commonnly searched word of that website.
# ========================================= #
# Imports									# 
# ========================================= #
import amara																	# import amara xml parsing functionality
from amara import tree															#
import subprocess; 																# to run cmd-line commands from within python.
from xml.sax._exceptions import SAXParseException 								# used by amara	
import codecs
import re
import timeit
from datetime import datetime;
import os

# ========================================= #
# Global Variables							# 
# ========================================= #
path_to_logs_parent 			= r'B:\prototypes\2016_10_Pop_Searches\v0.01_2016_10_19\Popular searchs\Prog Data\www_logs\www_logs';
path_to_output_file				= r'user_searches.log'
path_to_offensive_log			= r"Prog Data\Offensive words.log"
files 							= []											# list to contain all discovered intake files
start_date						= '20160412';
end_date						= '20161007';
time_diff						= (0,1);										# time difference Global variable set to one day and zero hours

# ========================================= #
# Classes									# 
# ========================================= #
class word:
	# A simple class for word search objects, they include a name, a frequancy (bin) and a date last searched
	def __init__(self, word, date_time):
		self.bin = 1;
		self.word = word;
		self.ldt = date_time;
	
	def timeDiff(self, dt, interval):
		# determines if the time difference between 'self', 'dt' is greater than 'interval' 
		# interval is a tuple, containing (days, hours)
		# will return True if it is, False otherwise.
		hr_rep = 3600;
		
		# if the day difference is greater than what is provided we are good to check hour difference
		if ((dt - self.ldt).days > interval[0]):
			return True;
		elif((dt - self.ldt).days == interval[0]):
			if ((dt - self.ldt).seconds >= interval[1]*hr_rep):
				return True;
			else:
				return False;
		else:
			return False;
	
	def dayDiff(self, dt):
		# determines if there has been a days difference between the last search and the provided date+time
		# input: date, time
		# output: boolean
		if ((dt - self.ldt).days > 1) or ((dt - self.ldt).days == 1 and (dt - self.ldt).seconds > 0):
			return True;
		else:
			return False;
			
	def incbin(self, date_time):
		self.bin += 1;
		self.ldt = date_time;
		
# ========================================= #
# Functions									# 
# ========================================= #
# Description:	Takes a word list and word and determines if the word is present.
# Input:		List of word objects
#				Word in question
# Output:		Tuple (a,b) 
#				a: if the word is present (true/false flag)
#				b: if a is set to 1 then b indicates index of the word in the list.	
def listContainsWord(wordList, wrd):
	# handle first pass case
	if wordList == []:
		return (0,0);

	i = 0
	while i < len(wordList):
		if (wordList[i].word == wrd): 
			return (1, i);	
		i += 1;
	return (0, 0);

# Description:	Scan provided directory for all files between 2 dates
# Input:		parent directory for the extracted log data
#  				A tuple containing the start(inclusive) and end(inclusive) date 
#				as (start, end) in the form of a string (yyyymmdd)
# Output:		Returns a list of paths to all files in provided directory 
def scanforfiles(dir, daterange):
	
	individ_files = [];
	
	# walk the directory structure.
	for root, dirs, files in os.walk(dir):
		for file in files:
			gt_start = False;	# reset variables
			ls_end   = False;
			
			# determine if the logged date is greater than the provided start date
			if (daterange[0][-4:-2] == file[-4:-2]):
				if (daterange[0][-2:] <= file[-2:]):
					gt_start = True;
			elif (daterange[0][-4:-2] < file[-4:-2]):
				gt_start = True;
			
			
			# determine if the logged date is less than than the provided end date
			if (daterange[1][-4:-2] == file[-4:-2]):
				if (daterange[1][-2:] >= file[-2:]):
					ls_end = True;
			elif (daterange[1][-4:-2] > file[-4:-2]):
				ls_end = True;
			
			
			# cheack if we are within bounds
			if (gt_start and ls_end):
				individ_files += [os.path.join(root, file)]

	return individ_files;

# Description:	Takes the string representation of date and time and converts it 
#				into a datatime format.
# Input:		date string
#				time string
# Output:		returns a datetime object corresponding to the provided input date/time stamp	
def ConvToDT(date, time):
	months 	= ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
	day		= int(date[:2]);
	
	# special case for months as log data represents them as strings while DT represents them as int's
	month	= months.index(date[3:6])+1;	# +1 as arrays start at 0
	year	= int(date[7:]);
	
	hr	= int(time[:2])
	mn	= int(time[3:5])
	s	= int(time[6:])
	dt = datetime(year, month, day, hr, mn, s)
	return dt;

# Description: 	Parses a given file, counting frequancie's of words searched
#				Will ignore obvious Bot lines and searches for words within 
#				24hrs of one another.
# Input:		file to parse
#				Wordlist to add new searchs/update counts of existing searchs/update
#				File to write out new search lines
# Side effects: Writes out to a file distinct word search's
#				Add's new words/updates counts for existing words in provided wordlist
def	parseLogfile(file, wordlist, out_file):
	access_log = codecs.open(file, 'r', 'utf8');	# read logfile in
	global time_diff;
	# go line by line through the log file
	for line in access_log:
	
		# These search's filter out unwanted line's
		extracted_searchs 	= re.search(r'_escaped_fragment_', line);						# seems that user searchs contain this '_escaped_fragment_' text if they contain a search, so cheack to see if this is present.
		filter_bots			= re.search(r'bot', line);										# see if this is a 'bot' search
		filter_js			= re.search(r'/?_escaped_fragment_=/word/[\d]*/js', line)		# ignore numerical word searches 
		filter_xref			= re.search(r'/?_escaped_fragment_=/search/xref/js', line)		# ignore empty xref searches
		
		if (extracted_searchs != None and filter_bots == None and filter_js == None and filter_xref == None):
		
			# These extractions pull out important information, namely the date, time and item searched
			search_term = re.findall(r'/?_escaped_fragment_=/word/[\d]*/(.*?)/js', line)
			
			
			
			search_date = re.findall(r'\[(.*?):.*\]', line)[0]
			search_time = re.findall(r'\[.*?:(.*) \+0200\]', line)[0]
			cur_dt = ConvToDT(search_date, search_time)
			
			# safty cheack that we succesfully extracted the word
			if (search_term != []):
				# determine if the word is already present
				tmp = listContainsWord(wordlist, search_term[0])
				if tmp[0] == 1:
					# determine if it has been more than 24 hrs since the last search of this word
					if (wordlist[tmp[1]].timeDiff(cur_dt, time_diff)):
						wordlist[tmp[1]].incbin(cur_dt);
						out_file.write(line);
				else:
					# new word has been searched safe to add it to searches list and out_file
					wordlist.append(word(search_term[0], cur_dt))
					out_file.write(line);
	
# Description:	Will parse a file containing deffined Offensive words and add them to an internal list for later computation
# Input:		file path to offensive word list
# Output:		List containing the offensive words
# Side effects: N/A
def importOffensiveList(file):
	off_file = codecs.open(file, 'r', 'utf8');
	off_list = [];
	
	# go line by line, if it is a Commented line, ignore it, if it is the EOF 
	# line, break, otherwise add word to offensive list.
	for line in off_file:
		if (re.search('^\s*#',line)):		# ignore commented lines
			continue;
		elif (re.search('EOF', line)):		# If last line, break
			break;
		else:								# add this word to the list
			off_wrd = line.strip();
			off_list.append(off_wrd);
	return off_list;
		
# Description:	takes a word and determins if it is offensive (by comparing it to known offensive words)
# Input:		word to cheack along with a list of offensive words
# Output:		boolean value indicating if it is not offensive (True) or Offensive (False)
# Side effects: N/A
def nonOffensive(word, off_list):
	for off_wrd in off_list:
		# might be prudent to exchange this part with a more sophisticated 
		# simmilar word algorithim once one is in the works.  
		# may need to create a escape script to escape any special characters that might apear in words (') as an example
		if re.search(off_wrd.lower(), word.lower()):
			return False;
	return True;

# Description:	Takes a word list and finds the most frequantly searched Word 
#				will ignore offensive word searches.
# Input:		The list of found searches with their frequancies
#				File to write data out to
# Side effects:	Data is written out to provided outfile	
def interpretWordList(wordlist, outfile, offensiveList):		
	# interprets data found in the word list (namely finding most frequant search)
	curr_hi = ('', 0);
	distinct_searches = 0;
	
	# go through each word in our output list, determine which has the highest search count, 
	# if its not offensive, return it, otherwise choose the next most searched word.
	for item in wordlist:
		distinct_searches += item.bin;
		if item.bin > curr_hi[1]:
			# if it is offensive, dont bother adding it, go on to the next word.
			if(nonOffensive(item.word, offensiveList)):
				curr_hi = (item.word, item.bin);
		
	# write out to output file
	outfile.write('-'*80+'\n');
	outfile.write('There have been ({0}) distinct searchs\n'.format(distinct_searches));
	curr_hi = (re.match('(\w+)',curr_hi[0]).group(1), curr_hi[1]);
	outfile.write('Most frequanlty searched word: {0} \nSearched: {1} times.'.format(curr_hi[0], curr_hi[1]))
	
# ========================================= #
# Entry Point								# 
# ========================================= #
if __name__ == "__main__":
	# steps:
	# walk the target directory and create list of all data logs
	# we know The logs are created with the name of the log being the date.  
	# We can use this to ensure we only grab the past weeks logs (or any other period of our choosing).
	# Now that we have the desired logs we can open them and parse them
	# going line by line we use regex to pick out lines with '_escaped_fragment_'
	# we then filter out the bots by also looking for 'bot'
	# whats left will be the lines of user searches
	# for now write these lines to a new coalessed file
	
	files = scanforfiles(path_to_logs_parent, (start_date, end_date))	# find all log files between the desired dates
	out_file = codecs.open(path_to_output_file, 'w', 'utf8');
	
	wordlist = []
	for file in files:
		parseLogfile(file, wordlist, out_file)
		
	off_list = importOffensiveList(path_to_offensive_log);
	interpretWordList(wordlist, out_file, off_list);
	
	out_file.close();