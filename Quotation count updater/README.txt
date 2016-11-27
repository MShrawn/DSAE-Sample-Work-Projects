Documentation for Quotation counts:
===========================================
	Problem:
	========
	This project simply automates the updating of Quotation counts in the wiki.
	each entry in:
	
		'\\aardvark\apache$\htdocs\wiki\dsaehist\data\pages\entries\'
	
	Has a possibly increasing number of associated quotes in the big XML file:
	
		'\\aardvark\dfs\dav\system\build\intake\Intake_compiled.xml'
		
	
	Overwiew:
	=========
	- Go through each alphabetical folder in target directory,
	- take each entry.
	- extract the ID
	- use this ID and count the number of times it occurs in the big XML file len(regex.findall())
	- backups of entrys are done "Manually"
	- edit entry to reflect this new count.
	
	- Automation is done using windows task scheduler. set to run: every sunday at 1:00 AM
	