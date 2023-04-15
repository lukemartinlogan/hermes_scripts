"""
USAGE: luke_test_manager.py [TEST_NAME]
"""
from jarvis_util.jutil_manager import JutilManager
from jarvis_util.shell.mpi_exec import MpiExec
from jarvis_util.shell.kill import Kill
from jarvis_util.shell.exec import Exec
from hermes_scripts.test_manager.test_manager import TestManager, SizeConv
import time
import getpass
import os, sys


class AresTestManager(TestManager):
    """======================================================================"""
    """ Test Case Constructor """
    """======================================================================"""
    def set_paths(self):
        self.CMAKE_SOURCE_DIR = os.path.join(os.getenv('HOME'),
                                             'hermes')
        self.CMAKE_BINARY_DIR = os.path.join(self.CMAKE_SOURCE_DIR,
                                             'build')
        self.HERMES_TRAIT_PATH = os.path.join(self.CMAKE_BINARY_DIR, 'bin')
        self.HERMES_CLIENT_CONF = os.path.join(self.TEST_MACHINE_DIR,
                                               'conf', 'hermes_client.yaml')
        self.HOSTFILE = os.path.join(os.getenv('HOME'), 'hostfile.txt')

    def set_devices(self):
        user = getpass.getuser()
        self.devices['ssd'] = f"/mnt/ssd/{user}/test_hermes"
        self.devices['nvme'] = f"/mnt/nvme/{user}/test_hermes"
        self.devices['pfs'] = f"{os.environ['HOME']}/test_hermes"

    def spawn_all_nodes(self):
        return self.spawn_info(hostfile=self.HOSTFILE)

    """======================================================================"""
    """ Native API Tests """
    """======================================================================"""

    def test_echo(self):
        """
        Test case. Launch the hermes daemon + shut it down.

        :return: None
        """
        spawn_info = self.spawn_info(hermes_conf='hermes_server')
        Exec("echo 5",
             self.spawn_info(hostfile=self.HOSTFILE))

    def test_hermes_launch(self):
        """
        Test case. Launch the hermes daemon + shut it down.

        :return: None
        """
        spawn_info = self.spawn_info(hermes_conf='hermes_server')
        self.start_daemon(spawn_info)
        self.stop_daemon(spawn_info)

    def test_hermes_launch_mn(self):
        """
        Test case. Launch the hermes daemon + shut it down.

        :return: None
        """
        spawn_info = self.spawn_info(
            hostfile=self.HOSTFILE,
            hermes_conf='hermes_server_ssd_nvme_ram_mn')
        self.start_daemon(spawn_info)
        self.stop_daemon(spawn_info)

    def test_hermes_put_get_tiered(self):
        """
        Test case. Test performance of PUT and GET operations in Hermes.

        :return: None
        """
        xfer_sizes = ["4k", "1m"]
        hermes_confs = [#"hermes_server_ssd",
                        #"hermes_server_ssd_nvme",
                        "hermes_server_ssd_nvme_ram"]
        nprocs = 12
        total_size = 20 * (1 << 30)
        size_pp = total_size / nprocs

        for xfer_size in xfer_sizes:
            for hermes_conf in hermes_confs:
                count_pp = int(size_pp / SizeConv.to_int(xfer_size))
                if count_pp * nprocs > 128000:
                    count_pp = 128000 / nprocs
                self.hermes_api_cmd(
                    self.spawn_info(nprocs, hermes_conf=hermes_conf),
                    "putget", xfer_size, count_pp)

    def test_hermes_put_get_scale(self):
        """
        Test case. Test performance of PUT and GET operations in Hermes.
        Vary number of processes and nodes

        :return: None
        """
        xfer_sizes = ["1m"]
        hermes_confs = [#"hermes_server_ssd",
                        #"hermes_server_ssd_nvme",
                        "hermes_server_ssd_nvme_ram"]
        nprocs = 24
        max_ppn = 12
        total_size = 40 * (1 << 30)
        size_pp = total_size / nprocs

        for xfer_size in xfer_sizes:
            for hermes_conf in hermes_confs:
                count_pp = int(size_pp / SizeConv.to_int(xfer_size))
                if count_pp * nprocs > 128000:
                    count_pp = 128000 / nprocs
                self.hermes_api_cmd(self.spawn_info(nprocs, ppn=max_ppn,
                                                    hermes_conf=hermes_conf),
                                    "putget", xfer_size, count_pp)

    def test_hermes_create_bucket(self):
        """
        Test case. Test performance of PUT and GET operations in Hermes.

        :return: None
        """
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'), 
                            "create_bkt", 20e3)
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'), 
                            "create_bkt", 40e3)
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'), 
                            "create_bkt", 80e3)
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'), 
                            "create_bkt", 160e3)
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'), 
                            "create_bkt", 320e3)
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'), 
                            "create_bkt", 640e3)
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'), 
                            "create_bkt", 1280e3)

    def test_hermes_create_bucket_mn(self):
        """
        Test case. Test performance of creating a bucket multiple nodes.

        :return: None
        """
        nprocs = [16, 32]
        counts = [128e3]
        for nproc in nprocs:
            for count in counts:
                count /= nproc
                spawn_info = self.spawn_info(
                    nprocs=nproc,
                    ppn=16,
                    hostfile=self.HOSTFILE,
                    hermes_conf="hermes_server_ssd_nvme_ram_mn")
                self.hermes_api_cmd(spawn_info, "create_bkt", count)

    def test_hermes_get_bucket(self):
        """
        Test case. Test performance of PUT and GET operations in Hermes.

        :return: None
        """
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'),
                            "get_bkt", 20e3)
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'),
                            "get_bkt", 40e3)
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'),
                            "get_bkt", 80e3)
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'),
                            "get_bkt", 160e3)
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'),
                            "get_bkt", 320e3)
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'),
                            "get_bkt", 640e3)
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'),
                            "get_bkt", 1280e3)

    def test_hermes_create_bucket_scale(self):
        """
        Test case. Test performance of creating a bucket (scaling).

        :return: None
        """
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'),
                            "create_bkt", 128e3)
        self.hermes_api_cmd(self.spawn_info(2, hermes_conf='hermes_server'),
                            "create_bkt", 64e3)
        self.hermes_api_cmd(self.spawn_info(4, hermes_conf='hermes_server'),
                            "create_bkt", 32e3)
        self.hermes_api_cmd(self.spawn_info(8, hermes_conf='hermes_server'),
                            "create_bkt", 16e3)

    def test_hermes_create_blob_1bkt(self):
        """
        Test case. Test performance of creating blobs in a
        single bucket (scale).

        :return: None
        """
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'),
                            "create_blob_1bkt", 128e3)
        self.hermes_api_cmd(self.spawn_info(2, hermes_conf='hermes_server'),
                            "create_blob_1bkt", 64e3)
        self.hermes_api_cmd(self.spawn_info(4, hermes_conf='hermes_server'),
                            "create_blob_1bkt", 32e3)
        self.hermes_api_cmd(self.spawn_info(8, hermes_conf='hermes_server'),
                            "create_blob_1bkt", 16e3)

    def test_hermes_create_blob_Nbkt(self):
        """
        Test case. Test performance of creating blobs per-bucket (scale).

        :return: None
        """
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'),
                            "create_blob_Nbkt", 128e3)
        self.hermes_api_cmd(self.spawn_info(2, hermes_conf='hermes_server'),
                            "create_blob_Nbkt", 64e3)
        self.hermes_api_cmd(self.spawn_info(4, hermes_conf='hermes_server'),
                            "create_blob_Nbkt", 32e3)
        self.hermes_api_cmd(self.spawn_info(8, hermes_conf='hermes_server'),
                            "create_blob_Nbkt", 16e3)

    def test_hermes_del_bkt(self):
        """
        Test case. Test performance of deleting a bucket.

        :return: None
        """
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'),
                            "del_bkt", 1, 128e3)
        self.hermes_api_cmd(self.spawn_info(2, hermes_conf='hermes_server'),
                            "del_bkt", 1, 64e3)
        self.hermes_api_cmd(self.spawn_info(4, hermes_conf='hermes_server'),
                            "del_bkt", 1, 32e3)
        self.hermes_api_cmd(self.spawn_info(8, hermes_conf='hermes_server'),
                            "del_bkt", 1, 16e3)

    def test_hermes_del_blobs(self):
        """
        Test case. Test performance of deleting a bucket.

        :return: None
        """
        self.hermes_api_cmd(self.spawn_info(1, hermes_conf='hermes_server'),
                            "del_blobs", 128e3)
        self.hermes_api_cmd(self.spawn_info(2, hermes_conf='hermes_server'),
                            "del_blobs", 64e3)
        self.hermes_api_cmd(self.spawn_info(4, hermes_conf='hermes_server'),
                            "del_blobs", 32e3)
        self.hermes_api_cmd(self.spawn_info(8, hermes_conf='hermes_server'),
                            "del_blobs", 16e3)

    """======================================================================"""
    """ IOR Tests (NO HERMES) """
    """======================================================================"""
    def test_ram_bw(self):
        count = SizeConv.to_int('16g') / SizeConv.to_int('1m')
        self.memcpy_test_cmd(self.spawn_info(1, hermes_conf='hermes_server'),
                             '1m', count)
        self.memcpy_test_cmd(self.spawn_info(2, hermes_conf='hermes_server'),
                             '1m', count / 2)
        self.memcpy_test_cmd(self.spawn_info(4, hermes_conf='hermes_server'),
                             '1m', count / 4)
        self.memcpy_test_cmd(self.spawn_info(8, hermes_conf='hermes_server'),
                             '1m', count / 8)
        self.memcpy_test_cmd(self.spawn_info(16, hermes_conf='hermes_server'),
                             '1m', count / 16)
        self.memcpy_test_cmd(self.spawn_info(32, hermes_conf='hermes_server'),
                             '1m', count / 32)

    def test_ram_latency(self):
        count = SizeConv.to_int('16g') / 4096
        self.memcpy_test_cmd(self.spawn_info(1, hermes_conf='hermes_server'),
                             '1m', count)
        self.memcpy_test_cmd(self.spawn_info(2, hermes_conf='hermes_server'),
                             '1m', count / 2)
        self.memcpy_test_cmd(self.spawn_info(4, hermes_conf='hermes_server'),
                             '1m', count / 4)
        self.memcpy_test_cmd(self.spawn_info(8, hermes_conf='hermes_server'),
                             '1m', count / 8)
        self.memcpy_test_cmd(self.spawn_info(16, hermes_conf='hermes_server'),
                             '1m', count / 16)
        self.memcpy_test_cmd(self.spawn_info(32, hermes_conf='hermes_server'),
                             '1m', count / 32)

    def test_ior_backends(self):
        self.ior_write_cmd(self.spawn_info(1, api='posix'), '1m', '1g')
        self.ior_write_cmd(self.spawn_info(1, api='mpiio'), '1m', '1g')
        self.ior_write_cmd(self.spawn_info(1, api='hdf5'), '1m', '1g')

    def test_ior_write(self):
        self.ior_write_cmd(self.spawn_info(8, api='posix'),
                           '1m', '4g', dev='ssd')

    def test_ior_write_mn(self):
        self.ior_write_cmd(self.spawn_info(8,
                                           ppn=4,
                                           hostfile=self.HOSTFILE,
                                           api='posix'),
                           '1m', '4g', dev='nvme')

    def test_ior_write_read(self):
        pass

    """======================================================================"""
    """ IOR Tests (HERMES) """
    """======================================================================"""
    def test_hermes_ior_write_tiered(self):
        self.ior_write_cmd(
            self.spawn_info(8,
                            hermes_mode='kScratch',
                            hermes_conf='hermes_server_ssd',
                            api='posix'),
            '1m', '4g', dev='ssd')
        self.ior_write_cmd(
            self.spawn_info(8,
                            hermes_mode='kScratch',
                            hermes_conf='hermes_server_ssd',
                            api='posix'),
            '1m', '4g', dev='ssd_nvme')
        self.ior_write_cmd(
            self.spawn_info(8,
                            hermes_mode='kScratch',
                            hermes_conf='hermes_server_ssd',
                            api='posix'),
            '1m', '4g', dev='ssd_nvme_ram')

    def test_hermes_ior_write_read(self):
        pass

