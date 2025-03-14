#!/usr/bin/env python

import simcal as sc
from .simulator import *
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
