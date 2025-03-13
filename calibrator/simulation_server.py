#!/usr/bin/env python
import simcal as sc
from util import *
from simulator import SchedulingSimulator
import multiprocessing
import time

class SimulationRunner:
	def __init__(self,shared_data): 
		self.shared_data = shared_data
		self.shared_data["last_state"]=shared_data["state"]
		
	def run(self):
		lastState=self.shared_data["last_state"]
		while self.shared_data["running"] and lastState!=self.shared_data["state"]:
			lastState=self.shared_data["state"]
			self.shared_data["last_state"]=lastState
			self.shared_data["ret"]=self.shared_data["simulator"](lastState)
			
class SimulationServer:
	def __init__(self,simulator):
		self.manager = multiprocessing.Manager()
		self.shared_data = self.manager.dict()  # Shared dictionary for variables
		self.shared_data["simulator"]=simulator
		self.shared_data["running"]=True
		self.shared_data["state"]=None
		self.shared_data["ret"]=None
		self.runner=SimulationRunner(self.shared_data)
		self.process = None

	def __call__(self,state):
		if self.shared_data["ret"] is None:
			return self.start(state)
		else:
			return self.update_state(state)
		
	def start(self,state):
		self.shared_data["running"] = True
		self.shared_data["state"]=state
		self.runner.run()
		ret=self.shared_data["ret"]
		self.update_state(state)
		return ret
		
	def wait(self):
		self.process.join()
		self.process = None
		return self.shared_data["ret"]
		
	def update_state(self, state):
		"""Update the shared value."""
		self.shared_data["state"] = state
		
		if self.process is not None and not self.process.is_alive():
			self.process.join()
			self.process = None
		if self.process is None:
			self.process = multiprocessing.Process(target=self.runner.run)
			self.process.start()
		return 	self.shared_data["ret"]
	def stop(self):
		"""Stop the background process."""
		self.shared_data["running"] = False
		self.process.join()
		self.process = None
		return self.shared_data["ret"]

if __name__ == "__main__":
	class ParseException(Exception):
		pass
	import sys
	import argparse
	import traceback
	import metrics
	import loss as losses
	from glob import glob
	from alg_manager import *
	parser = argparse.ArgumentParser(description="Simulation Argument Parser")
	parser.add_argument("-c", "--calibration", type=str, help="Calibration JSON as string", required=False)
	parser.add_argument("-s", "--state", type=str, help="State JSON as string", required=False)
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
	ret=server({})
	print(ret)
	ret=server(state)
	print(ret)
	ret=server.stop()
	print(ret)