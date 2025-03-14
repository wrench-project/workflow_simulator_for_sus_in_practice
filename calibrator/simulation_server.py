#!/usr/bin/env python
import simcal as sc
from parsl_scheduling_simulator.util import *
from parsl_scheduling_simulator.simulator import SchedulingSimulator
from parsl_scheduling_simulator.simulation_server import SimulationServer
import multiprocessing
import time

if __name__ == "__main__":
	class ParseException(Exception):
		pass
	import sys
	import argparse
	import traceback
	import parsl_scheduling_simulator.metrics as metrics
	import parsl_scheduling_simulator.loss as losses
	from glob import glob
	from parsl_scheduling_simulator.alg_manager import *
	parser = argparse.ArgumentParser(description="Simulation Argument Parser")
	parser.add_argument("-c", "--calibration", type=str, help="Calibration JSON as string", required=False)
	parser.add_argument("-s", "--state", type=str, help="State JSON as string")
	parser.add_argument("-s2", "--state2", type=str, help="State JSON to transition to as string")
	parser.add_argument("-p", "--simulator_path", type=str, help="Path to the simulator", required=True)
	parser.add_argument("-t", "--template", type=str, help="Template JSON as string", required=True)
	parser.add_argument("-m", "--metric", type=str, help="Metric to use", required=True)
	parser.add_argument("-n", "--num_threads", type=int, help="Number of threads", required=False)
	parser.add_argument("-tss", "--task_selection_schemes", nargs='+', type=str, help="Task selection schemes", required=True)
	parser.add_argument("-wss", "--worker_selection_schemes", nargs='+', type=str, help="Worker selection schemes", required=True)
	parser.add_argument("-nss", "--num_cores_selection_schemes", nargs='+', type=str, help="Number of cores selection schemes", required=True)
	parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode", required=False)
	args=parser.parse_args()
	if(args.calibration):
		calibration=json.loads(args.calibration)
	else:
		calibration={}
	if(args.state is not None):
		state=json.loads(args.state)
	else:
		state={}	
	if(args.state2 is not None):
		state2=json.loads(args.state2)
	else:
		state2={}	
	try: 
		template=load_json(args.template)
	except FileNotFoundError:
		try:
			template=json.loads(args.template)
		except:
			print("Template provided is not a path or a json object",file=sys.stderr)
			raise
	if hasattr(metrics, args.metric):  
		metric = getattr(metrics, args.metric)  # Get the function
	else:
		print(f"Error: metric {args.metric} does not exist")
		raise ParseException()
	if not args.num_threads or args.num_threads==1:
		coordinator=None
	else:
		from simcal.coordinators import ThreadPool
		coordinator=ThreadPool(args.num_threads)
	if args.verbose:
		verbosity = ["sim_error","parse_error"]
	else:
		verbosity = []
	algs=AlgManager(args.task_selection_schemes,args.worker_selection_schemes,args.num_cores_selection_schemes)
	
	simulator=SchedulingSimulator(args.simulator_path,template,calibration,algs,metric,coordinator,verbosity = verbosity)
	server=SimulationServer(simulator)
	print("should be blocking")
	ret=server(state)
	print(ret,server.shared_data["state"])
	print("should be nonblocking")
	ret=server(state2)
	print(ret,server.shared_data["state"])
	time.sleep(5) 
	print("should be blocking")
	ret=server.stop()
	
	print("should be final state")
	print(ret,server.shared_data["state"])