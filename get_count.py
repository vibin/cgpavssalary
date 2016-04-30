import json

companies = dict()
with open('comp.txt', 'r') as infile:
	for line in infile:
		line = line.strip()
		if line:
			companies[line] = companies.get(line, 0) + 1
#print sorted(companies.values())

companies_names = companies.keys()
salaries = [0] * len(companies_names)

json_outp = dict(zip(companies_names, salaries))

with open('ctc.json', 'w') as outfile:
	json.dump(json_outp, outfile, indent=4, sort_keys=True)
	print json_outp

'''
--------------
15 or more
--------------

TECH MAHINDRA, 129
NTT DATA, 51
MINDTREE, 28
CAERUS, 22
CGI, 18
VIRTUSA, 17
CYIENT, 15
OTHERS
'''
