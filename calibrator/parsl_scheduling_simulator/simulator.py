#!/usr/bin/env python
import simcal as sc
import copy
import json
from typing import Any
from .alg_manager import *
import re
from .util import *
import sys
# There are 3 different simulators for the 3 different situations we will run them in
# SchedulingSimulator is for making scheduling decisions.  It is given the state parts of the json (ie the "workflow" sub object) at each run and is initialized with a calibration and a set of scheduling algorithms, and a metric to use.  Run will then run the simulator on that state with that calibration for each algorithm and return the algorithm(s) with the lowest score according to the metric.  THIS VERSION IS NOT INTENDED TO BE RAN WITH SIMCAL

# CalibrationSimulator is for offline calibration of the simulator.  It is given a calibration at each run and is initialized with a loss function to use and a list of "ground truth" executions to use.  These include the workflow specs and the schedule used for each groundtruth run as well as the expected output.  Run will then run the simulator for each execution in the ground truth and return a scalar using the loss function

# ErrorCorrectionSimulator is for online error correction of the simulator.  It is given a calibration at each run and is initialized with a loss function to use and the state of a single partial execution, and a scheduling algorithm.  Run will then run the simulator using that state and return a scalar using the loss function
class Simulator(sc.Simulator):
	def __init__(self,simulator_path,json_template,verbosity = None):
		self.verbosity=[]
		if verbosity:
			self.verbosity=verbosity
		self.simulator_path=simulator_path
		self.json_template=json_template
	def modifyJSON(self,json_template,mod):
		if not isinstance(json_template, dict) or not isinstance(mod, dict):
			return copy.deepcopy(mod)  # Override A's value with B's if B is not a dict

		merged = copy.deepcopy(json_template)  # Create a copy of A to preserve immutability
		for key, value in mod.items():
			if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
				merged[key] = self.modifyJSON(merged[key], value)  # Recursive merge
			else:
				merged[key] = copy.deepcopy(value)  # Override with B's value

		return merged
	def exec(self,json_args,env):
		for worker in json_args["platform"]["workers"].values():
			worker["active"]=False
		json_file=load_json(json_args["workflow"]["file"])
		for machine in json_file["workflow"]["execution"]["machines"]:
			json_args["platform"]["workers"][machine["nodeName"]]["active"]=True
		output = env.bash(self.simulator_path,("--json_input",json.dumps(json_args)))
		try:
			json_output=json.loads(output[0])
		except:
			if "parse_error" in self.verbosity:
				print(json.dumps(json_args),file=sys.stderr)
				print(output,file=sys.stderr)
			raise
		if len(output[1].split("\n"))>3 and "sim_error" in self.verbosity:
			print(json.dumps(json_args),file=sys.stderr)
			print(output,file=sys.stderr)
		return json.loads(output[0])
	def run(self,env,json_args):
		return self.exec(json_args,env)
	def dictToTagged(self,calibration,subkey=None):
		if not subkey:
			subkey=[]
		params={}
		for key, value in calibration.items():
			if isinstance(value, dict):
				params |= self.dictToTagged(value,subkey+[key]) 
			else:
				param=sc.parameter.Base()
				json_type=type(value)
				param.set_custom_data({"json_type":json_type,"key":subkey+[key]})
				param_v=sc.parameter.Value(None,value,param)
				params[" ".join(subkey+[key])+ " "+str(value)]=(param_v)
		return params
	def _modifyJSON_tagged_recursive(self,json_copy,metadata,parameter):
		pattern = re.compile(metadata[0])
		for key in json_copy:
			if pattern.match(key):
				matched=True
				if len(metadata)>1:
					self._modifyJSON_tagged_recursive(json_copy[key],metadata[1:],parameter)
				else:
					metadata = parameter.get_parameter().get_custom_data()
					json_type=metadata["json_type"]
					json_copy[key] = json_type(parameter)
	def isSimcalCal(self,cal):
		for key in cal:
			if isinstance(cal[key],sc.parameter.Base):
				return True
		return False
		
	def modifyJSON_tagged(self,json_template,tagged_args):
		json_copy = copy.deepcopy(json_template)
		for parameter in tagged_args:
			metadata = tagged_args[parameter].get_parameter().get_custom_data()
			metadata=metadata["key"]
			self._modifyJSON_tagged_recursive(json_copy,metadata,tagged_args[parameter])
		return json_copy
def _exec(simulator: Simulator, alg,state,stoptime):
	return alg, simulator.supercall({"state":state,"alg":alg},stoptime)
	
class SchedulingSimulator(Simulator):
	def __init__(self,simulator_path,json_template,calibration,algs,metric,coordinator,verbosity = None):
		super().__init__(simulator_path,json_template,verbosity)
		self.algs=algs
		self.metric=metric
		self.calibration=calibration
		self.coordinator=coordinator
		if coordinator is None:
			self.coordinator = sc.coordinators.Base()

	def run(self,env,args):
		
		alg=args["alg"]
		state=args["state"]
		json_args=alg.modifyJSON(self.json_template)
		json_args=self.modifyJSON(json_args,state)
		if(self.isSimcalCal(self.calibration)):
			json_args=self.modifyJSON_tagged(json_args,self.calibration)
		else:
			json_args=self.modifyJSON(json_args,self.calibration)
		output=self.exec(json_args,env)
		return self.metric(output)
		
	def supercall(self, args: Any, stoptime: int | float | None = None) -> str:
		return super().__call__(args,stoptime)
		
	def __call__(self, args: Any, stoptime: int | float | None = None) -> str:
		best=None
		bestScore=None
		for alg in self.algs.asObj():
			self.coordinator.allocate(_exec, (self, alg, args, stoptime))
			results = self.coordinator.collect()
			for current, score in results:
				if score is None:
					continue
				if bestScore is None or score < bestScore:
					best = [current]
					bestScore=score
				elif  score==bestScore:
					best.append(alg)
		results = self.coordinator.await_all()
		for current, score in results:
			if score is None:
				continue
			if bestScore is None or score < bestScore:
				best = [current]
				bestScore=score
			elif  score==bestScore:
				best.append(alg)
				
		return best
class Experiment:
	def __init__(self,experiment_params,ground_truth = None):
		if ground_truth is None: #assume file path was given
			self.initFromFile(experiment_params)
		else:
			self.experiment_params=experiment_params
			self.ground_truth=ground_truth
	
	def initFromFile(self, file):
		self.experiment_params = {"workflow": {"file": file,"done_tasks": [],"ongoing_tasks": [],"interest_tasks": []}}
		json_file=load_json(file)
		self.ground_truth = json_file["workflow"]["execution"]
	def __repr__(self):
		return str(self.experiment_params)
class CalibrationSimulator(Simulator):
	def __init__(self,simulator_path,json_template,experiments,alg, loss ,verbosity = None, allowEmptyExperiments=False, coordinator=None):
		super().__init__(simulator_path,json_template,verbosity)
		self.experiments=experiments
		if not allowEmptyExperiments and (not experiments or len(self.experiments)==0):
			raise ValueError("CalibrationSimulator created without experiments.  If this is intentional pass `allowEmptyExperiments=True`")
		self.loss=loss
		self.alg=alg
		self.coordinator=coordinator
	def run_with_loss(self,json_args,env,ground_truth):
		output=self.exec(json_args,env)
		return self.loss.loss(output,ground_truth)
	def run(self,env,args):
		losses=[]
		for experiment in self.experiments:
			json_args=self.alg.modifyJSON(self.json_template)
			json_args=self.modifyJSON(json_args,experiment.experiment_params)
			json_args=self.modifyJSON_tagged(json_args,args)
			#print(json_args)
			if self.coordinator:
				self.coordinator.allocate(self.run_with_loss,(json_args,env,experiment.ground_truth))
			else:
				output=self.exec(json_args,env)
				losses.append(self.loss.loss(output,experiment.ground_truth))
		if self.coordinator:
			losses = self.coordinator.await_all()
		return self.loss.aggregator(losses)
		
# probably optional with calibrator, just replace losses and experiments
class ErrorCorrectionSimulator(Simulator):
	def __init__(self,simulator_path,json_template,verbosity = None):
		super().__init__(simulator_path,json_template,verbosity)
	
	def run(self,env,args):
		pass
		
	