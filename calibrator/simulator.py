#!/usr/bin/env python
import simcal as sc
import copy
import json
from typing import Any
from parsl_scheduling_simulator.alg_manager import *
import re
from parsl_scheduling_simulator.util import *
from parsl_scheduling_simulator.simulator import *
import sys
# There are 3 different simulators for the 3 different situations we will run them in
# SchedulingSimulator is for making scheduling decisions.  It is given the state parts of the json (ie the "workflow" sub object) at each run and is initialized with a calibration and a set of scheduling algorithms, and a metric to use.  Run will then run the simulator on that state with that calibration for each algorithm and return the algorithm(s) with the lowest score according to the metric.  THIS VERSION IS NOT INTENDED TO BE RAN WITH SIMCAL

# CalibrationSimulator is for offline calibration of the simulator.  It is given a calibration at each run and is initialized with a loss function to use and a list of "ground truth" executions to use.  These include the workflow specs and the schedule used for each groundtruth run as well as the expected output.  Run will then run the simulator for each execution in the ground truth and return a scalar using the loss function

# ErrorCorrectionSimulator is for online error correction of the simulator.  It is given a calibration at each run and is initialized with a loss function to use and the state of a single partial execution, and a scheduling algorithm.  Run will then run the simulator using that state and return a scalar using the loss function

	
if __name__ == "__main__":
	class ParseException(Exception):
		pass
	import sys
	import argparse
	import traceback
	import parsl_scheduling_simulator.metrics as metrics
	import parsl_scheduling_simulator.loss as losses
	from glob import glob
	
	try:
		sub=sys.argv[1].lower()
		if "scheduling".startswith(sub) or sub == "schedule":
			sys.argv[0]+=" "+sys.argv[1]
			del sys.argv[1]
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
			try:
				args=parser.parse_args()
				if(args.calibration):
					calibration=ast.literal_eval(raw_to_ast(lineargs.calibration))
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
				ret=simulator(state)
				print(ret)
			except ParseException:
				pass
			except Exception:
				print(traceback.format_exc())
				
		elif "calibration".startswith(sub):
			del sys.argv[1]
			sys.argv[0]+=" "+sub
			parser = argparse.ArgumentParser(description="Calibration Argument Parser")
			parser.add_argument("-c", "--calibration", type=str, help="Calibration JSON as string", required=False)
			parser.add_argument("-s", "--state", type=str, help="State JSON as string", required=False)
			parser.add_argument("-p", "--simulator_path", type=str, help="Path to the simulator", required=True)
			parser.add_argument("-t", "--template", type=str, help="Template JSON as string", required=True)
			parser.add_argument("-e", "--experiments", nargs='+', type=str, help="Path to workflow files to run for experiment", required=True)
			parser.add_argument("-l", "--loss", type=str, help="Loss Function to use", default='relative_makespan_loss')
			parser.add_argument("-n", "--num_threads", type=int, help="Number of threads", required=False)
			parser.add_argument("-a", "--aggregator", type=str, help="Loss aggregator to use", default='avg_aggregator')
			parser.add_argument("-tss", "--task_selection_scheme", type=str, help="Task selection scheme", required=True)
			parser.add_argument("-wss", "--worker_selection_scheme", type=str, help="Worker selection scheme", required=True)
			parser.add_argument("-nss", "--num_cores_selection_scheme", type=str, help="Number of cores selection scheme", required=True)
			parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode", required=False)
			try:
				args=parser.parse_args()
				if(args.calibration):
					calibration=ast.literal_eval(raw_to_ast(lineargs.calibration))
				else:
					calibration={}
				
				try: 
					template=load_json(args.template)
				except FileNotFoundError:
					try:
						template=json.loads(args.template)
					except:
						print("Template provided is not a path or a json object",file=sys.stderr)
						raise
				if hasattr(losses, args.loss):  
					loss = getattr(losses, args.loss)  # Get the function
				else:
					print(f"Error: loss function {args.loss} does not exist")
					raise ParseException()
				if not args.num_threads or args.num_threads==1:
					coordinator=None
				else:
					from simcal.coordinators import ThreadPool
					coordinator=ThreadPool(args.num_threads)	
				if hasattr(losses, args.aggregator):  
					aggregator = getattr(losses, args.aggregator)  # Get the function
				else:
					print(f"Error: loss aggregator {args.aggregator} does not exist")
					raise ParseException()
				loss = 	losses.Loss(loss,aggregator)
				
				if args.verbose:
					verbosity = ["sim_error","parse_error"]
				else:
					verbosity = []
				
				experiments = []
				for experiment in args.experiments:
					if '*' in experiment or '?' in experiment:
						experiments += glob(experiment)
					else:
						experiments.append(experiment)
				for i in range(len(experiments)):
					experiments[i]=Experiment(experiments[i])
				
				alg=SchedulingAlg(args.task_selection_scheme,args.worker_selection_scheme,args.num_cores_selection_scheme)	
				simulator=CalibrationSimulator(args.simulator_path,template,experiments,alg,loss,verbosity = verbosity, coordinator=coordinator)
				params=simulator.dictToTagged(calibration)
				ret=simulator(params)
				print(ret)
			except ParseException:
				pass
			except Exception:
				print(traceback.format_exc())
		elif "errorcorrection".startswith(sub) or "errorcorrection".startswith(sub) or sub == "ec":
			print("error correction not yet implemented",file=sys.stderr)
		elif "synthetic".startswith(sub):
			sys.argv[0]+=" "+sys.argv[1]
			del sys.argv[1]
			parser = argparse.ArgumentParser(description="Simulation Argument Parser")
			parser.add_argument("-c", "--calibration", type=str, help="Calibration JSON as string", required=False)
			parser.add_argument("-s", "--state", type=str, help="State JSON as string", required=False)
			parser.add_argument("-p", "--simulator_path", type=str, help="Path to the simulator", required=True)
			parser.add_argument("-t", "--template", type=str, help="Template JSON as string", required=True)
			parser.add_argument("-e", "--experiments", nargs='+', type=str, help="Path to workflow files to run for experiment", required=True)
			parser.add_argument("-n", "--num_threads", type=int, help="Number of threads", required=False)
			parser.add_argument("-tss", "--task_selection_scheme", type=str, help="Task selection scheme", required=True)
			parser.add_argument("-wss", "--worker_selection_scheme", type=str, help="Worker selection scheme", required=True)
			parser.add_argument("-nss", "--num_cores_selection_scheme", type=str, help="Number of cores selection scheme", required=True)
			parser.add_argument("-o", "--output_dir", type=str, help="Directory to dump new synthetic files into", required=True)
			parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode", required=False)
			try:
				args=parser.parse_args()
				if(args.calibration):
					calibration=ast.literal_eval(raw_to_ast(lineargs.calibration))
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
				if not args.num_threads or args.num_threads==1:
					coordinator=sc.coordinators.Base()
				else:
					from simcal.coordinators import ThreadPool
					coordinator=ThreadPool(args.num_threads)
				if args.verbose:
					verbosity = ["sim_error","parse_error"]
				else:
					verbosity = []
				experiments = []
				for experiment in args.experiments:
					if '*' in experiment or '?' in experiment:
						experiments += glob(experiment)
					else:
						experiments.append(experiment)
				for i in range(len(experiments)):
					experiments[i]=Experiment(experiments[i])
				alg=SchedulingAlg(args.task_selection_scheme,args.worker_selection_scheme,args.num_cores_selection_scheme)	
				simulator=Simulator(args.simulator_path,template,verbosity = verbosity)
				def synthetic_run(sim,alg,exp,state,cal,output_dir):
					json_args=alg.modifyJSON(template)
					json_args=sim.modifyJSON(json_args,exp.experiment_params)
					json_args=sim.modifyJSON(json_args,state)
					json_args=sim.modifyJSON(json_args,cal)
					output=sim(json_args)
					file=json_args["workflow"]["file"]
					json_file=load_json(file)
					file.replace("\\","/")
					#replace content of json file
					json_file["runtimeSystem"]["name"]="Synthetic"
					json_file["runtimeSystem"]["version"]="1.0"
					json_file["runtimeSystem"]["url"]=""
					json_file["name"]="synthetic-"+json_file["name"]
					json_file["workflow"]["execution"]["makespanInSeconds"]=output["finish_date"]
					for task in json_file["workflow"]["execution"]["tasks"]:
						if task["id"] in output["task_completions"]:
							output_task=output["task_completions"][task["id"]]
							task["runtimeInSeconds"]=output_task["end_date"]-output_task["start_date"]
							task["machines"]=[output_task["worker"]]
					with open(output_dir+"/synthetic_"+json_args["workflow"]["file"].split("/")[-1],'w') as synth_file:
						json.dump(json_file,synth_file)

				for exp in experiments:
					coordinator.allocate(synthetic_run, (simulator, alg, exp,state , calibration,args.output_dir))
					results = coordinator.collect()
				results = coordinator.await_all()
			except ParseException:
				pass
			except Exception:
				print(traceback.format_exc(),file=sys.stderr)
		else:
			print(f"subcommand \"{sys.argv[1]}\" not recognized",file=sys.stderr)
			raise
	except Exception:
		print(f"Usage: {sys.argv[0]} <scheduling | calibration | error_correction | synthetic> ...\n\t Specify a sub command for the usage of that subcommand",file=sys.stderr)