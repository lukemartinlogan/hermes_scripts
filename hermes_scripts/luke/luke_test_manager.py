"""
USAGE: luke_test_manager.py [TEST_NAME]
"""
from jarvis_util.jutil_manager import JutilManager
from jarvis_util.shell.mpi_exec import MpiExec
from jarvis_util.shell.kill import Kill
from jarvis_util.shell.local_exec import LocalExec
from hermes_scripts.test_manager.test_manager import TestManager
import time
import os, sys


class LukeTestManager(TestManager):
    """======================================================================"""
    """ Test Case Constructor """
    """======================================================================"""
    def set_paths(self):
        self.CMAKE_SOURCE_DIR = os.path.join(os.getenv('MY_PROJECTS'),
                                             'hermes')
        self.CMAKE_BINARY_DIR = os.path.join(self.CMAKE_SOURCE_DIR,
                                             'cmake-build-release-gcc')
        self.HERMES_TRAIT_PATH = os.path.join(self.CMAKE_BINARY_DIR, 'bin')
        self.HERMES_CONF = os.path.join(self.TEST_MACHINE_DIR,
                                        'conf', 'hermes_server.yaml')
        self.HERMES_CLIENT_CONF = os.path.join(self.TEST_MACHINE_DIR,
                                               'conf', 'hermes_client.yaml')

    def set_devices(self):
        self.devices['nvme'] = '/tmp/test_hermes'
        os.makedirs(self.devices['nvme'], exist_ok=True)

    """======================================================================"""
    """ Native API Tests """
    """======================================================================"""

    def test_hermes_launch(self):
        """
        Test case. Launch the hermes daemon + shut it down.

        :return: None
        """
        self.start_daemon(self.get_env())
        self.stop_daemon(self.get_env())

    def test_hermes_put_get(self):
        """
        Test case. Test performance of PUT and GET operations in Hermes.

        :return: None
        """
        io_sizes = ["4k", "16k", "64k", "1m", "16m"]
        nprocs = [1, 2, 4, 8]
        total_size = 8 * (1 << 30)

        self.hermes_api_cmd(1, "putget", "1m", 8192)

    def test_hermes_create_bucket(self):
        """
        Test case. Test performance of PUT and GET operations in Hermes.

        :return: None
        """
        self.hermes_api_cmd(1, "create_bkt", 20e3)
        self.hermes_api_cmd(1, "create_bkt", 40e3)
        self.hermes_api_cmd(1, "create_bkt", 80e3)
        self.hermes_api_cmd(1, "create_bkt", 160e3)
        self.hermes_api_cmd(1, "create_bkt", 320e3)
        self.hermes_api_cmd(1, "create_bkt", 640e3)
        self.hermes_api_cmd(1, "create_bkt", 1280e3)

    def test_hermes_get_bucket(self):
        """
        Test case. Test performance of PUT and GET operations in Hermes.

        :return: None
        """
        self.hermes_api_cmd(1, "get_bkt", 20e3)
        self.hermes_api_cmd(1, "get_bkt", 40e3)
        self.hermes_api_cmd(1, "get_bkt", 80e3)
        self.hermes_api_cmd(1, "get_bkt", 160e3)
        self.hermes_api_cmd(1, "get_bkt", 320e3)
        self.hermes_api_cmd(1, "get_bkt", 640e3)
        self.hermes_api_cmd(1, "get_bkt", 1280e3)

    def test_hermes_create_bucket_scale(self):
        """
        Test case. Test performance of PUT and GET operations in Hermes.

        :return: None
        """
        self.hermes_api_cmd(1, "create_bkt", 128e3)
        self.hermes_api_cmd(2, "create_bkt", 64e3)
        self.hermes_api_cmd(4, "create_bkt", 32e3)
        self.hermes_api_cmd(8, "create_bkt", 16e3)

    """======================================================================"""
    """ IOR Tests (NO HERMES) """
    """======================================================================"""
    def test_ior_backends(self):
        self.ior_write_cmd(1, '1m', '1g', backend='posix')
        self.ior_write_cmd(1, '1m', '1g', backend='mpiio')
        self.ior_write_cmd(1, '1m', '1g', backend='hdf5')

    def test_ior_write(self):
        self.ior_write_cmd(1, '1m', '4g', backend='posix')

    def test_ior_write_read(self):
        pass

    """======================================================================"""
    """ IOR Tests (HERMES) """
    """======================================================================"""
    def test_hermes_ior_write(self):
        self.ior_write_cmd(1, '1m', '4g',
                           hermes_mode='kScratch', backend='posix')

    def test_hermes_ior_write_read(self):
        pass
