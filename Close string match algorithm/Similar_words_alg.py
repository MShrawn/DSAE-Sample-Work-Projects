# Author:		MS. Kingon
# Date:			27/10/2016
# Description:	Algorithim to determine if 2 words are similar providing a confidence level.
# Requirments:	Python 2.7+
#				Re
#				codecs
# ========================================= #
# Imports									# 
# ========================================= #
import codecs;
import re;

# ========================================= #
# Global Variables							# 
# ========================================= #
path_to_testing_file = r'Data\tester_file.txt';
path_to_results = r'Data\results.log';
correct_cnt = 0.0;
# ========================================= #
# Functions									# 
# ========================================= #
def simmilar(wrd1, wrd2):
	Verdict = 'False';		# set default verdict to False
	confidence = -1;		# set default confidence Level to -1
	
	lev_dst_mat = levenshteimDistanceMatrix(wrd1, wrd2);
	confidence = calcConfidence(wrd1, wrd2, lev_dst_mat);
	
	if confidence > .75:
		Verdict = 'True';
		
	return (Verdict, confidence)
	
def prettyPrintLevenshteimMatrix(matrix):
	# just a pretty printer for a numerical matrix
	for i in matrix:
		for j in i:
			print("{:^3}".format(j)),
		print('\n')
		
def calcConfidence(src, tar, lev_mat):
	# given a source and target word along with the built Levenshteim Matrix, determine a confidence level that these two words are the same
	# input:	source, target, Levenshteim distance matrix
	# output:	Floating point value between 0-1 indicating confidence that these words are the same.
	
	if(len(src) < lev_mat[-1][-1]):
		return -1.0;
		
	inv_conf = float(lev_mat[-1][-1])/len(src);
	conf = 1-inv_conf;
	
	return conf
	
def levenshteimDistanceMatrix(src, tar):
	# computes the levenshteim distance Matrix between two strings.
	# create a (m+1)x(n+1) Matrix where:
	# 	m=src length
	#	n=tar length	
	# Input: a source word and a target word
	# Output: Levenshteim Distance Matrix for the 2 words
	
	d = []
	n = len(src);
	m = len(tar);
	for j in range(n+1):
		d.append([]);
		for i in range(m+1):
			d[j].append(0);
			
	# set source prefix's
	for i in range(1, m+1):
		d[0][i] = i;
		
	# set target prefix's
	for j in range(1, n+1):
		d[j][0] = j;
			
	for j in range(1, n+1):
		for i in range(1, m+1):
			# print src[i]
			if src[j-1] == tar[i-1]:
				subCost = 0;
			else:
				subCost = 1;
			d[j][i] = min([d[j][i-1]+1, d[j-1][i]+1, d[j-1][i-1] + subCost]) 
		
	prettyPrintLevenshteimMatrix(d);		

	return d
	
# Description: takes a file with testing data and reads it into a triplit array
# Input: file to fetch data from
# Output: an Nx3 Array where N is the number of test items.
def readInTester(testing_file):
	data = [];
	testing_file_lines = codecs.open(testing_file, 'r');
	
	for line in testing_file_lines:
		# ignore comment or emptty lines where comments are distinguished as #
		if re.search('^\s*#', line) or re.search('^\s*$', line):
			continue;
		else:
			src,tar,ver = re.findall('^(.*?)\|(.*?)\|(.*?)$', line)[0];
			data.append([src.strip(), tar.strip(), ver.strip()]);
	
	testing_file_lines.close();
	return data; 
	
# Description: takes two words and the correct verdict, applyies simmilar word alg to the words, and reports if it got the match correct along woth the confidence interval.
# Input:  source word, target word, human evaluation of their simmilarity.
# Output: tuple containing, correctness of guess, and the confidense of the match
def test(src, tar, correct_verdict):
	verdict_tuple = simmilar(src.lower(), tar.lower());
	correctness = 0;
	
	if verdict_tuple[0] == correct_verdict:
		correctness = 1;
		
	return (correctness, verdict_tuple[1]);
	
def tester(testing_data, path_to_results):
	# takes as input a File containing lines as:


	# it then creates a report file that tells you the words the Algorithim got wrong and percentage of words it got right
	# possibly also showing words with confidences between 50-75 that are tested correct?
	global correct_cnt;
	total_tests = len(testing_data);
	result_file = codecs.open(path_to_results, 'w');	
	false_pos = [];
	
	for item in testing_data:
		test_conclusion = test(item[0], item[1], item[2]);
		if (test_conclusion[0] == 1):
			correct_cnt += 1.0;
			continue;
		else:
			# provide log data for cases where the prediction failed
			our_predict = 'False';
			if (item[2] == 'False'):
				# keep special track of any false positives
				our_predict = 'True';
				false_pos.append([item[0], item [1], test_conclusion[1]]);
			
			# update log file with incoreect guesses.
			result_file.write('Source:     {0}\nTarget:     {1}\nPredicted:  {2}\nCorrect:    {3}\nConfidence: {4:5.2f}%\n'.format(item[0], item[1], our_predict, item[2], test_conclusion[1]*100));
			result_file.write('='*80 + '\n');
	
	# pretty print any false positives.
	result_file.write('Below is an extracted list of all the false positives along with the supposed confidence.\n');
	if false_pos == []:
		result_file.write('Wonderfull, there are No false Positives.\n' + '='*80 + '\n')
	for bad in false_pos:
		result_file.write('{0:20} | {1:20} | {2:5.2f}%\n'.format(bad[0], bad[1], bad[2]))
	
	result_file.write('In Conclusion; out of {0} test cases we got {1} Correct.\nThis equates to a: {2:5.2f}% success rate\n'.format(total_tests, correct_cnt, correct_cnt/total_tests*100));
	pass;
	
# ========================================= #
# Entry point								# 
# ========================================= #	
if __name__ == "__main__":
	# there are many heuristics that one could use, for an example, changes to 
	# the begining of words should be more concerning than changes at the end.
	
	test_data = readInTester(path_to_testing_file);				# import testing data.
	tester(test_data, path_to_results);