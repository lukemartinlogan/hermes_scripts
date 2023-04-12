# HERMES Scripts

This repo contains various tests we have conducted on Hermes.
We use python for the actual running of test cases, and bash scripts
for the act of 

## Dependencies
```
spack install ior +hdf5
spack install hermes
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
bash run_test.sh [TEST_MACHINE] [TEST_NAME]
```

For example:
```bash
bash run_test.sh ares test_hermes_create_bucket
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
