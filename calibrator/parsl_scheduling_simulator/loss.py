

class Loss:
	def __init__(self,loss,aggregator):
		self.loss=loss
		self.aggregator=aggregator
def _relative_loss	(sim,real):
	return abs(real-sim)/real
		
def relative_makespan_loss(simulated,real):
	sim=simulated['finish_date']
	real=real['makespanInSeconds']
	return _relative_loss(sim,real)
	
def avg_aggregator(losses):
	import statistics
	return statistics.mean(losses)
	
def sum_aggregator(losses):
	return sum(losses)
	
class AvgMakespanLoss(Loss):
	def __init__(self):
		super().__init__(relative_makespan_loss,avg_aggregator)
		
def relative_runtime_loss(simulated,real):
	total=0
	for task in real["task_completions"]:
		realt=real["task_completions"][task]
		simt=simulated["task_completions"][task]
		sim=simt["end_date"]-simt["start_date"]
		real=realt["end_date"]-realt["start_date"]
		total+= _relative_loss(sim,real)
	return total/len(real["task_completions"])
		
def relative_starttime_loss(simulated,real):
	total=0
	for task in real["task_completions"]:
		realt=real["task_completions"][task]
		simt=simulated["task_completions"][task]
		sim=simt["start_date"]
		real=realt["start_date"]
		total+= _relative_loss(sim,real)	
	return total/len(real["task_completions"])

def relative_endtime_loss(simulated,real):
	total=0
	for task in real["task_completions"]:
		realt=real["task_completions"][task]
		simt=simulated["task_completions"][task]
		sim=simt["end_date"]
		real=realt["end_date"]
		total+=_relative_loss(sim,real)		
	return total/len(real["task_completions"])
	
def relative_endpoint_dif(simulated,real):
	total=0
	for task in real["task_completions"]:
		realt=real["task_completions"][task]
		simt=simulated["task_completions"][task]
		end=abs(simt["end_date"]-realt["end_date"])
		start=abs(simt["start_date"]-realt["start_date"])
		total+= (end+start)/(realt["end_date"]-realt["start_date"])
	return total/len(real["task_completions"])
	
def relative_endpoint_dif2(simulated,real):
	total=0
	for task in real["task_completions"]:
		realt=real["task_completions"][task]
		simt=simulated["task_completions"][task]
		union=max(realt["end_date"],simt["end_date"])-min(realt["start_date"],simt["start_date"])
		intersection=min(realt["end_date"],simt["end_date"])-max(realt["start_date"],simt["start_date"])
		total+= 1-union/intersection
	return total/len(real["task_completions"])
	
class AvgMakespanLoss(Loss):
	def __init__(self):
		super().__init__(relative_makespan_loss,avg_aggregator)