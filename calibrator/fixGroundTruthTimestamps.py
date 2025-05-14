#!/usr/bin/env python
import json
import argparse
from glob import glob
import time
import datetime
parser = argparse.ArgumentParser(description="Calibration Argument Parser")
parser.add_argument("-e", "--experiments", nargs='+', type=str, help="Path to workflow files to run for experiment", required=True)
args=parser.parse_args()
experiments = []
def load_json(path):
	with open(path) as json_file:
		return json.load(json_file)
def save_json(path,data):
	with open(path, 'w') as json_file:
		return json.dump(data,json_file)
for experiment in args.experiments:
	if '*' in experiment or '?' in experiment:
		experiments += glob(experiment)
	else:
		experiments.append(experiment)
for exp in experiments:
	try:
		data=load_json(exp)
		start=float('inf')
		for i in range(len(data["workflow"]["execution"]["tasks"])):
			date=data["workflow"]["execution"]["tasks"][i]["executedAt"]
			date=time.mktime(datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f").timetuple())
			start=min(start,date)
			
		for i in range(len(data["workflow"]["execution"]["tasks"])):
			date=data["workflow"]["execution"]["tasks"][i]["executedAt"]
			date=time.mktime(datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f").timetuple())
			data["workflow"]["execution"]["tasks"][i]["executedAt"]=date-start
		save_json(exp,data)											
	except:
		print("except",exp)