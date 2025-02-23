# "Scheduling using simulation" simulator

This project contains the code and data for evaluating the potential merit
of a "scheduling using online-simulation" approach. The key idea is that
rather than executing a particular scheduling algorithm for the entire
execution of some parallel/distributed application on parallel/distributed
resources, it may be beneficial instead to select which scheduling
algorithm to use at runtime, thereby using perhaps more than one scheduling
algorithm during the application execution. Algorithm selection is made
based on simulation results, that is, one executes simulations of an
application execution throughout that very execution! This simulator
uses this approach (yes, simulation within simulation) in the context
of scientific workflow applications.

## Simulator usage

After building the simulator (see instructions below), just invoke it
as `./scheduling_using_simulation_simulator --help` to see the (long and detailed) usage message.

A sample invocation could be:

```
./scheduling_using_simulation_simulator --clusters 32:8:100Gf:100.0:100MBps:100MBps,16:4:50Gf:40.0:100MBps:200MBps,24:6:80Gf:20.0:100MBps:80MBps  --workflow ../sample_workflows/genome.json --reference_flops 100Gf  --first_scheduler_change_trigger 0.00 --periodic_scheduler_change_trigger 0.1 --speculative_work_fraction 0.1 --wrench-energy-simulation --simulation_noise_scheme macro --algorithm_selection_scheme makespan --task_selection_scheme most_children,most_data --cluster_selection_scheme fastest_cores,lowest_watts --core_selection_scheme as_many_as_possible
```

## Building the simulator from source

### Prerequisites and Dependencies

- **g++** (version 6.3 or higher) or (**clang** - version 3.8 or higher)
- **CMake** - version 3.7 or higher
- [SimGrid](https://framagit.org/simgrid/simgrid/-/releases) - version 3.31 and its dependencies
- [WRENCH](https://framagit.org/simgrid/simgrid/-/releases) - version 2.0 or later

### Installation instructions

You've all done it before:

```bash
mkdir build
cd build
cmake ..
make
sudo make install
```




