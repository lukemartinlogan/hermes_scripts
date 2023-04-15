"""
USAGE: luke_test_manager.py [TEST_NAME]
"""
from jarvis_util.jutil_manager import JutilManager
from jarvis_util.shell.mpi_exec import MpiExec
from jarvis_util.shell.kill import Kill
from jarvis_util.shell.local_exec import LocalExec
from hermes_scripts.test_manager.test_manager import *
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

    def spawn_all_nodes(self):
        return self.spawn_info(hostfile=None)

    """======================================================================"""
    """ Native API Tests """
    """======================================================================"""

    def test_hermes_launch(self):
        """
        Test case. Launch the hermes daemon + shut it down.

        :return: None
        """
        spawn_info = self.spawn_info(hermes_conf='hermes_server')
        self.start_daemon(spawn_info)
        self.stop_daemon(spawn_info)

    def test_hermes_put_get(self):
        """
        Test case. Test performance of PUT and GET operations in Hermes.

        :return: None
        """
        io_sizes = ["4k", "16k", "64k", "1m", "16m"]
        nprocs = [1, 2, 4, 8]
        total_size = 8 * (1 << 30)

        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "putget", "1m", 8192)

    def test_hermes_create_bucket(self):
        """
        Test case. Test performance of PUT and GET operations in Hermes.

        :return: None
        """
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "create_bkt", 20e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "create_bkt", 40e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "create_bkt", 80e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "create_bkt", 160e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "create_bkt", 320e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "create_bkt", 640e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "create_bkt", 1280e3)

    def test_hermes_get_bucket(self):
        """
        Test case. Test performance of PUT and GET operations in Hermes.

        :return: None
        """
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "get_bkt", 20e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "get_bkt", 40e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "get_bkt", 80e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "get_bkt", 160e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "get_bkt", 320e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "get_bkt", 640e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "get_bkt", 1280e3)

    def test_hermes_create_bucket_scale(self):
        """
        Test case. Test performance of creating a bucket (scaling).

        :return: None
        """
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "create_bkt", 128e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=2,
            hermes_conf='hermes_server'), "create_bkt", 64e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=4,
            hermes_conf='hermes_server'), "create_bkt", 32e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=8,
            hermes_conf='hermes_server'), "create_bkt", 16e3)

    def test_hermes_create_blob_1bkt(self):
        """
        Test case. Test performance of creating blobs in a
        single bucket (scale).

        :return: None
        """
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "create_blob_1bkt", 128e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=2,
            hermes_conf='hermes_server'), "create_blob_1bkt", 64e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=4,
            hermes_conf='hermes_server'), "create_blob_1bkt", 32e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=8,
            hermes_conf='hermes_server'), "create_blob_1bkt", 16e3)

    def test_hermes_create_blob_Nbkt(self):
        """
        Test case. Test performance of creating blobs per-bucket (scale).

        :return: None
        """
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1), "create_blob_Nbkt", 128e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=2,
            hermes_conf='hermes_server'), "create_blob_Nbkt", 64e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=4,
            hermes_conf='hermes_server'), "create_blob_Nbkt", 32e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=8,
            hermes_conf='hermes_server'), "create_blob_Nbkt", 16e3)

    def test_hermes_del_bkt(self):
        """
        Test case. Test performance of deleting a bucket.

        :return: None
        """
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "del_bkt", 1, 128e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=2,
            hermes_conf='hermes_server'), "del_bkt", 1, 64e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=4,
            hermes_conf='hermes_server'), "del_bkt", 1, 32e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=8,
            hermes_conf='hermes_server'), "del_bkt", 1, 16e3)

    def test_hermes_del_blobs(self):
        """
        Test case. Test performance of deleting a bucket.

        :return: None
        """
        self.hermes_api_cmd(self.spawn_info(
            nprocs=1,
            hermes_conf='hermes_server'), "del_blobs", 128e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=2,
            hermes_conf='hermes_server'), "del_blobs", 64e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=4,
            hermes_conf='hermes_server'), "del_blobs", 32e3)
        self.hermes_api_cmd(self.spawn_info(
            nprocs=8,
            hermes_conf='hermes_server'), "del_blobs", 16e3)

    """======================================================================"""
    """ IOR Tests (NO HERMES) """
    """======================================================================"""
    def test_ram(self):
        self.memcpy_test_cmd(self.spawn_info(nprocs=1, api=None), '1m', 4096)
        self.memcpy_test_cmd(self.spawn_info(nprocs=2, api=None), '1m', 2048)
        self.memcpy_test_cmd(self.spawn_info(nprocs=4, api=None), '1m', 1024)

    def test_ior_backends(self):
        self.ior_write_cmd(self.spawn_info(nprocs=1, api='posix'), '1m', '1g')
        self.ior_write_cmd(self.spawn_info(nprocs=2, api='mpiio'), '1m', '1g')
        self.ior_write_cmd(self.spawn_info(nprocs=4, api='hdf5'), '1m', '1g')

    def test_ior_write(self):
        self.ior_write_cmd(self.spawn_info(nprocs=1, api='posix'), '1m', '4g')

    def test_ior_write_read(self):
        pass

    """======================================================================"""
    """ IOR Tests (HERMES) """
    """======================================================================"""
    def test_hermes_ior_write(self):
        self.ior_write_cmd(self.spawn_info(
            nprocs=1,
            hermes_mode='kScratch',
            api='posix'), '1m', '4g')
        self.ior_write_cmd(self.spawn_info(
            nprocs=1,
            hermes_mode='kScratch',
            api='mpiio'), '1m', '4g')
        self.ior_write_cmd(self.spawn_info(
            nprocs=1,
            hermes_mode='kScratch',
            api='hdf5'), '1m', '4g')

    def test_hermes_ior_write_read(self):
        pass
