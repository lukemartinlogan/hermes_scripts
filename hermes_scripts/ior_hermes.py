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
# bench.append('orangefs',
#              mount='/home/llogan/ofs_mount')
bench.append('hermes_run',
             sleep=4, ram='8g',
             include='/home/llogan/ofs_mount')
bench.append('hermes_api', posix=True)
bench.append('ior', out='/home/llogan/ofs_mount/ior.bin')

# Scale the pipeline
io_sizes = ['4k', '64k', '1m']
proc_counts = [16, 32, 64, 128]
for io_size in io_sizes:
    for nprocs in proc_counts:
        bench.configure('ior',
                        xfer=io_size,
                        block='64m',
                        nprocs=nprocs,
                        ppn=nprocs,
                        write=True,
                        read=True)
        start = time.time()
        bench.run()
        stop = time.time()
        print(f'Time: {stop - start} sec')
        bench.clean()
        print('Cleaned')

print('COMPLETED!!!')
