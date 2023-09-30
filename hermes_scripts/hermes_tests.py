from jarvis_cd.basic.pkg import Pipeline
import time

# Create baseline pipeline
bench = Pipeline.load('hermes_scripts_bench')
bench.destroy()
bench.build_env()
bench.append('hermes_run', sleep=5)
bench.append('hermes_api', posix=True)
bench.append('ior')

# Scale the pipeline
proc_counts = [2, 4, 8, 16]
for nprocs in proc_counts:
    bench.configure('ior', xfer='4k', block='32m', nprocs=nprocs)
    start = time.time()
    bench.run()
    stop = time.time()
    print('Time: {} sec', stop - start)

