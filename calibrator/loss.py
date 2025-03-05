

class Loss:
	def __init__(self,loss,aggregator):
		self.loss=loss
		self.aggregator=aggregator
		
def relative_makespan_loss(simulated,real):
	sim=simulated['finish_date']
	real=real['makespanInSeconds']
	return abs(real-sim)/real
	
def avg_aggregator(losses):
	import statistics
	return statistics.mean(losses)
	
class AvgMakespanLoss(Loss):
	def __init__(self):
		super().__init__(relative_makespan_loss,avg_aggregator)