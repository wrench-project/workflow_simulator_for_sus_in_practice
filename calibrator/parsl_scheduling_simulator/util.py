import re
import json
import hashlib 

_units={None:1,"":1,
"s":1,"ms":0.001,"us":0.000001,"ns":0.000000001,
"f":1,"Kf":1_000, "Mf":1_000_000,"Gf":1_000_000_000,
"Bps":1,"KBps":1_000,"MBps":1_000_000,"GBps":1_000_000_000,
"bps":1,"Kbps":1_000,"Mbps":1_000_000,"Gbps":1_000_000_000,
"b":1,"Kb":1_000,"Mb":1_000_000,"Gb":1_000_000_000,
"B":1,"KB":1_000,"MB":1_000_000,"GB":1_000_000_000}

def ensureFull(calibration):
	flagWords={'wms_read_bandwidth', 'wms_write_bandwidth','wms_network_bandwidth','worker_speed','worker_network_bandwidth','task_scheduling_overhead','task_ready_delay'}
	for term in flagWords:#check that all flag words are in callibration
		if term not in calibration:
			break
	else:	
		for key in calibration: #check that the calibration only contains flag words
			if key not in flagWords:
				break
		else:
		#convert
			return {"platform":{"wms":{"disk_read_bandwidth":calibration['wms_read_bandwidth'],"disk_write_bandwidth":calibration['wms_write_bandwidth'],"network_bandwidth":calibration['wms_network_bandwidth']},"workers":{"worker\\d":{"speed":calibration['worker_speed'],"network_bandwidth":calibration['worker_network_bandwidth']}}},"scheduling":{"task_scheduling_overhead":float(calibration['task_scheduling_overhead']),"task_ready_delay": float(calibration['task_ready_delay'])}}
	return calibration
def raw_to_ast(input_str):
    
	items=input_str[1:-1].split(",")
	
	for i in range(len(items)):
		each=items[i].split(":")
		each = [("'"+ea.strip()+"'").replace("''","'") for ea in each]
		items[i]=":".join(each)
	return "{"+(", ".join(items))+"}"
def parseDoubleUnited(raw: str):
	#print(raw,re.match(r"(\d+\.?\d*)([a-zA-Z]+)*", raw).groups())
	result = re.match(r"(\d+\.?\d*)([a-zA-Z]+)*", raw).groups()
	return float(result[0])*_units[result[1]]
def load_json(path):
	with open(path) as json_file:
		return json.load(json_file)
def flatten(arr):
	flat_list = []
	for item in arr:
		if isinstance(item, list) or isinstance(item, tuple):
			flat_list.extend(flatten(item))  # Recursively flatten the nested list
		else:
			flat_list.append(item)  # Append non-list item
	return flat_list
def relative_error(ground, target):
	return abs(target - ground) / ground

def orderinvarient_hash(x,l=22):
	x=flatten(x)
	acc=bytearray(hashlib.md5(bytes(len(x))).digest())
	for i in x:
		tmp=hashlib.md5(i.encode()).digest()
		
		for j in range(len(acc)):
			#acc[j]^=tmp[j]
			acc[j]=(tmp[j]+acc[j])%256
	return base64.urlsafe_b64encode(acc)[:l].decode()
	


