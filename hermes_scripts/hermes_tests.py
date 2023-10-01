"""
USAGE: ./hermes_tests [pipeline-name]
"""

from jarvis_util import *
from jarvis_cd.basic.pkg import Pipeline
import time
import sys

# Create baseline pipeline
name = sys.argv[1]
bench = Pipeline().load(name)
# will clear all packages from pipeline
# will not erase env.yaml
bench.clear()
# append packages to pipeline
bench.append('hermes_run', sleep=2)
bench.append('hermes_api', posix=True)
bench.append('ior')

# Scale the pipeline
proc_counts = [2, 4, 8, 16]
for nprocs in proc_counts:
    bench.configure('ior', xfer='4k', block='32m', nprocs=nprocs)
    start = time.time()
    bench.run()
    stop = time.time()
    print(f'Time: {stop - start} sec')
    bench.clean()
    print('Cleaned')

print('COMPLETED!!!')
