#!/usr/bin/env python
import os
import requests
import json
import re
import xlrd
import plotly
from plotly.graph_objs import *

STARTING_ROW = 4  # skip first 4 rows
salariesdict = dict()
traced_roll = []
def populate_cgpa_salary_mapping():
	# populate cgpasalary.json only if it doesn't exist
	if not os.path.isfile('./cgpasalary.json'):
		cgpasalary = {}
		workbook = xlrd.open_workbook('./achievers.xlsx')
		worksheet = workbook.sheet_by_name('List of Students ')
		num_cols = worksheet.ncols
		num_rows = worksheet.nrows

		for row_index in range(STARTING_ROW, 351):
			try:
				companies = worksheet.cell_value(row_index, 7).encode('ascii', 'ignore')
				print companies
				roll = int(worksheet.cell_value(row_index, 8))
				name = worksheet.cell_value(row_index, 9).encode('ascii', 'ignore')
				salaries = get_salaries(companies)
				cgpa = get_cgpa(roll)
				extra_text = name.title() + '<br>' + companies.title() + '<br>' + str(salaries)
				print roll, name, salaries, cgpa, extra_text
				cgpasalary[roll] = [extra_text, cgpa, salaries]
			except ValueError as e:
				print row_index, e
		print 'cgpasalary is', cgpasalary
		with open('./cgpasalary.json', 'w') as outfile:
			json.dump(cgpasalary, outfile, indent=4)
	cgpasalary = json.load(open('./cgpasalary.json', 'r'))
	return cgpasalary


def make_graph(cgpasalary):
	legends = ['tech mahindra', 'ntt data', 'mindtree', 'caerus', 'cgi', 'virtusa', 'cyient', 'other']
	colors = ['red', 'blue', 'yellow', 'green', 'brown', 'pink', 'orange', 'black']
	traces = []
	for legend, color in zip(legends, colors):
		traces.append(make_trace(legend, color, cgpasalary))

	plotly.offline.plot({
		"data": traces,
		"layout": Layout(title="GITAM University Placements: CGPA vs Salaries",
		xaxis=dict(title='CGPA'), yaxis=dict(title='Salaries in LPA'))
	})

def make_trace(legend, legend_color, cgpasalary):
	x_data, y_data, extra_text = [], [], []
	lets = 0x12
	global traced_roll
	for roll in cgpasalary:
		if roll not in traced_roll:  # each roll will be traced only once
			values = cgpasalary[roll]
			highest_ctc_company = values[2][0][1]
			if legend == 'other' or highest_ctc_company == legend.upper():
				cgpa = values[1]
				highest_ctc = values[2][0][0]
				x_data.append(cgpa)
				y_data.append(highest_ctc)
				extra_text.append(values[0])
				traced_roll.append(roll)

	data = {'x': x_data, 'y': y_data}
	trace = Scattergl(
						data, mode='markers',
						marker=Marker(
							color=legend_color,
							symbol='diamond',
							size=8
						),
						text=extra_text,
						name='{} ({})'.format(legend.upper(), len(x_data))
					)
	return trace


def get_salaries(companies):
	companies = companies.split('+')
	print companies
	companies = map(str.strip, companies)
	salaries = [(salariesdict[company], company) for company in companies]
	salaries.sort(reverse=True)
	return salaries


# __VIEWSTATE and __EVENTVALIDATION values can be found from url's html source

def get_cgpa(roll):
	url = "https://doeresults.gitam.edu/onlineresults/pages/Newgrdcrdinput1.aspx"

	payload = ("__VIEWSTATE=%2FwEPDwULLTE3MTAzMDk3NzUPZBYCAgMPZBYCAgcPDxYCHgRUZXh0ZWRkZKKjA%2F8YeuWfLRpWAZ2J1Qp0eXCJ"
	"&__EVENTVALIDATION=%2FwEWFQKj%2FsbfBgLnsLO%2BDQLIk%2BgdAsmT6B0CypPoHQLLk%2BgdAsyT6B0CzZPoHQLOk%2BgdAt%2BT6B0C0JPoHQLIk6geAsiTpB4CyJOgHgLIk5weAsiTmB4CyJOUHgKL%2B46CBgKM54rGBgK7q7GGCALWlM%2BbAsr6TbZa4e1ProM8biQQXbC9%2FwS2"
	"&cbosem=7"
	"&txtreg={}"
	"&Button1=Get+Result").format(roll)

	headers = {'content-type': "application/x-www-form-urlencoded", }

	response = requests.request("POST", url, data=payload, headers=headers)
	print(response.text)

	cgpa_regex = re.compile('<span id="lblcgpa">(.*)</span>')
	cgpa = cgpa_regex.search(response.text).group(1)
	print 'cgpa is ', cgpa
	return cgpa

if __name__ == '__main__':
	global salariesdict
	salariesdict = json.load(open('ctc.json', 'r'))
	cgpasalary = populate_cgpa_salary_mapping()
	make_graph(cgpasalary)
