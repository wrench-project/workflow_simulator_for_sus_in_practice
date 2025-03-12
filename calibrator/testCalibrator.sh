for alg in random gradient genetic grid skopt.gp skopt.gbrt skopt.et skopt.rf; do
echo $alg
	./calibrator.py -p workflow_simulator -t template.json -e ../../parsle_data/groundtruth_* -tss most_flops -wss fastest_cores -nss one_core -c $alg -d 600 -v 
done