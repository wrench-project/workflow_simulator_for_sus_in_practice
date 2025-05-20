

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

def max_aggregator(losses):
	return max(losses)
	
class AvgMakespanLoss(Loss):
	def __init__(self):
		super().__init__(relative_makespan_loss,avg_aggregator)
		
def relative_runtime_loss(simulated,real):
	total=0
	for task in real["tasks"]:
		realt=task
		taskid=realt["id"]
		simt=simulated["task_completions"][taskid]
		sim=simt["end_date"]-simt["start_date"]
		realt=realt["runtimeInSeconds"]
		total+= _relative_loss(sim,realt)
	return total/len(real["tasks"])
		
def relative_starttime_loss(simulated,real):
	total=0
	for task in real["tasks"]:
		realt=task
		taskid=realt["id"]
		simt=simulated["task_completions"][taskid]
		sim=simt["start_date"]
		realt=realt["executedAt"]
		total+= abs(sim-realt)
	return total/len(real["tasks"])


def relative_endtime_loss(simulated,real):
	total=0
	for task in real["tasks"]:
		realt=task
		taskid=realt["id"]
		simt=simulated["task_completions"][taskid]
		sim=simt["end_date"]
		realt=realt["executedAt"]+realt["runtimeInSeconds"]
		total+= abs(sim-realt)
	return total/len(real["tasks"])
	
def relative_endpoint_dif(simulated,real):
	total=0
	for task in real["tasks"]:
		realt=task
		taskid=realt["id"]
		simt=simulated["task_completions"][taskid]
		end=abs(simt["end_date"]-(realt["executedAt"]+realt["runtimeInSeconds"]))
		start=abs(simt["start_date"]-realt["executedAt"])
		total+= (end+start)/(realt["runtimeInSeconds"])
	return total/len(real["tasks"])

	
def relative_endpoint_dif2(simulated,real):
	total=0
	for task in real["tasks"]:
		realt=task
		taskid=realt["id"]
		simt=simulated["task_completions"][taskid]
		union=max((realt["executedAt"]+realt["runtimeInSeconds"]),simt["end_date"])-min(realt["executedAt"],simt["start_date"])
		intersection=min((realt["executedAt"]+realt["runtimeInSeconds"]),simt["end_date"])-max(realt["executedAt"],simt["start_date"])
		total+= abs(1-union/intersection)
	return total/len(real["tasks"])

	
class AvgMakespanLoss(Loss):
	def __init__(self):
		super().__init__(relative_makespan_loss,avg_aggregator)