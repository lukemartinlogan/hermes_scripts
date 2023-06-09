# HERMES Scripts

This repo contains various tests we have conducted on Hermes.
We use python for the actual running of test cases, and bash scripts
for the act of 

## Dependencies
```
spack install ior +hdf5
spack install hermes +vfd
spack load hermes ior
git clone https://github.com/lukemartinlogan/jarvis-util.git
cd jarvis-util
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

Please note that Hermes may install python as a dependency, so you
should do spack load first.

## Usage

To execute a test, do the following
```bash
cd /path/to/hermes_scripts
spack load --only dependencies hermes
spack load ior
bin/cache_env
bash run_test.sh [TEST_MACHINE] [TEST_NAME]
```

For example:
```bash
bash run_test.sh ares test_hermes_ior_write_tiered
```

### Test Machines
Test machines are located underneath the "hermes_scripts" directory.
This is a python repo. test_manager/test_manager.py contains commands 
used internally to execute various experiments. All other 
directories (e.g., ares) inherit from this command class. With the
exception of "test_manager", all other directories are considered
test machines.

The test machines are as follows:
1. luke: my personal machine
2. ares: the Ares cluster at Illinois Tech

Running the Ares tests should be portable, so long as dependencies are
installed.

## Ares Test Cases

All tests are represented as functions in the file 
hermes_scripts/ares/ares_test_manager.py.

### 1. Setup Tests

There is some setup to do before running tests.

#### 1.1. CD into the hermes_scripts directory

We assume that you're in the hermes_scripts directory when running tests.
This is fundamental to the correctness of the platform.

```bash
cd /path/to/hermes_scripts
```

#### 1.2. Create a hostfile
```bash
nano ${HOME}/hostfile.txt
```
For now, we assume the hostfile is under ${HOME}/hostfile.txt

Example hostfile entries are as follows:
```
ares-comp-01-40g
ares-comp-[01-04]-40g
ares-comp-[01-05,06]-40g
```

We do not support fancy hostfile things. Just specify the nodes things
run on. If needed, we'll add fancy MPI hostfile features, but for now,
just specify the set of hosts.

#### 1.3. Create testing directories
```
bash run_test.sh ares test_init
```
This will create all necessary directories for tests. For now, this
is required.

### 1.4. Cache the spack environment

spack load is extremely slow. It's much faster to cache environment variables
in a shell script.

```
spack load --only dependencies hermes
spack load ior
bin/cache_env
```

### Run Tests

The only test we've executed recently is the one below. Other tests need
updating.

#### 1. test_hermes_ior_write_tiered

The objective of the experiment is to determine the impact of adding
additional tiers. 

Workload Description
1. 16GB total dataset size
2. 1MB transfer size
3. Write-only
4. Dataset will fit entirely in the fastest tier

To run the experiment:
```bash
bash run_test.sh ares test_hermes_ior_write_tiered
```

This will output data to ${HOME}/hermes_outputs/test_hermes_ior_write_tiered_*
```bash
ls ${HOME}/hermes_outputs | grep test_hermes_ior_write_tiered_*
```