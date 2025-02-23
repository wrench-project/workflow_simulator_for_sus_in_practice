# Workflow simulator for Scheduling-Using-Simulation (SUS) in practice

After building the simulator (see instructions below), just invoke it
as `./workflow_simulator --help` to see the usage message. See the `./data`
directory for a sample invocation.

## Building the simulator from source

### Prerequisites and Dependencies

- **g++** (version 6.3 or higher) or (**clang** - version 3.8 or higher)
- **CMake** - version 3.7 or higher
- [WRENCH](https://framagit.org/simgrid/simgrid/-/releases) - version 2.5 or later (and its dependencies)

### Installation instructions

You've all done it before:

```bash
mkdir build
cd build
cmake ..
make
sudo make install
```




