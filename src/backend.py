"""
This file handles the "behind-the-scenes" data analysis whose output is
used by the data visualizer (frontend.py).

In this case, it simply parses the .csv file into a set of dictionaries;
however, more complex data analysis would necessitate adding to this
file.
"""

# import some basic python utilities
from typing import Iterable
from csv import reader as csvReader

class DataSet:
	"""
	stores a collection of data as a list of dictionaries
	"""

	def __init__(self):
		"""
		create empty data set
		"""

		self._dataList = []
		self._schema = {}

	def __iter__(self):
		"""
		allows iterating through dataSet using a for loop
		"""

		for d in self._dataList:
			yield d

	def __len__(self):

		return len(self._dataList)

	def getSchema(self, csvFilePath):
		"""
		returns the cached schema of a csv file if it was added to the
		data set, which maps the 0-indexed column of a field in the csv
		file to its name specified in the first row of the file
		"""

		return self._schema[csvFilePath]

	def addData(self, data:dict):
		"""
		add a piece of data to the data set
		"""

		self._dataList.append(data)

	def addDataSet(self, dataSet:Iterable[dict]):
		"""
		add multiple pieces of data to the data set
		"""

		self._dataList.extend(dataSet)

	def addCsv(self, csvFilePath:str):
		"""
		add the schema of a csv file and its data to the data set
		"""

		with open(csvFilePath) as dataFile:

			rows = iter(
				splitRow
				for splitRow in csvReader(dataFile, dialect='excel')
				)

			self._schema[csvFilePath] = {
				attributeName:index for index, attributeName
				in enumerate(next(rows))
				}

			self.addDataSet(
				iter(
					{attrName : splitRow[index]
					 for attrName, index in self._schema[csvFilePath].items()}
					for splitRow in rows
					)
				)