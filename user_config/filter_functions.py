"""
Boolean filtering functions the user can define for their data set
which are incorporated into the web app.
"""

from random import getrandbits

def nativeEnglish(participant:dict) -> bool:
	return participant['nativeEnglish'] == '1'

def analyticMajor(participant:dict) -> bool:
	return participant['analyticMajor'] == 'yes'

def male(participant:dict) -> bool:
	return bool(getrandbits(1))

def female(participant:dict) -> bool:
	return bool(getrandbits(1))