#!/usr/bin/env python
from glob import glob
import ast
from parsl_scheduling_simulator.util import *
import argparse
parser = argparse.ArgumentParser(description="Calibration Argument Parser")
parser.add_argument("-e", "--experiments", nargs='+', type=str, help="Path to workflow files to run for experiment", required=True)
parser.add_argument("-a", "--args", type=str, help="Reference JSON args", required=True)
args=parser.parse_args()
def parseCalibration(path):
	path=path.replace("\\","/")
	name=path.split("/")[-1]
	with open(path) as f:
		content=f.read()
	content=content.split("\n")
	for line in content:
		if len(line)>0 and line[0]=='{':
			return ast.literal_eval(raw_to_ast(line)),name
	print("error on file",path)
	print(content)
	return None,name

def distance(ref,args):
	resl=0
	if(args is None):
		return float('inf')
	for parameter in args.keys():
		resl+=abs(relative_error(parseDoubleUnited(ref[parameter]),parseDoubleUnited(args[parameter])))
	return resl
	
experiments = []
for experiment in args.experiments:
	if '*' in experiment or '?' in experiment:
		experiments += glob(experiment)
	else:
		experiments.append(experiment)
ref=ast.literal_eval(raw_to_ast(args.args))

for i in range(len(experiments)):
	experiments[i]=parseCalibration(experiments[i])
	experiments[i]=distance(ref,experiments[i][0]),experiments[i][1]
for i in sorted(experiments,key = lambda x: x[0]):
	print(i)