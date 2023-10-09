# HERMES Scripts

This repo contains various tests we have conducted on Hermes.
We use python for the actual running of test cases, and bash scripts
for the act of 

## Dependencies
```
spack external find python
spack install hermes@dev-1.1 ior
spack load hermes@dev-1.1 ior
```

## IOR Scalability Test

This evaluation will scale number of processes between 2 and 16.
It uses an I/O size of 4KB. It generates total of 32MB per process. 

```
jarvis pipeline create hermes_bench
jarvis pipeline env build +ORANGEFS_PATH
python3 hermes_scripts/ior_hermes.py hermes_bench
```
