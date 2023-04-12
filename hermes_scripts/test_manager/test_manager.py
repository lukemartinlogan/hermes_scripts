"""
USAGE: luke_test_manager.py [TEST_NAME]
"""
from jarvis_util.jutil_manager import JutilManager
from jarvis_util.shell.mpi_exec import MpiExec
from jarvis_util.shell.kill import Kill
from jarvis_util.shell.local_exec import LocalExec
import time
import os, sys
from abc import ABC, abstractmethod


class TestManager(ABC):
    """======================================================================"""
    """ Test Case Constructor """
    """======================================================================"""
    def __init__(self, hermes_scripts_root, test_machine_dir):
        """
        Initialize test manager
        """
        jutil = JutilManager.get_instance()
        jutil.collect_output = False
        self.TEST_MACHINE_DIR = test_machine_dir
        self.HERMES_SCRIPTS_ROOT = hermes_scripts_root
        self.CMAKE_SOURCE_DIR = None
        self.CMAKE_BINARY_DIR = None
        self.HERMES_TRAIT_PATH = None
        self.HERMES_CONF = None
        self.HERMES_CLIENT_CONF = None

        self.tests_ = {}
        self.devices = {}
        self.set_paths()
        self.set_devices()

        self.find_tests()

    @abstractmethod
    def set_paths(self):
        pass

    @abstractmethod
    def set_devices(self):
        pass

    def cleanup(self):
        for dir in self.devices.values():
            files = os.listdir(dir)
            for file in files:
                os.remove(os.path.join(dir, file))

    def find_tests(self):
        # Filter the list to include only attributes that start with "test"
        test_attributes = [attr for attr in dir(self) if
                           attr.startswith("test")]

        # Get a reference to each test method
        for attr in test_attributes:
            if callable(getattr(self, attr)):
                self.tests_[attr] = getattr(self, attr)

    def call(self, test_name):
        test_name = test_name.strip()
        if test_name in self.tests_:
            print(f"Running test: {test_name}")
            self.tests_[test_name]()
        else:
            print(f"{test_name} was not found. Available tests: ")
            for i, test in enumerate(self.tests_):
                print(f"{i}: {test}")
            exit(1)
        self.cleanup()

    """======================================================================"""
    """ General Test Helper Functions """
    """======================================================================"""

    def set_hermes_conf(self, name):
        """
        Choose the hermes configuration from the "luke" directory

        :param name: the name of the YAML file
        :return: None
        """
        self.HERMES_CONF = os.path.join(self.HERMES_SCRIPTS_ROOT,
                                        self.TEST_SYSTEM, 'conf', name)

    def get_env(self, preload=None, mode=None):
        """
        Get the current Hermes environment variables
        :return: Dict of strings
        """
        # Basic environment variables
        env = {
            'PATH': os.getenv('PATH'),
            'LD_LIBRARY_PATH': os.getenv('LD_LIBRARY_PATH'),
            'HERMES_CONF': self.HERMES_CONF,
            'HERMES_CLIENT_CONF': self.HERMES_CLIENT_CONF,
            'HERMES_TRAIT_PATH': self.HERMES_TRAIT_PATH,
        }

        # Hermes interceptor paths
        if mode is not None:
            if preload == 'posix':
                env['LD_PRELOAD'] = f"{self.CMAKE_BINARY_DIR}/bin" \
                                    f"/libhermes_posix.so"
            elif preload == 'stdio':
                env['LD_PRELOAD'] = f"{self.CMAKE_BINARY_DIR}/bin" \
                                    f"/libhermes_stdio.so"
            elif preload == 'mpiio':
                env['LD_PRELOAD'] = f"{self.CMAKE_BINARY_DIR}/bin" \
                                    f"/libhermes_mpiio.so"
            elif preload == 'hdf5':
                env['LD_PRELOAD'] = f"{self.CMAKE_BINARY_DIR}/bin" \
                                    f"/libhdf5_hermes_vfd.so"
                env['HDF5_PLUGIN_PATH'] = f"{self.CMAKE_BINARY_DIR}/bin"

        # Hermes mode
        if mode == 'kDefault':
            env['HERMES_ADAPTER_MODE'] = 'kDefault'
        if mode == 'kScratch':
            env['HERMES_ADAPTER_MODE'] = 'kScratch'
        if mode == 'kBypass':
            env['HERMES_ADAPTER_MODE'] = 'kBypass'

        return env

    def start_daemon(self, env, num_nodes=1):
        """
        Helper function. Start the Hermes daemon

        :param env: Hermes environment variables
        :return: None
        """
        Kill("hermes_daemon")

        print("Start daemon")
        self.daemon = LocalExec(f"{self.CMAKE_BINARY_DIR}/bin/hermes_daemon",
                                env=env,
                                collect_output=True,
                                exec_async=True)
        time.sleep(3)
        print("Launched")

    def stop_daemon(self, env):
        """
        Helper function. Stop the Hermes daemon.

        :param env: Hermes environment variables
        :return: None
        """
        print("Stop daemon")
        LocalExec(f"{self.CMAKE_BINARY_DIR}/bin/finalize_hermes",
                  collect_output=True,
                  env=env)
        self.daemon.wait()
        print("Stopped daemon")

    """======================================================================"""
    """ Native API Tests + Commands """
    """======================================================================"""

    def hermes_api_cmd(self, nprocs, mode, *args):
        """
        Helper function. Run Hermes internal API performance tests.

        :return: None
        """

        self.start_daemon(self.get_env())
        cmd = [
            f"{self.CMAKE_BINARY_DIR}/bin/api_bench",
            mode,
        ]
        cmd += [str(arg) for arg in args]
        cmd = " ".join(cmd)
        print(cmd)
        MpiExec(cmd,
                nprocs=nprocs,
                env=self.get_env())
        self.stop_daemon(self.get_env())

    """======================================================================"""
    """ IOR Test Commands """
    """======================================================================"""

    def get_ior_backend(self, backend):
        if backend == 'posix':
            return '-a=POSIX -F'
        if backend == 'mpiio':
            return '-a=MPIIO'
        if backend == 'hdf5':
            return '-a=HDF5'
        return ''

    def ior_write_cmd(self, nprocs, transfer_size,
                      io_size_per_rank,
                      backend=None,
                      hermes_mode=None,
                      dev='nvme'):
        """
        A write-only IOR workload

        :param nprocs: MPI process to spawn
        :param transfer_size: size of each I/O in IOR (e.g., 16k, 1m, 4g)
        :param io_size_per_rank: Total amount of I/O to do for each rank
        :param backend: Which backend to use
        :param hermes_mode: The mode to run Hermes in. None indicates no Hermes.
        :param dev: The device to output data to

        :return: None
        """
        # Start daemon
        if hermes_mode is not None:
            self.start_daemon(self.get_env())

        # Run IOR
        cmd = [
            'ior',
            '-w',   # Write-only
            f"-o {self.devices[dev]}/hi.txt",  # Output file
            f"-t {transfer_size}",
            f"-b {io_size_per_rank}",
            '-k',   # Keep files after IOR
            self.get_ior_backend(backend)
        ]
        cmd = " ".join(cmd)
        MpiExec(cmd,
                nprocs=nprocs,
                env=self.get_env(preload=backend, mode=hermes_mode))

        # Stop daemon
        if hermes_mode is not None:
            self.stop_daemon(self.get_env())

    def ior_write_read_no_hermes_cmd(self, nprocs, transfer_size,
                                     io_size_per_rank,
                                     backend=None,
                                     hermes_mode=None,
                                     dev='nvme'):
        """
        A write-then-read IOR workflow

        :param nprocs: MPI process to spawn
        :param transfer_size: size of each I/O in IOR (e.g., 16k, 1m, 4g)
        :param io_size_per_rank: Total amount of I/O to do for each rank
        :param backend: Which backend to use
        :param hermes_mode: The mode to run Hermes in. None indicates no Hermes.
        :param dev: The device to output data to

        :return: None
        """
        # Start daemon
        if hermes_mode is not None:
            self.start_daemon(self.get_env())

        # Run IOR
        cmd = [
            'ior',
            '-w',   # Write-only
            f"-o {self.devices[dev]}/hi.txt",  # Output file
            f"-t {transfer_size}",
            f"-b {io_size_per_rank}",
            '-k',
            self.get_ior_backend(backend)
        ]
        cmd = " ".join(cmd)
        MpiExec(cmd,
                nprocs=nprocs,
                env=self.get_env(preload=backend, mode=hermes_mode))

        # Stop daemon
        if hermes_mode is not None:
            self.stop_daemon(self.get_env())
