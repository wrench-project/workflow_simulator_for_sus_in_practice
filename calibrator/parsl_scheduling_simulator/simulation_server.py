#!/usr/bin/env python
import simcal as sc
from .util import *
from .simulator import SchedulingSimulator
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
			start=time.now()
			self.shared_data["ret"]=self.shared_data["simulator"](lastState)
			self.shared_data["last_state_update"]=time.now()-start	
class SimulationServer:
	def __init__(self,simulator):
		self.manager = multiprocessing.Manager()
		self.shared_data = self.manager.dict()  # Shared dictionary for variables
		self.shared_data["simulator"]=simulator
		self.shared_data["running"]=True
		self.shared_data["state"]=None
		self.shared_data["last_time"]=None
		self.shared_data["ret"]=None
		self.simulation_time=None
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
		self.simulation_time=self.shared_data["last_state_update"]	
		ret=self.shared_data["ret"]
		self.update_state(state)
		return ret
		
	def wait(self):
		if self.process is not None:
			self.process.join()
			self.process = None
		self.simulation_time=self.shared_data["last_state_update"]	
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
		self.simulation_time=self.shared_data["last_state_update"]		
		return 	self.shared_data["ret"]
	def stop(self):
		"""Stop the background process."""
		self.shared_data["running"] = False
		if self.process is not None:
			self.process.join()
			self.process = None
		self.simulation_time=self.shared_data["last_state_update"]		
		return self.shared_data["ret"]
