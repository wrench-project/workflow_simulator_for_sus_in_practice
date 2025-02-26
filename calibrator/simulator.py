import simcal as sc

import json
# There are 3 different simulators for the 3 different situations we will run them in
# SchedulingSimulator is for making scheduling decisions.  It is given the state parts of the json (ie the "workflow" sub object) at each run and is initialized with a calibration and a set of scheduling algorithms, and a metric to use.  Run will then run the simulator on that state with that calibration for each algorithm and return the algorithm(s) with the lowest score according to the metric.  THIS VERSION IS NOT INTENDED TO BE RAN WITH SIMCAL

# CalibrationSimulator is for offline calibration of the simulator.  It is given a calibration at each run and is initialized with a loss function to use and a list of "ground truth" executions to use.  These include the workflow specs and the schedule used for each groundtruth run as well as the expected output.  Run will then run the simulator for each execution in the ground truth and return a scalar using the loss function

# ErrorCorrectionSimulator is for online error correction of the simulator.  It is given a calibration at each run and is initialized with a loss function to use and the state of a single partial execution, and a scheduling algorithm.  Run will then run the simulator using that state and return a scalar using the loss function
def _exec(simulator: Simulator, alg,state,env):
    return args, simulator.run({"state":state,"alg":alg},env)
class Simulator(sc.Simulator):
	def __init__(self,simulator_path,json_template,verbosity = None):
		self.verbosity=[]
		if verbosity:
			self.verbosity=verbosity
		self.simulator_path=simulator_path
		self.json_template=json_template
		
	def exec(self,json_args,env):
		output = env.bash(self.simulator_path,json.dumps(json_args))
		try:
			json_output=json.loads(output)
		except:
			if "parse_error" in self.verbosity:
				print(output)
			raise
		if output[1] and "sim_error" in self.verbosity:
			print(output)
	
class SchedulingSimulator(Simulator):
	def __init__(self,simulator_path,json_template,calibration,algs,metric,coordinator,verbosity = None):
		super().__init__(simulator_path,json_template,verbosity)
		self.algs=algs
		self.metric=metric
	def run(self,args,env):
		#unpack args
		#call simulator
		#apply metric
	def __call__(self, args: Any, stoptime: int | float | None = None) -> str:
		best=None
		bestScore=None
		for alg in self.algs.asObj():
			coordinator.allocate(_eval, (simulator, alg, args, stoptime))
			results = coordinator.collect()
			for current, score in results:
				if score is None:
					continue
				if bestScore is None or score < bestScore:
					best = [current]
					bestScore=score
				elif  score==bestScore:
					best.append(alg)
		results = coordinator.await_all()
		for current, score in results:
			if score is None:
				continue
			if bestScore is None or score < bestScore:
				best = [current]
				bestScore=score
			elif  score==bestScore:
				best.append(alg)
				
		return best
class CalibrationSimulator(Simulator):
	def __init__(self,simulator_path,json_template,verbosity = None):
		super().__init__(simulator_path,json_template,verbosity)
	
	def run(self,args,env):
		pass
		
		
class ErrorCorrectionSimulator(Simulator):
	def __init__(self,simulator_path,json_template,verbosity = None):
		super().__init__(simulator_path,json_template,verbosity)
	
	def run(self,args,env):
		pass
		
		
if __name__ == "main":
	pass