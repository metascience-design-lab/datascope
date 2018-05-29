"""
Boolean filtering functions the user can define for their data set
which are incorporated into the web app.
"""

def nativeEnglish(participant:dict) -> bool:
	return participant['nativeEnglish'] == '1'

def analyticMajor(participant:dict) -> bool:
	return participant['analyticMajor'] == 'yes'