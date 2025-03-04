./simulator.py schedule -p workflow_simulator -t template.json -e ../data/forkjoin.json -tss most_flops -wss fastest_cores -nss one_core -c '{"platform":{"wms":{"disk_read_bandwidth":"100MBps","disk_write_bandwidth":"100MBps","network_bandwidth":"10Gbps"},"workers":{"worker1":{"speed":"1f","network_bandwidth":"10Gbps"},"worker2":{"speed":"1f","network_bandwidth":"10Gbps"}}},"scheduling":{"task_scheduling_overhead":1}}' -v