# Workflow simulator for Scheduling-Using-Simulation (SUS) in practice

After building the simulator (see instructions below), just invoke it
as `./workflow_simulator --help` to see the usage message. See the `./data`
directory for a sample invocation.

## Building the simulator from source

### Prerequisites and Dependencies

- [SimGrid](https://framagit.org/simgrid/simgrid): `master` branch (commit tag: `ab006ff8ec8cd0088efa31fd729c048706bf37b8`)
- [FSMod](https://github.com/simgrid/file-system-module): `master` branch (commit tag: `744d760d963d721578172483fd7e55bede23ae32`)
- [WRENCH](https://github.com/wrench-project/wrench): `simgrid_master` branch


### Installation instructions

You've all done it before:

```bash
mkdir build
cd build
cmake ..
make
sudo make install
```




