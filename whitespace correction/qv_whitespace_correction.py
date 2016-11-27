# Author:		MS. Kingon
# Date:			06/06/2016
# Description:	Script to parse a Large XML file and find instances 
#				where hard spaces have been removed incorrectly by 
#				the text editor/cheap work-arounds used.
# Loc (code):	Q:\QV\system\build\post-build_cleanup
# loc (logs):	Q:\QV\system\logs\qv_space_cleanup.log
# loc (backups):Q:\QV\system\build\post-build_cleanup\backups\>>Appropriate sub directory<<\xxx_writeable.txt
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
import datetime

# ========================================= #
# Global Variables							# 
# ========================================= #
path_to_full_quots_out 	= r"..\Quots_compiled.xml"
path_to_stylesheet		= r"Quots-Simpleified2.xslt"
path_to_full_quots 		= r"..\Quots_compiled.xml"
path_to_writeables_test = r"..\..\..\data\quots"
path_to_logfile			= r"..\..\logs\qv_space_cleanup.log"
error_quot_cnt			= 0;
edited_quots			= [];

# ========================================= #
# Functions									# 
# ========================================= #
def correct_temp_fix_start(targets, corrected, amara_path):
	# fixes temporary solutions made by staff.
	global error_quot_cnt 
	firstflag = True
	
	# build path to writeable version of the quot
	rel_path_to_write	= "\\" + amara_path[:4] + "Writable_" + amara_path[4:]
	file 				= path_to_writeables_test + rel_path_to_write
	
	for x in range(0,len(targets),1):
		error_quot_cnt += 1
		# build replacment text
		if targets[x][3] == " ":
			# Handle:
			# '<i> ' || '<b> '
			replacment = u'\u00a0' + targets[x][:3] + targets[x][4:]
		elif targets[x][11]== " ":
			# handle:
			# '<catchword> '
			replacment = u'\u00a0' + targets[x][:11] + targets[x][12:]

		else:
			# handle:
			# '<edInsertion> '
			replacment = u'\u00a0' + targets[x][:13] + targets[x][14:]
		
		# correct it in the big file, then in individual writeable file
		corrected = re.sub(targets[x], replacment, corrected)
		firstflag = fix_writeable(file, targets[x], replacment, firstflag, rel_path_to_write)
	
	return corrected;
		
def correct_temp_fix_end(targets, corrected, amara_path):
	# fixes temporary solutions made by staff.
	global error_quot_cnt 
	firstflag = True
	
	# build path to writeable version of the quot
	rel_path_to_write	= "\\" + amara_path[:4] + "Writable_" + amara_path[4:]
	file 				= path_to_writeables_test + rel_path_to_write
	
	for x in range(0,len(targets),1):
		error_quot_cnt += 1
		
		# build replacment text
		if targets[x][-5] == " ":
			# Handle:
			# 'xxxx </i>' || 'xxxx </b>'
			replacment = targets[x][:-5]  + targets[x][-4:]  + u'\u00a0'
		elif targets[x][-13] == " ":
			# handle:
			# 'xxxx </catchword>'
			replacment = targets[x][:-13] + targets[x][-12:] + u'\u00a0'
		else:
			# handle:
			# 'xxxx </edInsertion>'
			replacment = targets[x][:-15] + targets[x][-14:] + u'\u00a0'
			
		# correct it in the big file, then in individual writeable file
		corrected = re.sub(targets[x], replacment, corrected)
		firstflag = fix_writeable(file, targets[x], replacment, firstflag, rel_path_to_write)
		print rel_path_to_write;
	return corrected;
	
def correct_missing_space(targets, corrected, amara_path):
	# fixes instances where there is no visible space between tags.
	global error_quot_cnt
	spaces = ['\t','\n','\x0b','\x0c','\r']
	firstflag = True
	
	# build path to writeable version of the quot
	rel_path_to_write	= "\\" + amara_path[:4] + "Writable_" + amara_path[4:]
	file 				= path_to_writeables_test + rel_path_to_write
	
	for x in range(0,len(targets),1):
		error_quot_cnt += 1
		
		# build replacement text
		# handle the case where it is a catchword tag as opposed to a i/b tag
		tar_comp = targets[x].split(' ')
		
		# create clean version of target string (to counter changes in visual
		# formating accross xml docs)
		# in the same way create the replacment string to be substituted over offending 
		# text (matters not that we check for correct replacment as if there was another 
		# element it substituted the replacment over, it should have been replaced anyway.)
		if (tar_comp[0][-1:] in spaces):
			target_neatened = tar_comp[0][:-1] 	+ '\s*' + tar_comp[len(tar_comp)-1]			
			replacment 		= tar_comp[0][:-1] + u'\u00a0' + tar_comp[len(tar_comp)-1]
		else:
			target_neatened = tar_comp[0] 		+ '\s*' + tar_comp[len(tar_comp)-1]
			replacment	 	= tar_comp[0] + u'\u00a0' + tar_comp[len(tar_comp)-1]
			
		# fix issue in large quots compiled file
		# then fix in individual file
		corrected = re.sub(targets[x], replacment, corrected)
		firstflag = fix_writeable(file, target_neatened, replacment, firstflag, rel_path_to_write)

	return corrected;
	
def run_xml_stylesheet(xml_file, stylesheet):
	# input: a xml file and stylesheet and runs xsltproc.
	# returns: a string contaning the transformed xml
	return subprocess.check_output(['xsltproc.exe', stylesheet, xml_file])
	
def fix_writeable(writeable_file, target, replacment, firstflag, rel_path_to_write):
	# fix's single writeable version of file.
	write_quot_file 	= codecs.open(writeable_file, 'r', 'utf-8');		# open main file
	writeable_file_text = write_quot_file.read();							# read data into memory
	write_quot_file.close();
	global edited_quots;
	
	if firstflag:		# backup orig writeable file (only once per file.)
		if not(writeable_file in edited_quots):			
			edited_quots.append(writeable_file);
			
		firstflag = False;
		path_to_bak			= "backups" + rel_path_to_write + "_" + str(datetime.date.today())		# make backup unique
		write_quot_file_bak = codecs.open(path_to_bak, 'w', 'utf-8');		# open main file
		write_quot_file_bak.write(writeable_file_text)
		write_quot_file_bak.close()
	
	write_quot_file		= codecs.open(writeable_file, 'w', 'utf-8');		# open main file
	fixed_text = re.sub(target, replacment, writeable_file_text)			# correct file
	write_quot_file.write(fixed_text);										# write corected version back
	write_quot_file.close();
	
	return firstflag
			
# xml_file:			working build file
# xml_stylesheet:	style sheet for simplifiying build file
# issue_type:		which problem case we are dealing with
#					'0' - correct_missing_space
#					'1' - correct_temp_fix_start
#					'2' - correct_temp_fix_end
# re_issue:			regular exp detaling the problem case
# xml_out_file:		output xml file
# logfile:			open logfile to write out system messages
# log_msg:			Message we would like to output.
# return:			>>Nothing<<			
def find_issues(xml_file, xml_stylesheet, issue_type, re_issue, xml_out_file, logfile, log_msg):
	# go through each quot and search for offending xml data.
	# once found use the corresponding ID to edit the correct quote in the main file.
	main_quot_file 			= codecs.open(xml_file, 'r', 'utf-8');						# open main file
	corrected 				= main_quot_file.read();									# read in main file
	main_quot_file.close();																# close main file as done reading
	
	simplified 				= run_xml_stylesheet(xml_file, xml_stylesheet)				# simplifiy quots for first pass
	comp_quots_amara_root 	= amara.parse(simplified);									# read in via amara
	amara_quots 	   		= comp_quots_amara_root.xml_children[0];					# position ourselves for looping.

	for i in range(1,len(amara_quots.xml_children),2):		
		# extract the ID and then the quoteText
	 	amara_quot_ID   = amara_quots.xml_children[i].xml_children[1].xml_children[0].xml_encode()
		amara_quot      = amara_quots.xml_children[i].xml_children[3].xml_encode()
		amara_quot_path = amara_quots.xml_children[i].xml_children[5].xml_children[0].xml_encode()

		# correct missing space between tags
		space_issue = re.findall(re_issue, amara_quot);	
		if(len(space_issue) != 0):
			if issue_type == '0':
				corrected = correct_missing_space(space_issue, corrected, amara_quot_path);
			elif issue_type == '1':
				corrected = correct_temp_fix_start(space_issue, corrected, amara_quot_path)
			else:
				corrected = correct_temp_fix_end(space_issue, corrected, amara_quot_path)
				
	main_quot_file_out = codecs.open(xml_out_file, 'w', 'utf-8'); # open main file for writing
	main_quot_file_out.write(corrected);
	logfile.write(log_msg.format(error_quot_cnt))
	
	main_quot_file_out.close()

# ========================================= #
# Entry Point								# 
# ========================================= #
if __name__ == "__main__":
	# Two main computation stages:
	# Shorten large_compiled file
	# Main computation stage one: 
	#  - Run through the shortened xml data, fix all missing space issues. (fix both large and individual files)
	# Shorten now corrected large_compiled data (currently stored in program mem)
	# Main computation stage two: 
	#  - Run through the shortened xml data, fix all temp solution issues. (fix both large and individual files)
	# write up log file (list edited files if no issue presented itself)
	# ====================================================================================== #
	# Open logfile:
	logfile = codecs.open(path_to_logfile,'a','utf-8');										 # open main file
	logfile.write(r'='*80 + "\r\n")															 # write logfile header
	logfile.write('Log entries for the date off: ' + str(datetime.date.today()) + '\r\n')
	# ====================================================================================== #
	# pass 1, read the file in (Amara).
	start = timeit.default_timer();															 # timmer to test efficency
		
	# case 00 there are missing spaces between closing and opening tags within the quotText element.
	log_msg 	= 'Count of quots that had the "missing space between tags" problem: {0}\r\n';
	regex		= '</[i|b|catchword]+>\s*<[i|b|catchword]+>'
	issue_type	= '0'
	find_issues(path_to_full_quots, path_to_stylesheet, issue_type, regex, path_to_full_quots_out, logfile, log_msg)
	
	# case 01 Capturers have manually 'Fixed' the above problem, by adding a space on the inside of 
	# the tag at the start. Normalizes to standard solution above.
	log_msg 	= 'Count of quots that had the "temp fix at start" problem: {0}\r\n';
	regex		= '<[(i|b|catchword|smallcaps|edInsertion)]+> '
	issue_type	= '1'
	find_issues(path_to_full_quots, path_to_stylesheet, issue_type, regex, path_to_full_quots_out, logfile, log_msg)
	
	# case 02 Capturers have manually 'Fixed' the above problem, by adding a space on the inside of 
	# the tag at the end. Normalizes to standard solution above.
	log_msg 	= 'Count of quots that had the "temp fix at end" problem: {0}\r\n';
	regex		= '\w+ +</[(i|b|catchword|smallcaps|edInsertion)]+>'
	issue_type	= '2'
	find_issues(path_to_full_quots, path_to_stylesheet, issue_type, regex, path_to_full_quots_out, logfile, log_msg)
	
	logfile.write('Below is a list of all the edited files: \r\n')
	logfile.write('(Backups for the below can be found in: \'Q:\\QV\\system\\build\\post-build_cleanup\\backups\')\r\n')
	for x in edited_quots:
		logfile.write('\t\t' + x + '\r\n');
	
	logfile.write('\r\n' + r'='*80 + "\r\n")
	logfile.close();
	