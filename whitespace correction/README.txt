Documentation for qv_whitespace_correction:
===========================================
	Problem:
	========
	The problem this project tries to remidy is rather broad, ultimatly it serves to resolve all 
	whitespace issues that may present themselves in the individual writeable and full build QV 
	xml files.  These problems would arise due to erronous editing of the writable files when they 
	are updated/edited.

	For now the Two problems are as described:
	==========================================
	[Error 01] "Missing space between tags"
	---------------------------------------
		This issue entails the presence of closing and opening tags not separated by a space eg: 
		
				xxxx</i><b>yyyy

		This occurs due to, in editing, a space is correctly used to separate the tags but serna strips 
		this space after the file is saved yeilding the above, causeing the italicised and bolded words 
		to become one.  Less comonly a hard space is not used when it should be, causing the words to be 
		split over two lines when they should be kept together.

	[Error 02] "Temporary User implemented fix"
	-------------------------------------------
		Not an Error per se but still undesirable as it could cause issues down the line.  This occurs when 
		a editor notices the problem as detailed above, but instead of inserting a hardspace, they opt to 
		include the space inside the tag.  As such: 

				xxxx </i>

				   'or'
				   
				<b> yyyy
				
		As can be seen, this comes in two flavours, insertion at begining of the tag and at end.  

				
	Overview:
	=========
	My code can be broken up into 2 stages or passes.
	- Starting pass 1:)
		- Read in QV build file
		- Apply xslt simplifier (strips everything save for the id, quotext and metadata tags)
		- Parse this simplified xml file using amara
		- For-each quottext, check for the "missing space betwenn tags" issue.
			- If found, 
				- Fix in QV build file
				- Backup individual writable file
				- Fix in individual writeable file
	- for Pass 2.)
		- pass Corrected QV build to xslt simplifier
		- Parse this simplified xml file using amara
		- For-each quottext, check for the "Temp user correction" issue. (both cases start and end.)
			- If found, 
				- Fix in QV build file
				- Backup individual writable file
				- Fix in individual writeable file 
				
	In amidst the above is various logfile writes to help users when the system "fixes" files or if 
	it runs into issues.  This log file can be found at:
	
	"Q:\QV\system\logs\qv_space_cleanup.log"
	
	