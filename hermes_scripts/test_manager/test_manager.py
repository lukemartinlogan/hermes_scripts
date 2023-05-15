"""
USAGE: luke_test_manager.py [TEST_NAME]
"""
from jarvis_util.jutil_manager import JutilManager
from jarvis_util.shell.process import Kill
from jarvis_util.shell.exec_info import ExecType, ExecInfo
from jarvis_util.shell.local_exec import LocalExecInfo
from jarvis_util.shell.mpi_exec import MpiExecInfo
from jarvis_util.shell.pssh_exec import PsshExecInfo
from jarvis_util.shell.filesystem import Rm
from jarvis_util.shell.exec import Exec
import time
import os, sys
from abc import ABC, abstractmethod


class SpawnInfo(MpiExecInfo):
    def __init__(self, nprocs, hermes_conf=None, hermes_mode=None, api=None,
                 **kwargs):
        super().__init__(nprocs=nprocs, **kwargs)
        self.hermes_conf = hermes_conf
        self.hermes_mode = hermes_mode
        self.api = api


class SizeConv:
    @staticmethod
    def to_int(text):
        text = text.lower()
        if 'k' in text:
            return SizeConv.KB(text)
        if 'm' in text:
            return SizeConv.MB(text)
        if 'g' in text:
            return SizeConv.GB(text)
        if 't' in text:
            return SizeConv.TB(text)
        if 'p' in text:
            return SizeConv.PB(text)
        return int(text)

    @staticmethod
    def KB(num):
        return int(num.split('k')[0]) * (1 << 10)

    @staticmethod
    def MB(num):
        return int(num.split('m')[0]) * (1 << 20)

    @staticmethod
    def GB(num):
        return int(num.split('g')[0]) * (1 << 30)

    @staticmethod
    def TB(num):
        return int(num.split('t')[0]) * (1 << 40)

    @staticmethod
    def PB(num):
        return int(num.split('p')[0]) * (1 << 50)


class TestManager(ABC):
    """======================================================================"""
    """ Test Case Constructor """
    """======================================================================"""
    def __init__(self, hermes_scripts_root, test_machine_dir):
        """
        Initialize test manager
        """
        jutil = JutilManager.get_instance()
        jutil.collect_output = True
        jutil.hide_output = False
        self.TEST_MACHINE_DIR = test_machine_dir
        self.HERMES_SCRIPTS_ROOT = hermes_scripts_root
        self.CMAKE_SOURCE_DIR = None
        self.CMAKE_BINARY_DIR = None
        self.HERMES_TRAIT_PATH = None
        self.HERMES_CLIENT_CONF = None
        self.daemon = None

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

    @abstractmethod
    def spawn_all_nodes(self):
        pass

    def test_init(self):
        # Make all device paths
        spawn_info = self.spawn_all_nodes()
        paths = " ".join(list(self.devices.values()))
        Exec(f"mkdir -p {paths}",
             PsshExecInfo(hostfile=spawn_info.hostfile))

    def test_hostfile(self):
        # Make all device paths
        spawn_info = self.spawn_all_nodes()
        for count in range(1, min(len(spawn_info.hostfile), 5)):
            print(f"TEST {count}: {spawn_info.hostfile.subset(count)[0:count]}")
            Exec(f"hostname",
                 PsshExecInfo(hostfile=spawn_info.hostfile.subset(count)))
            print()

    def spawn_info(self, nprocs=None, ppn=None, hostfile=None,
                   hermes_conf=None, hermes_mode=None, api=None,
                   file_output=None):
        # Whether to deploy hermes
        use_hermes = hermes_mode is not None \
                     or api == 'native' \
                     or hermes_conf is not None

        # Get the hermes configuration path
        if use_hermes:
            if hermes_conf is None:
                hermes_conf = os.path.join(self.TEST_MACHINE_DIR,
                                           'conf', 'hermes_server.yaml')
            else:
                hermes_conf = os.path.join(self.TEST_MACHINE_DIR,
                                           'conf',
                                           f"{hermes_conf}.yaml")

        # Basic environment variables
        env = {
            'PATH': os.getenv('PATH'),
            'LD_LIBRARY_PATH': os.getenv('LD_LIBRARY_PATH')
        }
        if use_hermes:
            env.update({
                'HERMES_LOG_OUT': "/tmp/hermes_log.txt",
                'HERMES_CONF': hermes_conf,
                'HERMES_CLIENT_CONF': self.HERMES_CLIENT_CONF,
                'HERMES_TRAIT_PATH': self.HERMES_TRAIT_PATH,
            })
            if hostfile:
                env['HERMES_HOSTFILE'] = hostfile.path

        # Hermes interceptor paths
        if use_hermes:
            if api == 'posix':
                env['LD_PRELOAD'] = f"{self.CMAKE_BINARY_DIR}/bin" \
                                    f"/libhermes_posix.so"
            elif api == 'stdio':
                env['LD_PRELOAD'] = f"{self.CMAKE_BINARY_DIR}/bin" \
                                    f"/libhermes_stdio.so"
            elif api == 'mpiio':
                env['LD_PRELOAD'] = f"{self.CMAKE_BINARY_DIR}/bin" \
                                    f"/libhermes_mpiio.so"
            elif api == 'hdf5':
                env['LD_PRELOAD'] = f"{self.CMAKE_BINARY_DIR}/bin" \
                                    f"/libhdf5_hermes_vfd.so"
                env['HDF5_PLUGIN_PATH'] = f"{self.CMAKE_BINARY_DIR}/bin"

        # Hermes mode
        if hermes_mode == 'kDefault':
            env['HERMES_ADAPTER_MODE'] = 'kDefault'
        if hermes_mode == 'kScratch':
            env['HERMES_ADAPTER_MODE'] = 'kScratch'
        if hermes_mode == 'kBypass':
            env['HERMES_ADAPTER_MODE'] = 'kBypass'

        return SpawnInfo(nprocs=nprocs,
                         ppn=ppn,
                         hostfile=hostfile,
                         hermes_conf=hermes_conf,
                         hermes_mode=hermes_mode,
                         pipe_stdout=file_output,
                         pipe_stderr=file_output,
                         api=api,
                         env=env)

    def cleanup(self):
        dirs = " ".join([os.path.join(d, '*') for d in self.devices.values()])
        Rm(dirs, PsshExecInfo(hostfile=self.spawn_all_nodes().hostfile))

    def find_tests(self):
        # Filter the list to include only attributes that start with "test"
        test_attributes = [attr for attr in dir(self) if
                           attr.startswith("test")]

        # Get a reference to each test method
        for attr in test_attributes:
            if callable(getattr(self, attr)):
                self.tests_[attr] = getattr(self, attr)

    def call(self, test_name):
        self.set_paths()
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

    def test_kill(self):
        print("BEGIN KILL")
        Kill("hermes_daemon",
             PsshExecInfo(
                 hostfile=self.spawn_all_nodes().hostfile,
                 collect_output=False))
        print("END KILL")

    def test_is_launched(self):
        print("BEGIN LAUNCH TEST")
        Exec("hostname && ps -ef | grep hermes_daemon",
             PsshExecInfo(
                 hostfile=self.spawn_all_nodes().hostfile,
                 collect_output=False))
        print("END LAUNCH TEST")

    def start_daemon(self, spawn_info):
        """
        Helper function. Start the Hermes daemon

        :param env: Hermes environment variables
        :return: None
        """
        Kill("hermes_daemon",
             PsshExecInfo(
                 hostfile=spawn_info.hostfile,
                 collect_output=False))

        print("Start daemon")
        self.daemon = Exec(f"{self.CMAKE_BINARY_DIR}/bin/hermes_daemon",
                           PsshExecInfo(
                               hostfile=spawn_info.hostfile,
                               env=spawn_info.env,
                               collect_output=False,
                               hide_output=False,
                               exec_async=True))
        time.sleep(30)
        print("Launched")

    def stop_daemon(self, spawn_info):
        """
        Helper function. Stop the Hermes daemon.

        :param env: Hermes environment variables
        :return: None
        """
        print("Stop daemon")
        Exec(f"{self.CMAKE_BINARY_DIR}/bin/finalize_hermes",
             LocalExecInfo(
                 env=spawn_info.env,
                 collect_output=False))
        self.daemon.wait()
        print("Stopped daemon")

    """======================================================================"""
    """ Native API Tests + Commands """
    """======================================================================"""

    def hermes_api_cmd(self, spawn_info, test_case, *args):
        """
        Helper function. Run Hermes internal API performance tests.

        :return: None
        """
        self.start_daemon(spawn_info)
        cmd = [
            f"{self.CMAKE_BINARY_DIR}/bin/api_bench",
            test_case,
        ]
        cmd += [str(arg) for arg in args]
        cmd = " ".join(cmd)
        print(f"HERMES_CONF={spawn_info.hermes_conf} {cmd}")
        Exec(cmd, spawn_info)
        self.stop_daemon(spawn_info)

    """======================================================================"""
    """ IOR Test Commands """
    """======================================================================"""

    def memcpy_test_cmd(self, spawn_info, xfer_size, count):
        cmd = [
            f"{self.CMAKE_BINARY_DIR}/bin/memcpy_bench",
            str(xfer_size),
            str(count)
        ]
        cmd = " ".join(cmd)
        Exec(cmd, spawn_info)

    def get_ior_backend(self, backend):
        if backend == 'posix':
            return '-a=POSIX -F'
        if backend == 'mpiio':
            return '-a=MPIIO'
        if backend == 'hdf5':
            return '-a=HDF5'
        return ''

    def ior_write_cmd(self, spawn_info, transfer_size,
                      io_size_per_rank,
                      dev='nvme'):
        """
        A write-only IOR workload

        :param spawn_info: MPI process to spawn
        :param transfer_size: size of each I/O in IOR (e.g., 16k, 1m, 4g)
        :param io_size_per_rank: Total amount of I/O to do for each rank
        :param dev: The device to output data to

        :return: None
        """
        # Start daemon
        if spawn_info.hermes_mode is not None:
            self.start_daemon(spawn_info)

        # Run IOR
        cmd = [
            'ior',
            '-w',   # Write-only
            f"-o {self.devices[dev]}/hi.txt",  # Output file
            f"-t {transfer_size}",
            f"-b {io_size_per_rank}",
            '-k',   # Keep files after IOR
            self.get_ior_backend(spawn_info.api)
        ]
        cmd = " ".join(cmd)
        Exec(cmd, spawn_info)

        # Stop daemon
        if spawn_info.hermes_mode is not None:
            self.stop_daemon(spawn_info)

    def ior_write_read_cmd(self, spawn_info, transfer_size,
                           io_size_per_rank,
                           dev='nvme'):
        """
        A write-then-read IOR workflow

        :param spawn_info: MPI process to spawn
        :param transfer_size: size of each I/O in IOR (e.g., 16k, 1m, 4g)
        :param io_size_per_rank: Total amount of I/O to do for each rank
        :param dev: The device to output data to

        :return: None
        """
        # Start daemon
        if spawn_info.hermes_mode is not None:
            self.start_daemon(spawn_info)

        # Run IOR
        cmd = [
            'ior',
            '-w -r',   # Write-only
            f"-o {self.devices[dev]}/hi.txt",  # Output file
            f"-t {transfer_size}",
            f"-b {io_size_per_rank}",
            '-k',
            self.get_ior_backend(spawn_info.api)
        ]
        cmd = " ".join(cmd)
        Exec(cmd, spawn_info)

        # Stop daemon
        if spawn_info.hermes_mode is not None:
            self.stop_daemon(spawn_info)
