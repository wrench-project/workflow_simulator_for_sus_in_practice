#!/usr/bin/env python

import simcal as sc
from parsl_scheduling_simulator.simulator import *
import time
from datetime import timedelta
class Calibrate:
	calibrators = { 
		"random":sc.calibrators.Random(seed=0),
		"gradient":sc.calibrators.GradientDescent(1,1,seed=0,early_reject_loss=None),#random hyperparameters
		"genetic":sc.calibrators.GeneticAlgorithm(1000,100,0.1,0.1,fitness_noise=0,annealing=True,seed=0,elites=10),#random hyperparameters
		"grid":sc.calibrators.Grid(),
		"skopt.gp":sc.calibrators.ScikitOptimizer(1000,"GP",seed=0),
		"skopt.gbrt":sc.calibrators.ScikitOptimizer(1000,"GBRT",seed=0),
		"skopt.et":sc.calibrators.ScikitOptimizer(1000,"ET",seed=0),
		"skopt.rf":sc.calibrators.ScikitOptimizer(1000,"RF",seed=0),
		"debug":sc.calibrators.Debug()
	
	}
	def __init__(self,simulator,calibrator,threads):
		self.simulator=simulator
		self.calibrator = self.calibrators[calibrator]
		self.param_ranges()
		self.coordinator = sc.coordinators.ThreadPool(pool_size=threads)
	def param_ranges(self):
		self.calibrator.add_param("wms_read_bandwidth", sc.parameters.Exponential(20, 30).
								 format("%lfBps").set_custom_data({"json_type":str,"key":[
									"platform",
									"wms",
									"disk_read_bandwidth"]}))
		self.calibrator.add_param("wms_write_bandwidth", sc.parameters.Exponential(20, 30).
								 format("%lfBps").set_custom_data({"json_type":str,"key":[
									"platform",
									"wms",
									"disk_write_bandwidth"]}))
		self.calibrator.add_param("wms_network_bandwidth", sc.parameters.Exponential(20, 40).
								 format("%lfbps").set_custom_data({"json_type":str,"key":[
									"platform",
									"wms",
									"network_bandwidth"]}))
		self.calibrator.add_param("worker_speed", sc.parameters.Linear(0.9, 1.1).
								 format("%lff").set_custom_data({"json_type":str,"key":[
									"platform",
									"workers",
									"worker\\d+",
									"speed"]}))		
		self.calibrator.add_param("worker_network_bandwidth", sc.parameters.Exponential(20, 40).
								 format("%lfbps").set_custom_data({"json_type":str,"key":[
									"platform",
									"workers",
									"worker\\d+",
									"network_bandwidth"]}))
		self.calibrator.add_param("task_scheduling_overhead", sc.parameters.Linear(0, 10).
								 format("%lf").set_custom_data({"json_type":float,"key":[
									"scheduling",
									"task_scheduling_overhead"]}))									
	def calibrate(self,timelimit):
		calibration, loss=self.calibrator.calibrate(self.simulator, timelimit=timelimit, coordinator=self.coordinator)
		return (calibration, loss, self.calibrator.timeline)



if __name__ == "__main__":
	class ParseException(Exception):
		pass
	import sys
	import argparse
	import traceback
	import parsl_scheduling_simulator.metrics
	import parsl_scheduling_simulator.loss as losses
	from glob import glob
	parser = argparse.ArgumentParser(description="Calibration Argument Parser")
	parser.add_argument("-p", "--simulator_path", type=str, help="Path to the simulator", required=True)
	parser.add_argument("-t", "--template", type=str, help="Template JSON as string", required=True)
	parser.add_argument("-e", "--experiments", nargs='+', type=str, help="Path to workflow files to run for experiment", required=True)
	parser.add_argument("-c", "--calibrator", type=str, help="Calibration Algorithm to use", required=True)
	parser.add_argument("-l", "--loss", type=str, help="Loss Function to use", default='relative_makespan_loss')
	parser.add_argument("-a", "--aggregator", type=str, help="Loss aggregator to use", default='avg_aggregator')
	parser.add_argument("-tss", "--task_selection_scheme", type=str, help="Task selection scheme", required=True)
	parser.add_argument("-wss", "--worker_selection_scheme", type=str, help="Worker selection scheme", required=True)
	parser.add_argument("-nss", "--num_cores_selection_scheme", type=str, help="Number of cores selection scheme", required=True)
	parser.add_argument("-n", "--num_threads", default=1,type=int, help="Number of threads", required=False)
	parser.add_argument("-d", "--time", type=int, help="Time to calibrate for")
	parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode", required=False)

	args=parser.parse_args()
	try: 
		with open(args.template) as template_file:
				template=json.load(template_file)
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
	simulator=CalibrationSimulator(args.simulator_path,template,experiments,alg,loss,verbosity = verbosity)
	calibrator=Calibrate(simulator,args.calibrator,args.num_threads)
	print(f"calibrating for {args.time}")
	start = time.perf_counter()
	calibration=calibrator.calibrate(args.time)
	elapsed = int(time.perf_counter() - start)
	sys.stderr.write(f"Actually ran in {timedelta(seconds=elapsed)}\n")
	print("finished")
	print(calibration[0])
	print(calibration[1])
	print(calibration[2])
	