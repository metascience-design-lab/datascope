"""
This file defines the appearance and functionality of the web app. It
has three main parts:

(1) imports from other modules
(2) defines and parses parameters (CAPITALIZED) that represent
	the 'static' aspects of the web page
(3) defines 'callback functions' which control the interactive aspects
	of the web page
"""

# imports backend and information from ../user_config

if __name__ == '__main__': # if using the local machine as the web server
	import sys
	# from backend import DataSet
	# sys.path.insert(1, '../user_config')
	# from settings import (
	# 	DATA_CSVFILEPATH, DATA_IDFIELD,
	# 	INITIAL_GRAPHTYPE, INITIAL_DATAFIELDS, INITIAL_DATAFILTERS,
	# 	)
	# CSVPATH_CACHE = DATA_CSVFILEPATH
	# DATA_CSVFILEPATH = '../user_config/' + DATA_CSVFILEPATH
	# import filter_functions as FILTER_FUNCTIONS

# else: # if using gunicorn (../Procfile) + Heroku as the web server
	# from src.backend import DataSet
	# from user_config.settings import (
	# 	DATA_CSVFILEPATH, DATA_IDFIELD,
	# 	INITIAL_GRAPHTYPE, INITIAL_DATAFIELDS, INITIAL_DATAFILTERS,
	# 	)
	# CSVPATH_CACHE = DATA_CSVFILEPATH
	# DATA_CSVFILEPATH = 'user_config/' + DATA_CSVFILEPATH
	# import user_config.filter_functions as FILTER_FUNCTIONS

INITIAL_GRAPHTYPE = 'Density Plot'

# imports graphing and page layout libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.figure_factory as ff
import grasia_dash_components as gdc #==0.3.0
from plotly import tools as plotlyTools
from dash.dependencies import Input, Output, State
import json
import numpy as np
import scipy.stats as scipyStats

CSS_URL = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
WEBAPP_TITLE = 'statscope' # title of the webpages' tab

# unique string IDs for UI elements
GRAPH_ID = 'graph'
GRAPHTYPESLIDER_ID = '1'
DATATYPEDROPDOWN_ID = '2'

# names and ordering of available graph types
GRAPHTYPE_CHOICES = [
	'Histogram', # leftmost choice
	'Density Plot',
	'Violin Plot',
	'Table', # central choice
	'Box Plot',
	'Bar Plot',
	'Dot Plot', # rightmost choice
	]

TABLEINFO_CHOICES = [
	"Basic Parametric",
	"Complete Parametric",
	"Basic Nonparametric",
	"Complete Nonparametric",
	]

BOXPLOTINFO_CHOICES = [
	'Mean',
	'Outliers',
	'Notches',
	]

BARDOTPLOTERROR_CHOICES = [
	"± 95% Confidence Interval",
	"± Standard Deviation",
	"± Standard Error",
	]

MIN_BINSIZE = 1
MAX_BINSIZE = 20 # http://www.statisticshowto.com/choose-bin-sizes-statistics/

# DRAWCONTROL_CHOICES = [
# 	'Submit', # bottom choice
# 	'Reset',
# 	'Draw: Freehand', # top choice
# 	]

# FILTER_CHOICES = [
# 	"analyticMajor",
# 	"nativeEnglish",
# 	"All",
# 	]

DENSITY_CURVE_TYPES = [
	'kde',
	'normal',
	]

DRAWMODE_CHOICES = [
	'Freehand',
	'Line',
	'Box',
	]

# # parses the parameters into helper variables
# dataSet = DataSet()
# dataSet.addCsv(DATA_CSVFILEPATH)
# chosenDataFields = [
# 	fieldName
# 	for fieldName in dataSet.getSchema(DATA_CSVFILEPATH)
# 	]
# filterFunctions = {} # maps filter function names' to their function objects
# def _negate(func):
# 	return (lambda x : not func(x))
# for name, func in FILTER_FUNCTIONS.__dict__.items():
# 	if callable(func):
# 		filterFunctions[name] = func
# 		# adds a negated version of every filter
# 		filterFunctions['not_' + name] = _negate(func)

# lays out the basic HTML along with the interactive components
INITIAL_LAYOUT = html.Div(children=[

	html.Div(
		id='session_info',
		style=dict(display='none'),
		children=[
			html.Div(
				id='drawMode_info',
				children=json.dumps({'choices':DRAWMODE_CHOICES, 'i':len(DRAWMODE_CHOICES)-1}),
				),
			# html.Div(
			# 	id='clear_drawing',
			# 	children="false",
			# 	),
			html.Div(
				id="showDataIndicator",
				children="false",
				),
			html.Button(
				id="showDataButton",
				n_clicks=0,
				),
			html.Div(
				id='uploaded_fileAsJson',
				children="{}",
				),
			html.Div(
				id='rangeToZeroIndicator',
				children="true",
				),
			html.A(
				id='rangeToZeroButton',
				n_clicks=0,
				),
			html.Div(
				id='graphTypeIndicator',
				children="Density Plot",
				),
			] + [ html.Button(id="boxPlotToggles-"+e, n_clicks=(1 if e in ('Notches','Mean') else 0)) for e in BOXPLOTINFO_CHOICES ]
		),
	html.Div(
		id='graph_container_container',
		children=[
			html.Div(
				id='drawingInstructions',
				style=dict(
					position="absolute",
					fontSize="18px",
					# whiteSpace="nowrap",
					# overflow="hidden",
					# textOverflow="ellipsis",
					left="calc(50% + 30px)", #TODO adapt to adaptive left padding when implemented
					maxWidth="320px",
					textAlign="center",
					# top="calc(486px/2)",
					top="40%",
					transform="translate(-50%, -50%)",
					),
				children=[
					"",
					],
				),
			html.Div(
				id='graph_container',
				style=dict(
					position='relative',
					zIndex='-1',
					),
				children=[
					# displays the data, controlled by the callback function 'updateGraph'
					# defined below
					dcc.Graph(
						id=GRAPH_ID,
						# config={'staticPlot':True},
						figure=go.Figure(layout=dict(
							paper_bgcolor='rgba(0,0,0,0)',
							plot_bgcolor='rgba(0,0,0,0)',
							)),
						),
					],
				),
			# html.Div(
			# 	id='drawingControl_slider_container',
			# 	children=[
			# 		dcc.Slider(
			# 			id='drawingControl_slider',
			# 			min=0,
			# 			max=len(DRAWCONTROL_CHOICES)-1,
			# 			marks={i: m for i, m in enumerate(DRAWCONTROL_CHOICES)},
			# 			included=False,
			# 			step=None,
			# 			vertical=True,
			# 			value=len(DRAWCONTROL_CHOICES)-1,
			# 			),
			# 		],
			# 	style={
			# 		'position': 'absolute',
			# 		'height': '250',
			# 		'left': '-70',
			# 		'bottom': '100',
			# 		},
			# 	),
			html.Div(
				id='graphTuning_slider_container',
				children=[
					dcc.Slider(
						id='graphTuning_slider',
						),
					],
				style={
					'position': 'absolute',
					'height': '295',
					'right': '-20',
					'bottom': '82',
					},
				),
			],
		style={"position":"relative", "height":"400px"},
		),

	# graph type slider
	html.Div(
		id='graphtypeslider_container',
		children=[
			dcc.Slider(
				id=GRAPHTYPESLIDER_ID,
				min=0,
				max=len(GRAPHTYPE_CHOICES)-1,
				marks={i:m for i,m in enumerate(GRAPHTYPE_CHOICES)},
				included=False,
				step=None,
				value=GRAPHTYPE_CHOICES.index(INITIAL_GRAPHTYPE)
				),
			],
		style=dict(
			paddingLeft="40px",
			),
		),

	# 3 line breaks
	dcc.Markdown('''
&nbsp;
		'''),

	dcc.Markdown('''
&nbsp;
		'''),

	dcc.Markdown('''
&nbsp;
		'''),

	html.Div(
		id="data_uploader_container",
		children=[
			dcc.Upload(
				id='data_uploader',
				children=[html.Div(children=[
					"Drag and drop a csv file or ",
					html.A('select one from your computer'),
					], style={
						"margin":"auto", 'textAlign': 'center',
						'lineHeight': '60px',
						}
					)],
				multiple=False,
				filename="ind-diff-regression.csv",
				contents='data:application/vnd.ms-excel;base64,cGFydGljaXBhbnQsYmV0YUNvbnN0YW50LHBhcnRpY2lwYW50LGJldGFEaXN0YW5jZU5hdHVyYWxzLGJldGFEaXN0YW5jZVJhZGljYWxzLGJldGFTaXplTmF0dXJhbHMsYmV0YVNpemVSYWRpY2FscyxiZXRhRGlzdGFuY2UsYmV0YVNpemUsYmV0YVR5cGUsYmV0YVBlcmZlY3RTcXVhcmUsYmV0YVR5cGV4UFMsYmV0YVNuYXJjTmF0dXJhbHMsYlNuYXJjUmFkaWNhbHMscmt0Q29uY2VwdHVhbCxya3RQcm9jZWR1cmFsLHJrdE92ZXJhbGwscmt0UHJvY2VkdXJhbFN0cmF0ZWd5LG5hdGl2ZUVuZ2xpc2gsYW5hbHl0aWNNYWpvcixubGVFcnJvck5hdHVyYWxzLG5sZUVycm9yUmFkMUQsbmxlRXJyb3JSYWQyRCxubGVFcnJvclJhZFBTLG5sZVJUTmF0dXJhbHNTZWMsbmxlUlRSYWQxRHNlYyxubGVSVFJhZDJEU2VjLG5sZVJUUmFkUFNTZWMKMSw2MjMuNzIsMSwtMTMuOCwtMzEuNiwyMS43LDIwLjMsLTIwLjQxLDE1LjA2LDExNS45NywwLjY0LDQ5LjM0LC02LjU2LC0xNS4wNyw3Ni43LDI1LDUwLjgsNCwxLG5vLDAuMjUsMC43OSwwLjM0LDAuMzMsNi4wMSw3LjU3LDcuMDksNC4yNAoyLDQ5OC4yOCwyLC0xMC40LC03LjksMTUuNyw1LjYsLTExLjM3LDEwLjUzLDY0Ljc5LDMuNzUsLTI2Ljg2LC05LjA3LC0yLjMyLDgyLjIsMzcuMSw1OS43LDIsMSxubywwLjE5LDAuNTksMC42MSwwLjI0LDMuNyw1Ljg4LDcuNDQsNC4xOQozLDQ4MC44MSwzLC02LC03LjUsNy42LDAuMiwtMTEuMTksNy4xOSw4MC42NCw2LjkyLC0xNS42NCwtMTYuOTYsMC41Miw1My4zLDczLjYsNjMuNSwxLDAsbm8sMC4zNywwLjgxLDAuNTYsMC4yNCwzLjAzLDMuNjIsNC43OSwyLjcKNCw1NTUuMTYsNCwtMTEuNiwtMTMuMiwyMy4zLDI4LjQsLTE2Ljc2LDIwLjM3LDczLjIzLC0yLjUyLDIuMTksLTUuNjUsLTEzLjk0LDMwLDEwLDIwLDQsMSxubywwLjIyLDAuOTksMC44MSwwLjQzLDIuMjEsMiwyLjE5LDEuOTQKNSw1NjAuMTgsNSwtNy42LC0xMC40LDkuMywyLjIsLTkuMDUsNy41MywyNDIuMTMsLTEuODgsNTMuODUsMTEuMzYsLTUuMzIsNTMuMyw2MS40LDU3LjQsMiwxLG5vLDAuMTYsMC4xOCwwLjIyLDAuMTQsMy42Nyw0Ljk4LDUuOTYsMy40OQo2LDUwNS43OCw2LC02LjYsLTcuOSw3LDUuNSwtOS4yNyw0LjUyLC0xMy4xNCwtMTAuMjksNi44NywtMy4wMiwtMy4wOSw3Ni43LDgyLjksNzkuOCwyLDEsbm8sMC4yLDAuNTYsMC4yLDAuMjMsNS4xNyw5LjYxLDkuMDksNy4yNgo3LDU1MS43MSw3LC03LjcsLTI1LjEsMi4yLDExLjMsLTEzLjM0LDEyLjA2LDE1LjAxLC0zNi4wNCw0OC4xOSwtMS42NiwxMi44NSw3MS4xLDgyLjksNzcsMiwxLG5vLDAuMTIsMC42OCwwLjI0LDAuMTYsMi45LDQuMzMsNS40OSwzLjQxCjgsNTM0LjA1LDgsLTEzLjcsLTYuNiwxMC44LDUsLTExLjYzLDExLjMzLDM4LjEsLTMuNTIsOS41NCwtMy4yLC02LjY2LDc2LjcsMTUsNDUuOCw0LDEsbm8sMC4xNCwwLjEzLDAuMzcsMC4yLDMuNTcsNy4yMiw5LjQxLDQuMTYKOSw2NTMuMTgsOSwtNy40LC0xOS4xLDkuOCw5LjYsLTE1LjM2LDEyLjQ5LC02OS42OSwtMTYuNjcsNy41NywtMTEuNTUsMTcuNjQsNzcuOCw4MC43LDc5LjIsMiwxLG5vLDAuMiwwLjE1LDAuMTIsMC4xMyw3LjQ5LDExLjExLDcuNTEsOC4wNwoxMCw1NzguMTIsMTAsLTguNywtMTMuNSwxMC4xLDUuOCwtMTMuNjIsOS4xMywyMy42MywtMTMuODEsNi41MywtMC43LDEwLjE4LDc1LjYsNjEuNCw2OC41LDIsMSxubywwLjE1LDAuNDUsMC4xNCwwLjE0LDIuNzksNS42MSw2LjU2LDQuNDQKMTEsNjUwLjcxLDExLC0yMSwtMTcuOSwyMC44LDIzLjUsLTIxLjkzLDI0LjM0LDExNy42LC0zMi4zMSwxOS44OCwxMS40MywtMy4zMywzMS4xLDIwLDI1LjYsNCwxLG5vLDAuNDUsMC43NywwLjg2LDAuNTUsNC44NCw0LjU4LDcuNTUsNC45NwoxMiw2MjkuNTQsMTIsLTE1LjQsLTExLjQsMjMuMiwxMS42LC0xNy42MywxNi42LDE5MS4xMywtMTUuNywtNS4wNSwtMTAuMzgsLTkuOTgsNTQuNCw2OC42LDYxLjUsMiwxLHllcywwLjE2LDAuMTgsMC4yNCwwLjI0LDMuNzksNC40MSw2LjksNC4wMQoxMyw1ODAuMTUsMTMsLTE5LjEsLTExLjMsOC41LC0xLjQsLTE3LjAxLDkuMDcsNTguMzQsMTEuMTIsLTExLjg5LDcuODgsLTEuNTEsMzAsNTkuMyw0NC42LDEsMSxubywwLjQ1LDAuMzUsMC4zMSwwLjE5LDMuOCw1LjI3LDUuMDIsMy41NQoxNCw2NzIsMTQsLTEyLjksLTExLjcsMTUuNCwxMywtMTYuODIsMTUuOSwyMDkuNTQsLTMuMDQsMi45OCwtNy43LC0xNy40LDgzLjMsNzMuNiw3OC41LDEsMCx5ZXMsMC4yMywwLjM2LDAuMDgsMC4xOSw0LjQyLDUuOCw3LjMxLDMuNTMKMTUsNTI2LjczLDE1LC0xMy40LC0xOC44LDksMTEuNywtMTAuNjUsMTAuNDgsMjI2LjU2LDEyLjgxLC05LjYxLC02LjE4LC02LjM0LDcxLjEsODAuNyw3NS45LDIsMSxubywwLjI4LDAuODEsMC41NiwwLjI1LDMuMjEsNC4zMSw1LjA2LDIuOTQKMTYsNTQwLjI0LDE2LC0xMSwtMTIuMiwxNCw4LC0xNS4wNCwxMC41LDEyMS4yMiwxMS44NiwtMTkuMzIsLTEuMzEsLTExLjIsNDEuMSwyMi4xLDMxLjYsNCwwLG5vLDAuMzEsMC41OSwyLjE2LDAuNDEsMy4wNiw0LjM1LDQuMTYsMi43NwoxNyw1NDEuNDYsMTcsLTEzLjgsLTkuMSwyMC43LDExLjIsLTE2Ljk2LDEyLjkyLDE1LjE0LC0xMy42NSwtMy43LC05LjA2LDcuNzMsNzUuNiwyNSw1MC4zLDQsMSxubywwLjI4LDAuMzksMC40OCwwLjI3LDQuMTcsNC41NCw0LjY1LDMuOTQKMTgsNTcwLjU4LDE4LC0xNS4zLC0yMC43LDE4LjcsMjIuMSwtMTkuNTcsMTguOTEsNjYuMDQsOS4wNCwxLjUyLDAuNTEsMTQuMTIsNjAsMzcuMSw0OC42LDIsMSxubywwLjI3LDAuNTYsMC40LDAuNTEsMy40NCw0LjgxLDUuNTIsMi41OQoxOSw2NzQuMTgsMTksLTE5LjgsLTE5LjEsMjguOSwyNS4yLC0yNC45NiwyOC40MSw0Mi41NSw1LjYzLC0zMS4yMywtNS4wNywxLjM4LDYxLjEsMTAsMzUuNiw0LDEsbm8sMC4zNCwyLjk3LDAuNjcsMC41NywyLjc5LDMuMTcsNi43Myw0LjE3CjIwLDU3NC40LDIwLC0xMS4zLC0yMi42LDE0LjksMjcuNiwtMTIuNyw1LjU5LDE1OC41NiwxNC45MiwtMzcuOTksLTEzLjY2LC0yNS40OCw2MS4xLDIwLDQwLjYsNCwwLG5vLDAuMzYsMC44NSwwLjc1LDAuMjUsMi4zOCwzLjY1LDUuNDcsNC4xNwoyMSw1MDkuNTQsMjEsLTkuOSwtMTkuOCwyMSwyMy4xLC0xNi4wOSwxNy41NSw0MS4xMywtNS4xNiwyNy42OCwtMy4xMywxMS44OSw3MS4xLDI3LjEsNDkuMSw0LDEseWVzLDAuMTIsMC4yLDAuMzIsMC40OCw5LjQyLDcuMzIsNy45Miw1LjIzCjIyLDUxMC41OCwyMiwtMTYuNCwtMTYuMiwyMyw5LjEsLTE2LjY2LDEzLjQyLDY4LjQzLDguMDgsLTE2LjE3LDEwLjYxLC0xMC42OSw0Mi4yLDgwLjcsNjEuNSwxLDEsbm8sMC4xMiwwLjQxLDAuMjEsMC4xMSw0LjE4LDUuMDMsNy4wOCw0LjA0CjIzLDQ1Mi4yMywyMywtOC41LC03LjksOS4xLDguMiwtMTAuOTYsOC43NCw0NC45NiwtMS40NywtMi40NywzLjMxLC0wLjE2LDQ3LjgsMjAsMzMuOSw0LDEsbm8sMC4xMSwwLjU4LDAuNDYsMC4zOCwyLjE0LDIuOSw0LjIyLDIuNTgKMjQsNTU2Ljg3LDI0LC0xNCwtMTIuOCwxNi4xLC0zLjksLTEzLjgxLDEwLjU3LDExNi40OCwxMS4zOSwtMjUuMTUsLTIuNjMsLTEyLjM5LDY1LjYsMjAsNDIuOCw0LDEsbm8sMC4yNiwwLjg1LDAuMjYsMC4zNiwyLjczLDQuNDMsNS4wNCwzLjQ5CjI1LDY3MC40NSwyNSwtOC45LC0xNC4xLDcuMiwtMy4zLC0xMy44NCw4LjcsLTY3LjA5LC0zMS4yNiwzOC4yNywtMTAuOTksMTYuMTMsNzAsMTAsNDAsNCwxLG5vLDAuMDksMC41OCwwLjEyLDAuMTEsNC4xNSw2Ljg4LDkuNDcsNS45NwoyNiw1MDkuNTIsMjYsLTIyLjEsOC44LDI0LjEsMTkuMiwtMTcuOTQsMjEuNDcsMjcwLjc1LDI0LjIzLC02MS4zMywtMTkuNDEsMTAuMDgsNzYuNyw4Mi45LDc5LjgsMiwwLG5vLDAuMzEsMC40MSwwLjI0LDAuMzEsMi4zNiwyLjY0LDQuNjcsMi45MgoyNyw0NTUuNjUsMjcsLTYuMSwtNy40LDguMywxNS41LC03Ljc2LDguNjUsNzguMjQsNS4zMSwtMTYuNzIsMC4wNSwtMi4zNiw3Ny44LDEwMCw4OC45LDIsMSx5ZXMsMC4wOSwwLjM0LDAuMDksMC4xMiwzLjk1LDUuODcsNi4zNywzLjIzCjI4LDQ3MS4wMiwyOCwtMTIuNywtMTIuNywyNCwxMC4yLC0xMy4yNywxOS4wNiw2My45OCw2LjY5LC0yNi4xNSw3Ljg5LC03LjE0LDY1LjYsMjIuMSw0My44LDEsMSxubywwLjQzLDEuMDIsMi41LDAuMzgsMy4zMiw2LjE0LDUuMjcsMi43MQoyOSw1NDguMjgsMjksLTcuMiwtOC45LDE0LjYsNy43LC05LjM1LDExLjYsNTUuODgsLTE2LjkyLC01LjkyLDkuOTEsMTQuODMsNzEuMSwxMDAsODUuNiwyLDEseWVzLDAuMTksMC4zNCwwLjE1LDAuMTgsMy4zNSw1LjY4LDYuNSwzLjkzCjMwLDUxMi41OCwzMCwtNS41LC04LjEsNC44LDEyLjcsLTUuNTIsNS45OSw0My43LC00LjA2LDguMjIsLTUuMzgsMTAuMzIsNzEuMSw3My42LDcyLjMsMywxLHllcywwLjE4LDAuNDYsMC4yNCwwLjIyLDQuMjEsNC45OCw2LjQ0LDMuNjQKMzEsNTg1LjA5LDMxLC02LjIsLTEzLjcsMTMuMSwtMC42LC0xMS4yOSw1LjM2LDkzLjU4LC03LjUyLC0xNi43NiwtMTYuNzEsMTIuNyw3MS4xLDQyLjEsNTYuNiw0LDAsbm8sMC4zOCwwLjU1LDAuNzIsMC4zNiwzLjE1LDMuMDQsNS45MywyLjk5CjMyLDY1Mi4xMSwzMiwtOC44LC0xOS41LDEuNiwyNi42LC0xMC4xNSwxMi41OCw2Ni43MiwxMS45LDM4LjQ3LC04LjEsLTYuODksNzYuNywyNSw1MC44LDIsMSx5ZXMsMC4xOSwwLjU3LDAuNjMsMC40MiwyLjkxLDMuODEsNS44LDMuNzIKMzMsODM0LjAyLDMzLC0yMS45LC0xOC45LDE4LjEsOS4xLC0yNS41NSwxNS44Nyw1Ny43MywtMzMuMTQsLTIzLjE5LC0xLjkyLC0xMC4yLDQyLjIsMjAsMzEuMSw0LDEsbm8sMC4zLDEuMDYsMi40MSwwLjM0LDQuMDUsNS4yNiw0LjA2LDQuMjUKMzQsNjAyLjA0LDM0LC02LjQsLTIuMyw1LjIsNS4xLC0zLjI1LDAuNDgsMzkxLjM4LDI5LjA3LC0zNC4xNCwtOS42OCw3LjMsNzcuOCw2MS40LDY5LjYsMiwxLG5vLDAuMzYsMC44LDAuNzgsMC4yMywxLjgyLDIuNjMsNC41LDEuOQozNSw0MzYuOTYsMzUsLTExLjEsLTguNywxNi43LDEwLjIsLTkuMTQsMTQuNzgsMTE2LjE1LDI2LjY4LC0yOS4xMSwxMi41NCwyLjM5LDgyLjIsNjEuNCw3MS44LDIsMSx5ZXMsMC4xLDAuMiwwLjE3LDAuNjIsNC40OSw1LjM2LDUuNzQsMy40NgozNiw1MzYuOTQsMzYsLTIuNSwtMTAuOCwxNS41LDIuMSwtMTQuNjUsMTAuODIsMTMwLjkzLC0xMi40MiwtMTEuNSwtMi4zNCwtNy4xOCw3Mi4yLDQ2LjQsNTkuMyw0LDAseWVzLDAuNDcsMS4yNiwwLjMyLDAuNTcsMy4yLDIuOTYsNC43MSwyLjYzCjM3LDUwMC4yMSwzNywtNi44LC0xLjIsNy45LDIuNiwtMTAuMjYsNS42MywxMTcuMzEsMTcuODcsLTI4LjUyLC00LjcsMTQuMjIsNzAsNTQuMyw2Mi4xLDMsMSxubywwLjE0LDAuMzQsMC4xOSwwLjIsNC40Nyw1Ljk2LDYuMzEsMy4zMwozOCw0NjcuMzgsMzgsLTguMSwtMTMuMiwxMC41LDE0LjIsLTEwLjIsMTMuMzEsNjcuOTcsMS43MywtMjEuNjIsLTMuMjYsLTUuMzQsNzIuMiw0NC4zLDU4LjMsMSwxLHllcywwLjE5LDAuMTgsMC4yLDAuMywzLjU2LDYuNTQsNi42MywzLjg3CjM5LDY3MS4yOCwzOSwtMjYuNSwtMTEuOSw0Ny43LDI1LjEsLTI3LjYxLDMxLjMyLDEwMC40NiwtMTguNzcsLTE5Ljg4LC0yNy4zMSwtMi4yLDY1LjYsNSwzNS4zLDQsMSx5ZXMsMC4zNywwLjc1LDIuMSwwLjY4LDMuMjQsMy45MywyLjkyLDQKNDAsNDgwLjkyLDQwLC03LjksLTEzLjUsOS43LDguOSwtMTAuMDMsMTAuOTIsMzYuNDgsLTkuOSwxMy41OSwtNi41NSwtMTcuOTIsMzUuNiw2MS40LDQ4LjUsMiwxLG5vLDAuMzMsMC44OSwwLjMzLDAuMzUsMy4wMiw0LjAyLDYuNTgsNC4wNAo0MSw1NjEuNjQsNDEsLTUuOCwtMS40LDExLjUsNy4zLC0xMS42MiwxMS45NywwLjY3LC00NC43MywxNS4zLC0xLjYxLDEzLjU1LDUzLjMsMTAwLDc2LjcsMiwxLHllcywwLjE3LDAuMzUsMC4yNCwwLjIsNC4yNCw2LjcxLDYuNzEsMy42OAo0Miw3MTIuMzIsNDIsLTE3LjcsLTIyLjksMTEuMSw1LjksLTIzLjg5LDE0LjM5LDExLjM1LC0yNS41Nyw0NC44MSwzLjYyLC0xMi40OSwzOC45LDEwLDI0LjQsNCwxLG5vLDAuMjMsMC43NiwxLjMxLDAuNDgsMy40Niw0LjMsNi4wMyw0LjYyCjQzLDYxOS4zNiw0MywtMTAuNiwxLjksNi44LDEwLjEsLTguNTcsNy4xOSwxNC42NiwtOS45NywtMTUuOTQsLTguNjMsMyw2MCwyNy4xLDQzLjYsNCwxLHllcywwLjE2LDAuNTEsMC4zNSwwLjIsMi44LDMuNjUsNC41MywzLjc3CjQ0LDY5My41Miw0NCwtOSwtMTIuMywxNy44LDEwLjIsLTE0LjczLDE2LjE4LC0yLjgsMjAuMDEsLTguMjksMTIuNzgsMzAuMzYsNzYuNywzMi4xLDU0LjQsNCwxLHllcywwLjI0LDAuMzcsMS40NSwwLjU3LDIuMDcsMi43NSwxLjg5LDEuOTgKNDUsNzYzLjAxLDQ1LC0xNS44LC0yMi4zLDE2LjIsOC40LC0yMy42OSwxNS4xMSw1NC41OSwyLjQ4LC0yMi40OSwxLjkzLC0xNiw3Ni43LDE1LDQ1LjgsNCwxLHllcywwLjI2LDAuNSwwLjQ5LDAuMTksNS45NCw3LjA3LDcuNTgsNi4zNQo0Niw3MjUuOTcsNDYsLTE0LjEsLTIxLjcsMjkuNCw1My4xLC0xNC4zNCw0MC44NywxMDIuNTUsMjAuMzcsMTMxLjcxLDE4Ljc0LC0zOS4wMyw0My4zLDIwLDMxLjcsNCwxLG5vLDAuMzQsMC44NywxLjk3LDAuODUsMi4zOCwyLjUyLDIuMTQsMS45NQo0Nyw1NjMuNzcsNDcsLTEyLjcsLTE5LjYsMjEuNiwxMy45LC0xMy43NiwxMC4wOCwyLjMyLDUuMDgsMTEuNDYsLTEuMDksLTE1LjUyLDY0LjQsODcuOSw3Ni4yLDEsMSx5ZXMsMC4yMiwwLjQyLDAuMTMsMC4xNSwzLjI2LDcuNzUsOC4yNSw0LjQ0CjQ4LDU0MC4yMSw0OCwtNS4xLC0xOC4xLDUuMSwxOS45LC0xMS4yNywxMC44Niw4Ny41MSwtNy40MiwxMy4wNiwtNi41NSwtMTAuMTIsODcuOCwyNSw1Ni40LDQsMSxubywwLjIsMC42MiwwLjYyLDAuMjYsMi42LDIuNTYsMy4zOSwyLjMxCjQ5LDcyOC4xMiw0OSwtMTMuNiwtMTcuNiwzMy40LDUsLTI1LjY3LDIwLjY0LDE3Mi41OCwtMjguMDEsLTcwLjk3LC01LjUsMTguMTcsNzcuOCw2MS40LDY5LjYsMiwxLG5vLDAuMjgsMC41NSwwLjUxLDAuNSwyLjQ4LDUuMDksNC43NCwyLjY3CjUwLDUzMS43Niw1MCwtNy40LC01LjYsNy4yLDMuMiwtOS4yMSw3LjQ2LDcxLjgsLTE1LjY5LDEyLjY4LC04LjUyLDUsNjQuNCwyMCw0Mi4yLDQsMSxubywwLjEzLDAuODMsMC4zMywwLjM0LDIuNDIsMy43OCw1LjEyLDIuNTgKNTEsNTM5LjkyLDUxLC0xMS4xLC0xNC4xLDIxLjYsMTMuOCwtMTUuODMsMTQsMjQuMjUsOC4xOSwtOS4zNywxNC42NCwtMC4wMSw0Ni43LDc3LjksNjIuMywxLDEseWVzLDAuMTYsMC4zOCwwLjE5LDAuMTMsMi4xNCwzLjM1LDQuNTEsMi40Ngo1Miw1MDMuMjUsNTIsLTEwLjksLTYuOCwxMywxMy44LC0xMS44MSwxMi40MiwyOS43NSwtMi40NSw2Ljg4LDIuODIsLTMuMjcsNjUuNiwyMCw0Mi44LDQsMSxubywwLjU0LDAuNjIsMC40OSwwLjQ1LDIuNzksNSw3LjQsMy4xCjUzLDQ4Ny4zNyw1MywtMTMuNCwtMTIuNiwxNS4yLDEwLjMsLTE0LjUxLDE1LjQyLDEwMS43OSwyLjUzLDAuMDcsLTAuMjQsLTUuMTMsODguOSw1NC4zLDcxLjYsMiwxLG5vLDAuMTgsMC4yMiwwLjI4LDAuMTcsMi45Nyw1LjA3LDUuNTgsMi44MQo1NCw1MTYuNjUsNTQsLTkuNywtMTAuMSwxOC45LC0wLjQsLTExLjczLDcuMiwxMzMuNzQsMC44OCwtNDEsLTMuNzMsMTIuOCw4Mi4yLDgyLjksODIuNSwyLDEsbm8sMC4zMywwLjU1LDAuMjgsMC4yMSw0LjQxLDcuODIsOS42NCw2LjY1CjU1LDUzNy41NSw1NSwtOCwtMTMuNCwxMy44LDQsLTEyLjU1LDkuNDIsMTEyLjU0LC03LjU4LC0zLjQ3LDEwLjQ3LDIuNTMsNzEuMSw3My42LDcyLjMsMiwxLHllcywwLjE4LDAuMzEsMC4yLDAuMjMsNi4xOCw1LjY1LDUuODIsNC40Nwo1Niw0ODEuNCw1NiwtMTQuNSwtMTcuNCwyNywxNi44LC0xNi4xLDIwLjkzLDM3LjIxLDQxLjcsLTIzLjcxLC0xLjc3LC0xLjE3LDc2LjcsNjQuMyw3MC41LDMsMSx5ZXMsMS4yNiwwLjcyLDAuMzQsMC4xNSwzLjY4LDQuMTcsNC4xMSwyLjYKNTcsNjQ0LjY5LDU3LC0yMy43LC0xLjksMjUuNSw3LjMsLTIwLjUsMjQuNDgsMjQ0LjE0LC0yMy4zNywtNzQuNjEsNS4yMiwxNi43MSw2MCw2My42LDYxLjgsMiwwLG5vLDAuMSwwLjM0LDAuMSwwLjMsMy45MSw3Ljg4LDUuNDksMy45Nwo1OCw3MzYuNzksNTgsLTE2LjksLTUuOSwxNy45LDEyLjQsLTI1LjE3LDE5LjQ1LC00Mi4xNiwtNTEuMjcsNi4zMSwtMS43NCw3LjE5LDU0LjQsNzcuOSw2Ni4yLDIsMCx5ZXMsMC4zLDEuNjksMC4xNiwwLjQ0LDQuMTcsNC40Myw4LjIyLDMuODEKNTksNTE0Ljc1LDU5LC0yLjIsLTEuMSw5LDE4LjUsLTEzLjE0LDEzLjU0LDEwMC42OCwtMjcuNzUsMjQuMTMsLTcuMjcsLTI0LjA1LDgzLjMsOTAsODYuNywzLDEsbm8sMC4zMiwwLjQ0LDAuMzksMC4zMiwzLjE0LDUuNjMsNi4wNSw1LjE1CjYwLDYyOC44LDYwLC00LjksLTguOSw2LjcsMS40LC05LjIxLDQuMTEsNzcuNzIsNS43MywxNS42NiwtMzYuNjksLTIuNTIsNzcuOCwxMDAsODguOSwyLDEseWVzLDAuMTQsMC4zOCwwLjE5LDAuMjYsMy4xNywzLjg2LDQuODIsMi4yNgo2MSw2OTUuMSw2MSwtMy44LC05LjgsMTUuNSwtMTAuNiwtMTMuMTUsNC45OCwxNTAuMDQsLTQuMTYsLTM3LjIxLDEuMzIsMTAuNTYsNzcuOCw4MC43LDc5LjIsMiwwLG5vLDAuMTEsMC4zNywwLjI2LDAuMTYsNC4yMiwzLjU4LDUuMjMsMy4wMQo2Miw0NTUuMzIsNjIsLTcuMSwtNi40LDEyLjQsNC4xLC03LjMyLDguNTUsOTIuNTksLTUuNzksLTE5LjAyLDMuMjcsLTAuNTQsNzYuNywxMDAsODguMywyLDEseWVzLDAuMjMsMC41MywwLjM1LDAuMjMsMi42MSwyLjU4LDQuMzQsMy4zNQo2Myw2NDcuOTMsNjMsLTE2LC01LjksMTkuMiw2LC0xNC41NSwxMy4xOSwxNDkuNzUsMTQuMjIsLTkxLjMzLDYuNTUsLTE3LjEyLDc2LjcsNzIuOSw3NC44LDIsMSx5ZXMsMC4xMiwwLjI4LDAuMzMsMC4xMywzLjMyLDQuNzMsNS41LDMuMDIKNjQsNTM5LjkxLDY0LC02LjQsLTkuNCw1LjcsMTAuNCwtMTIuMjksNy43LDUwLjMzLC0zMC4zOCwyMS40MywtMy44NSwxNC4zMiw2NC40LDU5LjMsNjEuOSwyLDEsbm8sMC4yNiwwLjcsMC4xMywwLjI1LDMuMTQsNi4zOSw2LjksMy4xOQo2NSw5MTMuMDIsNjUsLTI0LjcsLTExLjMsMzUsMTQuNywtMTkuODQsMTkuMDIsMTEzLjAzLDIxLjIyLC0xNS4zLC0yOS4xOCwtNC4zNiwyMi4yLDEyLjEsMTcuMiw0LDAsbm8sMS4xOSwxLjIsMy44MiwxLjc3LDUuNzgsNS4zNSwyLjkyLDMuNTkKNjYsNTQ4LjkxLDY2LC0xMS41LC0xMC45LDE3LjgsMTkuOCwtMTMuMDYsMTYuODQsLTEyLjMzLC00LjE1LDIxLjU5LDYuOTUsLTE2LjYzLDQ0LjQsMTAsMjcuMiw0LDEsbm8sMC4xOCwwLjg0LDAuMzcsMC40LDIuNTcsMi45Niw0LjU0LDMuMDMKNjcsNDQyLjk0LDY3LC0zLjMsLTkuOCwzLjEsNi44LC01LjkxLDEuNjIsOTUuNDQsNC40OCwxNS44NSwtMC42NywtMy42OCwxOC45LDEwLDE0LjQsNCwwLG5vLDAuMzQsMC4zNSwwLjcyLDAuNDMsMi4zMiwyLjYsMi41NSwyLjY0CjY4LDg5MC44Niw2OCwtMy43LC0yOS42LDExLjQsLTAuNywtNi42MSw1LjgxLC0yNDkuNDMsLTk3LjIsMTc1LjYsMTAuMTMsNy4yOSwyNS42LDE3LjEsMjEuMywzLDAsbm8sMC4zMiwwLjQ4LDAuNjMsMC4zNiwzLjI4LDMuOCw1LjQyLDMuMTkKNjksNTI1Ljk5LDY5LC04LjMsLTEwLjMsMTIuNCwxMC42LC0xMC42NSwxMS4zMSwxNy45OCwtMTAuNzgsLTExLjcsLTguOTYsNC4yOCw1MCw1OS4zLDU0LjYsMiwxLG5vLDAuMjksMC41MywwLjI5LDAuMywyLjc2LDguMDUsOSw2LjI3CjcxLDY0NC4zOCw3MSwtMTYuNCwtMTAuMiwyNC41LDIwLjgsLTE4LjQ1LDIwLjIyLDYxLjE2LDUuMDIsNDQuNjksLTkuMzMsNS4zNiw4Mi4yLDE1LDQ4LjYsNCwxLG5vLDAuMzMsMC42MSwwLjksMC40LDIuMzQsMi42OCwyLjAzLDIuNDkKNzIsNjQzLjUsNzIsLTguOSwtMTYuNywxNS4zLDguNCwtMTAuODMsMTQuNjEsMTAzLjIxLC02LjEsLTE0LjEzLC0xNy45OCw0LjEsNDIuMiwyNy4xLDM0LjcsMSwxLG5vLDAuMzIsMC41NSwwLjQsMC4yOSwzLjA1LDIuOTQsNC4wMSwzLjA1CjczLDQ4My41LDczLC05LjUsLTguMywyMC41LDE4LjIsLTguMDEsMTkuODcsNDQuNDYsLTYuMTksMzguMTQsMTAuMzEsLTEuMzMsNzYuNyw2Mi45LDY5LjgsMywxLG5vLDAuMjYsMC44MywwLjM0LDAuNCw1Ljc3LDUuMzEsOS4yOCw0LjcxCjc0LDY2OC43LDc0LC0xNS45LC0xNywxOS42LDEuMiwtMTkuOTgsMTUuNTcsMTg5LjA3LC0zLjQ1LC02LjU5LC0xNi40OCwyLjA0LDc3LjgsMTAsNDMuOSw0LDEsbm8sMC4xOCwwLjc5LDAuOTQsMC4yNCwzLjMsNS41NCwzLjk2LDMuODkKNzUsOTIwLjM4LDc1LC0xMy4yLC0xNS44LDE1LjMsMTcuOCwtMTkuOTUsMTUuODMsLTgyLjU3LC0zNS4yNSw0MC43NiwtNy4yNywtMTkuMzksNTIuMiwxNSwzMy42LDQsMSxubywwLjU3LDMuMTcsMS4yMSwwLjMyLDMuMDIsMi45NSwzLjAxLDMuODMKNzYsNTUwLjU0LDc2LC05LjcsLTksOC43LC0wLjgsLTEwLjY2LDYuODUsMTM5LjYxLC01LjQyLDkuNTYsLTUuNzEsMTEuMSw4Ny44LDkyLjksOTAuMywyLDAsbm8sMC4xNCwwLjI1LDAuMiwwLjIsMy42Miw0LjExLDUuMDgsMy42Nwo3Nyw1NTMuNzIsNzcsLTkuNywtMTEuNCwxMC4zLC00LjEsLTEyLjM1LDYuNjIsNDguMjMsLTIwLjA2LDIuNDYsLTEyLjYsLTMuNCwyOC45LDQ3LjEsMzgsNCwwLG5vLDAuMTMsMC4yLDAuMiwwLjE0LDYuNjgsMTAuMjEsOS44NCwxMi4yMwo3OCw1NTUuMzYsNzgsLTEwLjQsLTYuNywxNy41LDIyLC0xMy42MywxOC4xLDEyNy44MywzLjcxLC0yMS43NywwLjI1LC0xMS45Miw3MS4xLDgwLjcsNzUuOSwxLDEseWVzLDAuMTgsMC43NywwLjU0LDAuMzMsMy41OSw1Ljg2LDYuMzYsNC41NAo3OSw2NDkuNDEsNzksLTksLTkuOCwxNy40LC0wLjksLTE0LjY5LDcuMyw3NS40OCwtMTEuODgsLTE1LjgzLDcuMjIsLTExLjY3LDUzLjMsMjAsMzYuNyw0LDAsbm8sMC40MSwyLjg3LDIuMjgsMC44OSwyLjUyLDIuNTgsMy4xMiwzLjgxCjgwLDU1Ni40Niw4MCwtMTEuNCwtMTIuOCwxOS4zLDE5LC0xNi42MywxOS4zMiwyODAuOTIsLTM1LjcxLDUuMDYsOC4yLC0zLjU1LDY1LjYsMjUsNDUuMyw0LDEseWVzLDAuMzQsMC44NCwwLjIzLDAuMzIsNC4xLDYuNDUsNy4xOCw0LjA4CjgxLDQxMS45Myw4MSwtNC45LC0xMC45LDkuNCwxNSwtNy40NSw3LjI5LDEyLjE0LC0yLjU2LDE1LjI1LC0wLjI0LDYuMjMsNjUuNiw2My42LDY0LjYsMiwxLHllcywwLjI1LDAuNjIsMC4yNiwwLjIyLDYuMTUsNi4zLDYuNzUsNC45Cg==',
				),
			],
		style={
			'width': '100%',
			'height': '60px',
			'borderWidth': '1px',
			'borderStyle': 'dashed',
			'borderRadius': '5px',
			"display": "none",
			},
		),

	# line break
	dcc.Markdown('''
&nbsp;
		'''),

	html.Div(
		id="selectDataFieldsPrompt",
		children=["Select data fields:"],
		style={"display":"none", 'text-align':'center'},
		),

	html.Div(id='datafieldselector_container',
		children=[
			# data field selector
			dcc.Dropdown(
				id=DATATYPEDROPDOWN_ID,
				options=[],
				multi=True,
				value=[],
				placeholder='',
				),
			],
		style={
			"display":"none"
			},
		),

	# line break
	dcc.Markdown('''
&nbsp;
		'''),

	html.Div(
		id="selectDataGroupFieldsPrompt",
		children=["Select data grouping criteria:"],
		style={"display":"none", 'text-align':'center'},
		),

	html.Div(id='dataGroupFieldSelector_container',
		children=[
			dcc.Dropdown(
				id='dataGroupFieldSelector',
				options=[{"label":"None", "value":""}],
				multi=False,
				value='',
				placeholder='',
				),
			],
		style={
			"display":"none"
			},
		),

# 	#line break
# 	dcc.Markdown('''
# &nbsp;
# 		'''),

	# html.Div(
	# 	id="binSizePrompt",
	# 	children=["Select histogram bin size:"],
	# 	style={
	# 		"display":"none",
	# 		'text-align':'center'
	# 		},
	# 	),

	# html.Div(id='binSizeSlider_container',
	# 	children=[
	# 		# data field selector
	# 		dcc.Slider(
	# 			id="binSizeSlider",
	# 			min=1,
	# 			max=50,
	# 			marks=dict({1:"1"}.items() | {i:str(i) for i in range(5,55,5)}.items()),
	# 			value=1,
	# 			step=1,
	# 			),
	# 		],
	# 	style={
	# 		"display":"none"
	# 		},
	# 	),

	#line break
	dcc.Markdown('''
&nbsp;
		'''),

	gdc.Import(src="https://rawgit.com/MasalaMunch/6de3a86496cca99f4786d81465980f96/raw/ef9212021b7de605562ab284713e37f07d7e9e97/statscope.js"),

	# prevents things from being cut off or the elements being
	# excessively wide on large screens
	], style={'maxWidth':'1000px',
			  'padding-left':'0px', 'padding-right':'110px',
			  'user-select':'none', '-ms-user-select':'none',
			  '-moz-user-select':'none', '-webkit-user-select':'none',
			  }
	)

# creates the "app" helper variable
app = dash.Dash(__name__)
app.layout = INITIAL_LAYOUT
server = app.server
app.scripts.append_script({"external_url":"https://code.jquery.com/jquery-1.11.0.min.js"})
app.title = WEBAPP_TITLE
app.css.append_css(dict(external_url=CSS_URL))
app.css.append_css(dict(external_url=
	'https://rawgit.com/MasalaMunch/db53bfa58350aa4a969aeba5689d086e/raw/87acfae74b5bfff91a295a0f90458ae796d54cc9/statscope.css'
	))

@app.callback(
	Output("rangeToZeroIndicator", "children"),
	[Input("rangeToZeroButton", "n_clicks")],
	[State("rangeToZeroIndicator", "children")]
	)
def updateRangeToZeroIndicator(nClicks:int, rangeToZeroIndicator:str):
	if nClicks > 0:
		return ("false" if (rangeToZeroIndicator == "true") else "true")
	return "true"

@app.callback(
	Output("graphTypeIndicator", "children"),
	[Input(GRAPHTYPESLIDER_ID, "value")],
	)
def updateGraphTypeIndicator(graphTypeIndex:int):
	return GRAPHTYPE_CHOICES[graphTypeIndex];

@app.callback(
	Output('drawMode_info', 'children'),
	[Input(GRAPHTYPESLIDER_ID, 'value')],
	# [Input('drawingControl_slider', 'value'),
	#  Input(GRAPHTYPESLIDER_ID, 'value')],
	# [State('drawMode_info', 'children')],
	)
# def updateDrawModeInfo(sliderIndex:str, graphType:int, drawModeInfo:list):
def updateDrawModeInfo(graphType:int):
	graphTypeName = GRAPHTYPE_CHOICES[graphType]
	output = dict(choices=DRAWMODE_CHOICES)
	if graphTypeName in ('Density Plot', 'Violin Plot', 'Table'):
		output['i'] = 0
	elif graphTypeName == 'Dot Plot':
		output['i'] = 1
	else:
		output['i'] = 2
	return json.dumps(output)

# @app.callback(
# 	Output('drawingControl_slider', 'marks'),
# 	[Input('drawMode_info', 'children')],
# 	)
# def updateDrawingControlSliderMark(drawModeInfo:str):
# 	drawMode = DRAWMODE_CHOICES[json.loads(drawModeInfo)['i']]
# 	out = {i: m for i, m in enumerate(DRAWCONTROL_CHOICES)}
# 	out[len(DRAWMODE_CHOICES)-1] = 'Draw: ' + drawMode
	# return out

# @app.callback(
# 	Output('showdata_checkbox_info', 'children'),
# 	[Input('drawingControl_slider', 'value')],
# 	)
# def updateShowDataCheckBoxInfo(sliderIndex:int):
# 	if sliderIndex == 0: # bottom choice
# 		return json.dumps({'allowDrawing':False})
# 	else:
# 		return json.dumps({'allowDrawing':True})

# @app.callback(
# 	Output('clear_drawing', 'children'),
# 	[Input('drawingControl_slider', 'value')],
# 	)
# def updateClearDrawing(sliderIndex:int):
# 	if sliderIndex == 1: # middle slider position
# 		return "true"
# 	else:
# 		return "false"

import base64
import io
import csv

@app.callback(
	Output("datafieldselector_container", "children"),
	[Input("data_uploader", "contents"),
	 Input("data_uploader", "filename"),],
	)
def updateDataFieldSelector(fileContents:str, filename:str):

	return [dcc.Dropdown(
		id=DATATYPEDROPDOWN_ID,
		options=[
			{"label":e,"value":e}
			for e in
			list(csv.reader(io.StringIO(base64.b64decode(fileContents.split(',')[1]).decode("utf-8"))))[0]
			],
		multi=True,
		value=["rktProcedural", "rktConceptual"] if filename=="ind-diff-regression.csv" else [],
		placeholder='',
		)]

@app.callback(
	Output("uploaded_fileAsJson", "children"),
	[Input("data_uploader", "contents"),],
	)
def updateCsvAsJson(fileContents:str):

	return json.dumps(
		list(csv.DictReader(io.StringIO(base64.b64decode(fileContents.split(',')[1]).decode("utf-8"))))
		)

@app.callback(
	Output("dataGroupFieldSelector_container", "children"),
	[Input("data_uploader", "contents"),
	 Input("data_uploader", "filename"),],
	)
def updateDataGroupFieldSelector(fileContents:str, filename:str):

	return [dcc.Dropdown(
		id="dataGroupFieldSelector",
		options=[
			{"label":e,"value":e}
			for e in
			list(csv.reader(io.StringIO(base64.b64decode(fileContents.split(',')[1]).decode("utf-8"))))[0]
			] + [{"label":'None',"value":''}],
		multi=False,
		value='',
		placeholder='',
		)]

def isToggledOn(nClicks:int):
	return (nClicks % 2 == 0)

def guessBandwidth(values):
	# adapted from https://github.com/plotly/plotly.js/blob/1a050e85c2b901b2579af0a5e09df00197271ca9/src/traces/violin/calc.js#L74-L81
	return max(
		1.059 * min(
			np.std(values),
			(np.percentile(values,75)-np.percentile(values,25)) / 1.349
			)
		* len(values)**-0.2, (max(values)-min(values))/100
		)

@app.callback(
	Output("graphTuning_slider_container", "children"),
	[Input(GRAPHTYPESLIDER_ID, "value"),
	 Input(DATATYPEDROPDOWN_ID, 'value'),
	 Input('dataGroupFieldSelector', 'value'),
	 Input("uploaded_fileAsJson", "children")]
	+ [ Input("boxPlotToggles-"+e, "n_clicks") for e in BOXPLOTINFO_CHOICES ],
	[State("graphTuning_slider", "value")],
	)
def updateGraphTuningSliderContainer(graphTypeIndex:int, chosenDataFields:list, dataGroupField:str, csvAsJson:str, boxPlotMean, boxPlotOutliers, boxPlotNotch, currentSliderValue):

	graphType = GRAPHTYPE_CHOICES[graphTypeIndex]

	noWrapStyle = {"whiteSpace":"nowrap", "textOverflow":"visible"}

	if graphType == "Histogram":

		marks = {i:str(i) for i in range(MIN_BINSIZE+4,MAX_BINSIZE+5,5)}
		marks[MIN_BINSIZE] = {"label":"Bins: "+str(MIN_BINSIZE), "style":noWrapStyle}
		return [
			dcc.Slider(
				id="graphTuning_slider",
				min=MIN_BINSIZE,
				max=MAX_BINSIZE,
				marks=marks,
				value=MIN_BINSIZE,
				step=1,
				vertical=True,
				included=False,
				),
			]

	elif graphType == "Density Plot":

		return [
			dcc.Slider(
				id="graphTuning_slider",
				min=0,
				max=1,
				marks={0: {"label":"KDE", "style":noWrapStyle}, 1: "Normal"},
				value=0,
				step=None,
				included=False,
				vertical=True,
				),
			]

	elif graphType == "Violin Plot":

		dataSetFromJson = json.loads(csvAsJson)

		if dataGroupField == '':
			groupedDataSets = {'': dataSetFromJson}
		else:
			groupedDataSets = defaultdict(list)
			for dataDict in dataSetFromJson:
				groupedDataSets[" ({})".format(str(dataDict[dataGroupField]))].append(dataDict)

		# convert the data being plotted into numbers
		traceValues = []
		for fieldName in chosenDataFields:
			for groupName in groupedDataSets:
				traceValues.append([])
				for dataDict in groupedDataSets[groupName]:
					traceValues[-1].append(float(dataDict[fieldName]))

		maxBandwidth = 0
		for values in traceValues:
			bandwidth = guessBandwidth(values)
			if bandwidth > maxBandwidth:
				maxBandwidth = bandwidth

		markStep = 5 if maxBandwidth > 10 else 1
		marks = {i:str(i) for i in range(0, int(2*maxBandwidth)+markStep, markStep)}
		marks[0] = {"label":"Bandwidth: Auto", "style":noWrapStyle}

		return [
			dcc.Slider(
				id="graphTuning_slider",
				min=0,
				max=int(2*maxBandwidth),
				marks=marks,
				value=0,
				step=0.00001,
				vertical=True,
				included=False,
				),
			]

	elif graphType == "Table":
		return [
				dcc.Slider(
					id="graphTuning_slider",
					min=0,
					max=3,
					value=0,
					marks={i:{"label":e, "style":{"transform":"translate(0,10px)"}} for i,e in enumerate(TABLEINFO_CHOICES)},
					step=None,
					included=False,
					vertical=True,
				),
		  ]

	elif graphType == 'Box Plot':

		boxPlotToggle_nClickArray = (boxPlotMean, boxPlotOutliers, boxPlotNotch)

		return [
			dcc.Slider(
				id="graphTuning_slider",
				min=0,
				max=len(BOXPLOTINFO_CHOICES)-1,
				value=currentSliderValue,
				marks={
					len(BOXPLOTINFO_CHOICES)-1-i: {
						"label": e,
						"style": {
							"whiteSpace": "nowrap",
							"overflow": "visible",
							"color": "#666" if isToggledOn(boxPlotToggle_nClickArray[i]) else "lightgray",
							},
						}
					for i,e in enumerate(BOXPLOTINFO_CHOICES)
					},
				step=None,
				included=False,
				vertical=True,
				)
			]

	elif graphType in ('Bar Plot', 'Dot Plot'):

		return [
			dcc.Slider(
				id="graphTuning_slider",
				min=0,
				max=len(BARDOTPLOTERROR_CHOICES)-1,
				marks={len(BARDOTPLOTERROR_CHOICES)-1-i: {"label":e, "style":{"whiteSpace": "nowrap", "overflow": "visible"}}
						for i,e in enumerate(BARDOTPLOTERROR_CHOICES)},
				value=0,
				step=None,
				included=False,
				vertical=True,
				),
			]

from collections import Mapping

@app.callback(
	Output("drawingInstructions", "children"),
	[Input(DATATYPEDROPDOWN_ID, 'value'),
	 Input(GRAPHTYPESLIDER_ID, 'value'),
	 Input('dataGroupFieldSelector', 'value'),
	 Input('showDataIndicator', 'children'),
	 Input("graphTuning_slider", "value")]
	)
def updateDrawingInstructions(chosenDataFields:list, graphType:int, dataGroupField:str, showDataIndicator:str, graphTuningSliderIndex:int):

	instructions = ""
	if showDataIndicator == "false":
		instructions += "Make"
		graphTypeName = GRAPHTYPE_CHOICES[graphType]
		if graphTypeName == "Density Plot":
			if graphTuningSliderIndex is None or graphTuningSliderIndex < 0 or graphTuningSliderIndex >= len(DENSITY_CURVE_TYPES):
				graphTuningSliderIndex = 0
			if DENSITY_CURVE_TYPES[int(graphTuningSliderIndex)] != "kde":
				instructions += " normal"
		if len(chosenDataFields) == 1:
			instructions += " a"
		instructions += " " + graphTypeName.lower() + ("" if len(chosenDataFields) == 1 else "s")
		if graphTypeName == "Histogram":
			instructions += " (bins = " + str(graphTuningSliderIndex) + ")"
		if graphTypeName == "Violin Plot":
			if graphTuningSliderIndex != 0:
				instructions += " (bandwidth = " + str(graphTuningSliderIndex) + ")"
		elif graphTypeName == "Table":
			return ""
		instructions += " of"
		for i,field in enumerate(chosenDataFields):
			instructions += " " + field
			if i != len(chosenDataFields)-1 and len(chosenDataFields) > 2:
				instructions += ","
			if i == len(chosenDataFields)-2:
				instructions += " and"
		if dataGroupField != '':
			instructions += " (grouped by {})".format(dataGroupField)
		instructions += '. Double-click ' + ('it' if len(chosenDataFields) == 1 else 'them') + ' to submit.'
	return [instructions]

PLOTLY_DEFAULT_COLORS = [

	# '#1f77b4',  # muted blue
	# '#ff7f0e',  # safety orange
	# '#2ca02c',  # cooked asparagus green
	# '#d62728',  # brick red
	# '#9467bd',  # muted purple
	# '#8c564b',  # chestnut brown
	# '#e377c2',  # raspberry yogurt pink
	# '#7f7f7f',  # middle gray
	# '#bcbd22',  # curry yellow-green
	# '#17becf',  # blue-teal
    
    '#8dd3c7' , # R Color Brewer - Set 3 (Pastel)
    '#fb8072',  # R Color Brewer - Set 3 (Pastel)
    '#bebada',  # R Color Brewer - Set 3 (Pastel)
    '#984ea3',  # R Color Brewer - Set 3 (Pastel)
    '#fdb462',  # R Color Brewer - Set 3 (Pastel)
    '#b3de69',  # R Color Brewer - Set 3 (Pastel)
    '#80b1d3',  # R Color Brewer - Set 3 (Pastel)
    '#bc80bd',  # R Color Brewer - Set 3 (Pastel)
    '#fccde5',  # R Color Brewer - Set 3 (Pastel)
	'#ffffb3',  # R Color Brewer - Set 3 (Pastel)


	#'#440154FF', # viridis 1
	#'#39568CFF', # viridis 2
	#'#1F968BFF', # viridis 3
	#'#73D055FF', # viridis 4
	#'#481567FF', # viridis 5
	#'#33638DFF', # viridis 6
	#'#20A387FF', # viridis 7
	#'#95D840FF', # viridis 8
	#'#482677FF', # viridis 9
	#'#2D708EFF', # viridis 10
	#'#29AF7FFF', # viridis 11
	#'#B8DE29FF', # viridis 12
	#'#453781FF', # viridis 13
	#'#287D8EFF', # viridis 14
	#'#3CBB75FF', # viridis 15
	#'#DCE319FF', # viridis 16
	#'#404788FF', # viridis 17
	#'#238A8DFF', # viridis 18
	#'#55C667FF', # viridis 19
	#'#FDE725FF', # viridis 20
	]

from collections import defaultdict

@app.callback(
	Output('graph_container', 'children'),
	[Input(DATATYPEDROPDOWN_ID, 'value'),
	 Input(GRAPHTYPESLIDER_ID, 'value'),
	 # Input('drawingControl_slider', 'value'),
	 Input('dataGroupFieldSelector', 'value'),
	 # Input('drawingControl_slider', 'value'),
	 Input("uploaded_fileAsJson", "children"),
	 Input("graphTuning_slider", "value"),
	 Input("rangeToZeroIndicator", "children"),
	 Input("showDataIndicator", "children")]
	+ [ Input("boxPlotToggles-"+e, "n_clicks") for e in BOXPLOTINFO_CHOICES ],
	)
def updateGraph(chosenDataFields:list, graphType:int, dataGroupField:str, csvAsJson:str, tuningSliderValue:int, rangeToZeroIndicator:str, showDataIndicator:str, boxPlotMean, boxPlotOutliers, boxPlotNotch):
	"""
	updates the graph based on the chosen data fields, data filters,
	and graph type
	"""

	graphConfig = dict(
		modeBarButtonsToRemove=["sendDataToCloud", "toggleSpikelines", "hoverClosestCartesian", "hoverCompareCartesian", "toggleHover", "select2d", "lasso2d"],
		displaylogo=False,
		displayModeBar="hover",
		# fillFrame=True,
		)

	# turn the position on the graph type slider into a graph type name
	graphType = GRAPHTYPE_CHOICES[graphType]

	showDataBoolean = (showDataIndicator == "true")
	rangeToZeroBoolean = (rangeToZeroIndicator == "true")

	layout = dict(
		paper_bgcolor='rgba(0,0,0,0)',
		plot_bgcolor='rgba(0,0,0,0)',
		xaxis=dict(showline=False, zeroline=False, hoverformat='.1f', fixedrange=True, showgrid=False, titlefont=dict(size=15), ticks='outside', ticklen=6, tickwidth=2.75, tickcolor='darkgray', tickfont = dict(size = 14, family = "Arial")),
		yaxis=dict(showline=False, zeroline=False, hoverformat='.1f', fixedrange=True, showgrid=False, title=str(chosenDataFields)[1:-1].replace("'",""), titlefont=dict(size=15), ticks='outside', ticklen=6, tickwidth=2.75, tickcolor='darkgray', tickfont = dict(size = 14, family = "Arial")),
		legend=dict(orientation="h", x=0.5, y=-0.1, xanchor="center"),
		showlegend=False,
		margin=dict(t=20, l=140), #TODO adapt left padding to length of labels
		height=400,
		titlefont=dict(size=14),
		)
	if rangeToZeroBoolean:
		layout['xaxis']['rangemode'] = 'tozero'
		layout['yaxis']['rangemode'] = 'tozero'
	if not showDataBoolean:
		layout['legend']['font'] = dict(color="rgba(0,0,0,0)")

	if len(chosenDataFields) == 0:
		return [dcc.Graph(id=GRAPH_ID, figure=go.Figure(layout=layout), config=graphConfig)] # empty graph

	dataSetFromJson = json.loads(csvAsJson)

	if dataGroupField == '':
		groupedDataSets = {'': dataSetFromJson}
	else:
		groupedDataSets = defaultdict(list)
		for dataDict in dataSetFromJson:
			groupedDataSets[" ({})".format(str(dataDict[dataGroupField]))].append(dataDict)

	# convert the data being plotted into numbers
	try:
		minValue, maxValue = (0, 0) if rangeToZeroBoolean else (float("inf"), -float("inf"))
		traceValues = []
		for fieldName in chosenDataFields:
			for groupName in groupedDataSets:
				traceValues.append([])
				for dataDict in groupedDataSets[groupName]:
					value = float(dataDict[fieldName])
					traceValues[-1].append(value)
					if value > maxValue:
						maxValue = value
					elif value < minValue:
						minValue = value
	except ValueError:
		layout['title'] = "Error: Can't plot non-numeric data on a numeric axis."
		return [dcc.Graph(id=GRAPH_ID, figure=go.Figure(layout=layout), config=graphConfig)] # empty graph

	traceNames = [
		fieldName + groupName
		for fieldName in chosenDataFields
		for groupName in groupedDataSets
		]

	# layout['margin']['l'] = 5*max(len(s) for s in traceNames)
	# layout['margin']['l'] = 80 + 5*max(0,max(len(s) for s in traceNames)-10)

	if graphType == 'Histogram':

		for i,trace in enumerate(traceValues):
			if len(trace) < 2:
				del traceValues[i] # can't plot the density of a single variable without errors
		
		if tuningSliderValue is None or tuningSliderValue < MIN_BINSIZE or tuningSliderValue > MAX_BINSIZE:
			tuningSliderValue = 1
		try:
			graphFigure = ff.create_distplot(
				traceValues, traceNames,
				show_curve=False, show_rug=False, bin_size=tuningSliderValue,
				)
		except Exception as e:
			layout['title'] = "Error: " + str(e) # show error message in graph title
			return [dcc.Graph(id=GRAPH_ID, figure=go.Figure(layout=layout), config=graphConfig)] # empty graph

		if showDataBoolean:
			for i,trace in enumerate(graphFigure.data):
				trace['opacity'] = 0.6
				trace['marker']['color'] = PLOTLY_DEFAULT_COLORS[i % len(PLOTLY_DEFAULT_COLORS)]
		else:
			for trace in graphFigure.data:
				trace['marker']['color'] = 'rgba(0,0,0,0)'
		
		ridgelineFigure = plotlyTools.make_subplots(
			rows=len(traceValues),
			cols=1,
			specs=[[{}] for i in range(len(traceValues))],
			shared_xaxes=True, 
			shared_yaxes=True,
			vertical_spacing=0,
			)
		for i,trace in enumerate(reversed(graphFigure.data)):
			ridgelineFigure.append_trace(trace, i+1, 1)

		# for name,values in zip(reversed(traceNames), reversed(traceValues)): #TEMP
		# 	print(name, np.histogram(values, bins=tuningSliderValue, density=True), file=sys.stderr) #TEMP

		#TODO fix drawing instructions
		# layout['showlegend'] = True
		layout['xaxis']['title'] = str(chosenDataFields)[1:-1].replace("'","")
		layout['yaxis']['hoverformat'] = '.3f'
		layout['yaxis']['showticklabels'] = False
		layout['yaxis']['ticks'] = ''
		layout['yaxis']['title'] = ''
		ridgeLayout = ridgelineFigure['layout']
		for key,value in ridgeLayout.items():
			if len(key) >= 5 and (key[:5] == "xaxis" or key[:5] == "yaxis"):
				for k,v in layout[key[:5]].items():
					value[k] = v
		# from pprint import pprint #TEMP
		# pprint(graphFigure['data'], sys.stderr) #TEMP
		_annotations = []
		for i in range(len(traceNames)):
			_histoMax = np.histogram(traceValues[len(traceValues)-i-1], bins=tuningSliderValue, density=True)[0][0]
			_annotations.append(dict(
				xref='paper',
				xanchor='right',
				x=-0.01,
				yref='y'+(str(i+1) if (i > 0) else ''),
				y=0.6*_histoMax*10/tuningSliderValue,
				text=traceNames[len(traceNames)-i-1],
				font=dict(size=14, family='Arial'),
				showarrow=False,
				))
		layout['annotations'] = _annotations
		# print(ridgeLayout, file=sys.stderr) #TEMP
		del layout['xaxis']
		del layout['yaxis']
		ridgeLayout.update(layout)
		return [
			dcc.Graph(id=GRAPH_ID, figure=ridgelineFigure, config=graphConfig)
			]

	if graphType == 'Density Plot':

		for i,trace in enumerate(traceValues):
			if len(trace) < 2:
				del traceValues[i] # can't plot the density of a single variable without errors
		
		if tuningSliderValue is None or tuningSliderValue < 0 or tuningSliderValue >= len(DENSITY_CURVE_TYPES):
			tuningSliderValue = 0
		try:
			graphFigure = ff.create_distplot(
				traceValues, traceNames,
				show_hist=False, show_rug=False, curve_type=DENSITY_CURVE_TYPES[int(tuningSliderValue)],
				)
		except Exception as e:
			layout['title'] = "Error: " + str(e) # show error message in graph title
			return [dcc.Graph(id=GRAPH_ID, figure=go.Figure(layout=layout), config=graphConfig)] # empty graph

		if showDataBoolean:
			for i,trace in enumerate(graphFigure.data):
				trace['fill'] = 'tozeroy'
				trace['marker']['color'] = PLOTLY_DEFAULT_COLORS[i % len(PLOTLY_DEFAULT_COLORS)]
		else:
			for trace in graphFigure.data:
				trace['marker']['color'] = 'rgba(0,0,0,0)'
				trace['fillcolor'] = 'rgba(0,0,0,0)'
		
		ridgelineFigure = plotlyTools.make_subplots(
			rows=len(traceValues),
			cols=1,
			specs=[[{}] for i in range(len(traceValues))],
			shared_xaxes=True, 
			shared_yaxes=True,
			vertical_spacing=0,
			)
		for i,trace in enumerate(reversed(graphFigure.data)):
			ridgelineFigure.append_trace(trace, i+1, 1)

		layout['xaxis']['title'] = str(chosenDataFields)[1:-1].replace("'","")
		layout['yaxis']['hoverformat'] = '.3f'
		layout['yaxis']['showticklabels'] = False
		layout['yaxis']['ticks'] = ''
		layout['yaxis']['title'] = ''
		ridgeLayout = ridgelineFigure['layout']
		for key,value in ridgeLayout.items():
			if len(key) >= 5 and (key[:5] == "xaxis" or key[:5] == "yaxis"):
				for k,v in layout[key[:5]].items():
					value[k] = v
		layout['annotations'] = [
			dict(
				xref='paper',
				xanchor='right',
				x=-0.01,
				yref='y'+(str(i+1) if (i > 0) else ''),
				# possible speed improvement: if graphFigure.data[len(traceNames)-i-1]['y'] is sorted, can use [-1] instead of max()
				y=0.5*max(graphFigure.data[len(traceNames)-i-1]['y']), 
				text=traceNames[len(traceNames)-i-1],
				font=dict(size=14, family='Arial'),
				showarrow=False,
				)
			for i in range(len(traceNames))
			]
		del layout['xaxis']
		del layout['yaxis']
		ridgeLayout.update(layout)
		return [
			dcc.Graph(id=GRAPH_ID, figure=ridgelineFigure, config=graphConfig)
			]

	if graphType == 'Violin Plot':

		traces = [
			dict(
				type='violin',
				name=tName,
				x=values,
				opacity=0.6,
				side='both', 
				bandwidth=tuningSliderValue,
				)
			for tName,values in zip(traceNames,traceValues)
			]

		if showDataBoolean:
			for i,trace in enumerate(traces):
				trace['fillcolor'] = PLOTLY_DEFAULT_COLORS[i % len(PLOTLY_DEFAULT_COLORS)]
				trace['line'] = dict(color="black")
		else:
			for trace in traces:
				trace['fillcolor'] = 'rgba(0,0,0,0)'
				trace['line'] = dict(color='rgba(0,0,0,0)')

		layout['yaxis']['title'] = ''
		layout['xaxis']['title'] = str(chosenDataFields)[1:-1].replace("'","")
		# layout['margin']['l'] = 140

	elif graphType == 'Table':

		if tuningSliderValue is None or tuningSliderValue >= len(TABLEINFO_CHOICES) or tuningSliderValue < 0:
			tuningSliderValue = 0
		tableType = TABLEINFO_CHOICES[int(tuningSliderValue)]

		tableHeaders = ['']
		tableHolder = []
		tableNumber = []
		tableAverage = []
		tableStd = []
		tableError = []
		tableMedian = []
		tableMode = []
		tableRange = []
		tableMinimum = []
		tableTrimean = []
		tableMaximum = []
		tableSkew = []
		tableKurtosis = []

		if tableType == "Basic Parametric":
			categories = [["N", "Minimum", "Mean", "Standard Deviation", "Median", "Maximum"]]
			thingsToZip = [tableNumber, tableMinimum, tableAverage, tableStd, tableMedian, tableMaximum]
		elif tableType == "Complete Parametric":
			categories = [["N", "Minimum", "Mean", "Standard Deviation", "Median", "Skewness", "Kurtosis", "Maximum"]]
			thingsToZip = [tableNumber, tableMinimum, tableAverage, tableStd, tableMedian, tableSkew, tableKurtosis, tableMaximum]
		elif tableType == "Basic Nonparametric":
			categories = [["N", "Minimum", "Trimean", "Standard Deviation", "Maximum"]]
			thingsToZip = [tableNumber, tableMinimum, tableTrimean, tableStd, tableMaximum]
		elif tableType == "Complete Nonparametric":
			categories = [["N", "Minimum", "Trimean", "Standard Deviation", "Median", "Skewness", "Kurtosis", "Maximum"]]
			thingsToZip = [tableNumber, tableMinimum, tableTrimean, tableStd, tableMedian, tableSkew, tableKurtosis, tableMaximum]

		for name in traceNames:
			tableHeaders.append(name)

		for row in traceValues:
			tableNumber.append(len(row))
			tableTrimean.append(round(scipyStats.trim_mean(row, 0.1), 3)) #TODO decide how much to trim
			tableAverage.append(round(sum(row)/len(row),3))
			tableStd.append(round(np.std(row)/np.sqrt(len(row)),3))
			tableError.append(round(scipyStats.sem(row),3))
			tableMedian.append(round(np.median(row),3))
			tableMode.append(scipyStats.mode(row)[0][0])
			tableMinimum.append(min(row))
			tableMaximum.append(max(row))
			tableRange.append(round(max(row)-min(row),3))
			tableSkew.append(round(scipyStats.skew(row),3))
			tableKurtosis.append(round(scipyStats.kurtosis(row),3))

		tableHolder.append(list(map(list, zip(*thingsToZip))))
		for e in tableHolder[0]:
			categories.append(e)

		# convert the data being plotted into numbers
		print(tableHeaders)
		print(traceValues)
		print(categories)
		return [
			# TODO: don't display graph but only the settings buttons & the slider keeps going back to Basic Parametric
			# dcc.Graph(id=GRAPH_ID, figure=go.Figure(data=traces, layout=layout), style={'width': '0', 'height' : '0'}, config=graphConfig),
			html.Div(className="frame",children=[
				html.Table(className="table-format",
			   		children=[
				   		html.Thead(
					   		html.Tr(
						   		children=[html.Th(col) for col in tableHeaders]
					   		)
				   		),
				   		html.Tbody(className="table-body",
			   				children=[
								html.Td(
									children=[html.Tr(data) for data in th]
								)
							for th in categories]
				   			)
			   			])
				])

		]


	elif graphType == 'Box Plot':

		traces = [
			go.Box(
				name=tName,
				x=values,
				opacity=0.6,
				notched=isToggledOn(boxPlotNotch),
				boxpoints="outliers" if isToggledOn(boxPlotOutliers) else False,
				boxmean=isToggledOn(boxPlotMean),
				)
			for tName,values in zip(traceNames,traceValues)
			]

		if showDataBoolean:
			for i,trace in enumerate(traces):
				trace['fillcolor'] = PLOTLY_DEFAULT_COLORS[i % len(PLOTLY_DEFAULT_COLORS)]
				trace['marker'] = dict(color="black")
		else:
			for trace in traces:
				trace['fillcolor'] = 'rgba(0,0,0,0)'
				trace['marker'] = dict(color='rgba(0,0,0,0)')

		layout['yaxis']['title'] = ''
		layout['xaxis']['title'] = str(chosenDataFields)[1:-1].replace("'","")

	if tuningSliderValue is None or tuningSliderValue < 0 or tuningSliderValue >= len(BARDOTPLOTERROR_CHOICES):
		tuningSliderValue = 0
	errorBarType = BARDOTPLOTERROR_CHOICES[len(BARDOTPLOTERROR_CHOICES)-1-int(tuningSliderValue)]

	if errorBarType == "± Standard Error":
		def getError(values):
			return np.std(values)/np.sqrt(len(values))
	elif errorBarType == "± Standard Deviation":
		def getError(values):
			return np.std(values)/2
	elif errorBarType == "± 95% Confidence Interval":
		def getError(values):
			return 1.96*np.std(values)/np.sqrt(len(values))

	if graphType == 'Dot Plot':

		# dummy traces to avoid rendering errors
		traces = [
			dict(
				visible='legendonly',
				showlegend=False,
				y=[0.0 for i in range(len(values))],
				x=['0.0' for i in range(len(values))],
				)
			for values in traceValues
			]

		# real traces
		traces += [
			go.Scatter(
				name=tName,
				x=[sum(values)/len(values)],
				y=[tName],
				# opacity=0.6,
				error_x=dict(
				    thickness = 4.0,
					type='data',
					array=[getError(values)],
					color=PLOTLY_DEFAULT_COLORS[i % len(PLOTLY_DEFAULT_COLORS)],
					),
				# width=0.01,
				marker=dict(
					size = 10,
					color=PLOTLY_DEFAULT_COLORS[i % len(PLOTLY_DEFAULT_COLORS)],
					),
				# orientation='h',
				)

			for i,(tName,values) in enumerate(zip(traceNames,traceValues))
			]

		if not showDataBoolean:
			for i in range(len(traceValues), 2*len(traceValues)):
				traces[i]['marker']['color'] = 'rgba(0,0,0,0)'
				traces[i]['error_x']['color'] = 'rgba(0,0,0,0)'

		# layout['margin']['l'] = 140
		layout['yaxis']['title'] = ""
		layout['yaxis']['type'] = 'category'
		layout['xaxis']['title'] = str(chosenDataFields)[1:-1].replace("'","")
		layout['yaxis']['ticklen'] = 0
		layout['xaxis']['autorange'] = False
		layout['xaxis']['range'] = [minValue, maxValue]
		layout['yaxis']['showgrid'] = True
		layout['yaxis']['gridwidth'] = 1.0
		layout['yaxis']['gridcolor'] = '#e6eaf2'


	elif graphType == 'Bar Plot':

		traces = [
			dict(
				visible='legendonly',
				showlegend=False,
				y=[0.0 for i in range(len(values))],
				x=['0.0' for i in range(len(values))],
				)
			for values in traceValues
			]

		traces += [
			go.Bar(
				name=tName,
				x=[sum(values)/len(values)],
				y=[tName],
				opacity=0.6,
				marker=dict(
					color=PLOTLY_DEFAULT_COLORS[i % len(PLOTLY_DEFAULT_COLORS)],
					),
				error_x=dict(
					type='data',
					#color = 'black',
					thickness = 2.75,
					width = 5,
					array=[getError(values)],
					),
				orientation='h',
				)

			for i,(tName,values) in enumerate(zip(traceNames,traceValues))
			]

		if not showDataBoolean:
			for i in range(len(traceValues), 2*len(traceValues)):
				traces[i]['marker']['color'] = 'rgba(0,0,0,0)'
				traces[i]['error_x']['color'] = 'rgba(0,0,0,0)'

		# layout['margin']['l'] = 140
		layout['yaxis']['title'] = ""
		layout['xaxis']['title'] = str(chosenDataFields)[1:-1].replace("'","")
		layout['yaxis']['type'] = 'category'
		layout['yaxis']['ticklen'] = 0
		layout['xaxis']['autorange'] = False
		layout['xaxis']['range'] = [minValue, maxValue]

	return [dcc.Graph(id=GRAPH_ID, figure=go.Figure(data=traces, layout=layout), config=graphConfig)]

@app.callback(
	Output('graph_container', 'style'),
	[Input("showDataIndicator", "children")],
	)
def updateGraphCss(showDataIndicator:str):
	return dict(
		position="relative",
		zIndex="-1" if (showDataIndicator == "false") else "1",
		)

@app.callback(
	Output("showDataIndicator", "children"),
	[Input("showDataButton", "n_clicks")],
	[State("showDataIndicator", "children")],
	)
def updateShowDataIndicator(nClicks:int, showDataIndicator:str):
	if nClicks == 0:
		return "false"
	else:
		return "true" if showDataIndicator=="false" else "false"


if __name__ == '__main__': # if using the local machine as the web server

	app.run_server(debug=True)
