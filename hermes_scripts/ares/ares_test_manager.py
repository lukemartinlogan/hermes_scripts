"""
USAGE: luke_test_manager.py [TEST_NAME]
"""
from jarvis_util.jutil_manager import JutilManager
from jarvis_util.shell.mpi_exec import MpiExec
from jarvis_util.shell.process import Kill
import itertools
from jarvis_util.util.hostfile import Hostfile
from jarvis_util.shell.exec import Exec
from jarvis_util.util.size_conv import SizeConv
from hermes_scripts.test_manager.test_manager import TestManager
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
        self.HOSTFILE_DIR = os.path.join(os.getenv('HOME'), 'hostfiles')
        self.HOSTFILE = Hostfile(os.path.join(
            os.getenv('HOME'), 'hostfile.txt'))
        self.TEST_DIR = os.path.join(os.getenv('HOME'),
                                     f"hermes_outputs")
        os.makedirs(self.TEST_DIR, exist_ok=True)
        os.makedirs(self.HOSTFILE_DIR, exist_ok=True)
        self.hostfiles = [self.HOSTFILE.subset(count).save(
                          f"{self.HOSTFILE_DIR}/hostfile_{count}.txt")
                          for count in range(0, len(self.HOSTFILE) + 1)]

    def set_devices(self):
        user = getpass.getuser()
        self.devices['ssd'] = f"/mnt/ssd/{user}/test_hermes"
        self.devices['nvme'] = f"/mnt/nvme/{user}/test_hermes"
        self.devices['hdd'] = f"/mnt/hdd/{user}/test_hermes"
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
        for hostfile in [self.hostfiles[1]]:
            spawn_info = self.spawn_info(
                hostfile=hostfile,
                hermes_conf='hermes_server_ssd_nvme_ram_tcp')
            self.start_daemon(spawn_info)
            self.stop_daemon(spawn_info)

    def test_hermes_put_get_tiered(self):
        """
        Test case. Test performance of PUT and GET operations in Hermes.

        :return: None
        """
        #xfer_size_set = ["4k", "64k", "1m"]
        xfer_size_set = ["1m"]
        hermes_conf_set = [#"hermes_server_ssd_tcp",
                           "hermes_server_ssd_nvme_tcp",
                           "hermes_server_ssd_nvme_ram_tcp"]
        num_nodes_set = [1]
        ppn_set = [1, 2, 4, 8, 16, 32, 48]
        size_per_node = {
            #'4k': SizeConv.to_int('500m'),
            #'64k': SizeConv.to_int('6g'),
            '1m': SizeConv.to_int('40g'),
        }
        combos = itertools.product(xfer_size_set, hermes_conf_set,
                                   num_nodes_set, ppn_set)

        for xfer_size, hermes_conf, num_nodes, ppn in combos:
            size_pp = size_per_node[xfer_size] / ppn
            xfer_size = SizeConv.to_int(xfer_size)
            count_pp = size_pp / xfer_size
            nprocs = num_nodes * ppn
            test_name = f"test_hermes_put_get_tiered_" \
                        f"{xfer_size}_{hermes_conf}_{num_nodes}_{ppn}"
            self.hermes_api_cmd(
                self.spawn_info(nprocs=nprocs,
                                ppn=ppn,
                                hostfile=self.hostfiles[num_nodes],
                                hermes_conf=hermes_conf,
                                file_output=f"{self.TEST_DIR}/{test_name}"),
                "putget", xfer_size, count_pp)

    def test_hermes_put_get_tiered_mn(self):
        """
        Test case. Test performance of PUT and GET operations in Hermes.

        :return: None
        """
        #xfer_size_set = ["4k", "64k", "1m"]
        xfer_size_set = ["1m"]
        hermes_conf_set = ["hermes_server_ssd_tcp",
                           "hermes_server_ssd_nvme_tcp",
                           "hermes_server_ssd_nvme_ram_tcp"]
        # num_nodes_set = [1, 2, 4, 8, 15]
        num_nodes_set = [1, 2, 4, 8]
        ppn_set = [16]
        size_per_node = {
            #'4k': SizeConv.to_int('500m'),
            #'64k': SizeConv.to_int('6g'),
            '1m': SizeConv.to_int('10g'),
        }
        combos = itertools.product(xfer_size_set, hermes_conf_set,
                                   num_nodes_set, ppn_set)

        for xfer_size, hermes_conf, num_nodes, ppn in combos:
            size_pp = size_per_node[xfer_size] / ppn
            xfer_size = SizeConv.to_int(xfer_size)
            count_pp = size_pp / xfer_size
            nprocs = num_nodes * ppn
            test_name = f"test_hermes_put_get_tiered_mn_" \
                        f"{xfer_size}_{hermes_conf}_{num_nodes}_{ppn}"
            self.hermes_api_cmd(
                self.spawn_info(nprocs=nprocs,
                                ppn=ppn,
                                hostfile=self.hostfiles[num_nodes],
                                hermes_conf=hermes_conf,
                                file_output=f"{self.TEST_DIR}/{test_name}"),
                "putget", xfer_size, count_pp)

    def test_hermes_put_get_dpe(self):
        """
        Test case. Test performance of PUT and GET operations in Hermes.

        :return: None
        """
        #xfer_size_set = ["4k", "64k", "1m"]
        xfer_size_set = ["1m"]
        hermes_conf_set = ["hermes_server_ssd_nvme_ram_minio_tcp",
                           "hermes_server_ssd_nvme_ram_rand_tcp",
                           "hermes_server_ssd_nvme_ram_rr_tcp"]
        num_nodes_set = [4]
        ppn_set = [16]
        size_per_node = {
            '1m': SizeConv.to_int('40g'),
        }
        combos = itertools.product(xfer_size_set, hermes_conf_set,
                                   num_nodes_set, ppn_set)

        for xfer_size, hermes_conf, num_nodes, ppn in combos:
            size_pp = size_per_node[xfer_size] / ppn
            xfer_size = SizeConv.to_int(xfer_size)
            count_pp = size_pp / xfer_size
            nprocs = num_nodes * ppn
            test_name = f"test_hermes_put_get_dpe_" \
                        f"{xfer_size}_{hermes_conf}_{num_nodes}_{ppn}"
            self.hermes_api_cmd(
                self.spawn_info(nprocs=nprocs,
                                ppn=ppn,
                                hostfile=self.hostfiles[num_nodes],
                                hermes_conf=hermes_conf,
                                file_output=f"{self.TEST_DIR}/{test_name}"),
                "putget", xfer_size, count_pp)

    def test_hermes_create_bucket_count(self):
        """
        Test case. Test performance of creating buckets at scale.

        :return: None
        """
        count_pn_set = [20e3, 40e3, 80e3, 160e3, 320e3, 640e3]
        hermes_conf_set = ["hermes_server_ssd_nvme_ram_tcp"]
        num_nodes_set = [1]
        ppn_set = [1]
        combos = itertools.product(count_pn_set, hermes_conf_set,
                                   num_nodes_set, ppn_set)
        for count_pn, hermes_conf, num_nodes, ppn in combos:
            count_pp = int(count_pn / ppn)
            nprocs = num_nodes * ppn
            test_name = f"test_hermes_create_bucket_count_" \
                        f"{count_pn}_{hermes_conf}_{num_nodes}_{ppn}"
            self.hermes_api_cmd(
                self.spawn_info(nprocs=nprocs,
                                ppn=ppn,
                                hostfile=self.hostfiles[num_nodes],
                                hermes_conf=hermes_conf,
                                file_output=f"{self.TEST_DIR}/{test_name}"),
                "create_bkt", count_pp)

    def test_hermes_create_bucket(self):
        """
        Test case. Test performance of creating buckets at scale.

        :return: None
        """
        count_pn_set = [160e3]
        hermes_conf_set = ["hermes_server_ssd_nvme_ram_tcp"]
        num_nodes_set = [1, 2, 3, 4]
        ppn_set = [1, 2, 4, 8, 16, 32, 48]
        combos = itertools.product(count_pn_set, hermes_conf_set,
                                   num_nodes_set, ppn_set)
        for count_pn, hermes_conf, num_nodes, ppn in combos:
            count_pp = int(count_pn / ppn)
            nprocs = num_nodes * ppn
            test_name = f"test_hermes_create_bucket_" \
                        f"{count_pn}_{hermes_conf}_{num_nodes}_{ppn}"
            self.hermes_api_cmd(
                self.spawn_info(nprocs=nprocs,
                                ppn=ppn,
                                hostfile=self.hostfiles[num_nodes],
                                hermes_conf=hermes_conf,
                                file_output=f"{self.TEST_DIR}/{test_name}"),
                "create_bkt", count_pp)

    def test_hermes_get_bucket_count(self):
        """
        Test case. Test getting buckets at scale.

        :return: None
        """
        count_pn_set = [20e3, 40e3, 80e3, 160e3, 320e3, 640e3]
        hermes_conf_set = ["hermes_server_ssd_nvme_ram_tcp"]
        num_nodes_set = [1, 2, 3, 4]
        ppn_set = [1]
        combos = itertools.product(count_pn_set, hermes_conf_set,
                                   num_nodes_set, ppn_set)
        for count_pn, hermes_conf, num_nodes, ppn in combos:
            count_pp = int(count_pn / ppn)
            nprocs = num_nodes * ppn
            test_name = f"test_hermes_get_bucket_count_" \
                        f"{count_pn}_{hermes_conf}_{num_nodes}_{ppn}"
            self.hermes_api_cmd(
                self.spawn_info(nprocs=nprocs,
                                ppn=ppn,
                                hostfile=self.hostfiles[num_nodes],
                                hermes_conf=hermes_conf,
                                file_output=f"{self.TEST_DIR}/{test_name}"),
                "get_bkt", count_pp)

    def test_hermes_get_bucket(self):
        """
        Test case. Test getting buckets at scale.

        :return: None
        """
        count_pn_set = [160e3]
        hermes_conf_set = ["hermes_server_ssd_nvme_ram_tcp"]
        num_nodes_set = [1, 2, 3, 4]
        ppn_set = [1, 2, 4, 8, 16, 32, 48]
        combos = itertools.product(count_pn_set, hermes_conf_set,
                                   num_nodes_set, ppn_set)
        for count_pn, hermes_conf, num_nodes, ppn in combos:
            count_pp = int(count_pn / ppn)
            nprocs = num_nodes * ppn
            test_name = f"test_hermes_get_bucket_" \
                        f"{count_pn}_{hermes_conf}_{num_nodes}_{ppn}"
            self.hermes_api_cmd(
                self.spawn_info(nprocs=nprocs,
                                ppn=ppn,
                                hostfile=self.hostfiles[num_nodes],
                                hermes_conf=hermes_conf,
                                file_output=f"{self.TEST_DIR}/{test_name}"),
                "get_bkt", count_pp)

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
        nprocs_set = [1, 2, 4, 8, 16, 32]
        for nprocs in nprocs_set:
            self.memcpy_test_cmd(
                self.spawn_info(nprocs, hermes_conf='hermes_server'),
                '1m', count / nprocs)

    def test_ram_latency(self):
        count = SizeConv.to_int('16g') / SizeConv.to_int('4k')
        nprocs_set = [1, 2, 4, 8, 16, 32]
        for nprocs in nprocs_set:
            self.memcpy_test_cmd(
                self.spawn_info(nprocs, hermes_conf='hermes_server'),
                '4k', count / nprocs)

    def test_ior_backends(self):
        self.ior_write_cmd(self.spawn_info(1, api='posix'), '1m', '1g')
        self.ior_write_cmd(self.spawn_info(1, api='mpiio'), '1m', '1g')
        self.ior_write_cmd(self.spawn_info(1, api='hdf5'), '1m', '1g')

    def test_device_bw(self):
        nprocs_set = [1, 2, 4, 8, 16, 32, 48]
        dev_set = ['ssd', 'nvme']
        total_size = ['10g', '20g', '40g']
        test_cases = itertools.product(nprocs_set, dev_set, total_size)
        for nprocs, dev, total_size in test_cases:
            test_name = f"test_device_bw_{dev}_{nprocs}_{total_size}"
            test_out = f"{self.TEST_DIR}/{test_name}"
            spawn_info = self.spawn_info(nprocs=nprocs,
                                         ppn=nprocs,
                                         hostfile=self.hostfiles[1],
                                         file_output=test_out,
                                         api='posix')
            total_size = SizeConv.to_int(total_size)
            size_pp = total_size / nprocs
            self.ior_write_read_cmd(spawn_info,
                                    '1m', size_pp, dev=dev)
        self.test_ram_bw()

    def test_ior_write_pfs(self):
        num_nodes_set = [1, 2, 3, 4]
        ppn_set = [16]
        test_cases = itertools.product(num_nodes_set, ppn_set)
        for num_nodes, ppn in test_cases:
            nprocs = ppn * num_nodes
            spawn_info = self.spawn_info(nprocs,
                                         ppn=ppn,
                                         hostfile=self.hostfiles[num_nodes],
                                         api='posix')
            self.ior_write_cmd(spawn_info, '1m', '1g', dev='nvme')

    def test_ior_write_read(self):
        pass

    """======================================================================"""
    """ IOR Tests (HERMES) """
    """======================================================================"""
    def test_hermes_ior_write_tiered(self):
        num_nodes_set = [4]
        io_size = ['1m']
        ppn_set = [16]
        config_set = ['hermes_server_ssd_nvme_ram_tcp',
                      'hermes_server_ssd_nvme_tcp',
                      'hermes_server_ssd_tcp']
        apis = ['posix']
        test_cases = itertools.product(num_nodes_set, ppn_set, config_set, apis)
        for num_nodes, ppn, config, api in test_cases:
            nprocs = ppn * num_nodes
            test_name = f"test_hermes_ior_write_tiered_{num_nodes}_{ppn}_{api}_{io_size}_{config}"
            test_out = f"{self.TEST_DIR}/{test_name}"
            spawn_info = self.spawn_info(
                nprocs=nprocs,
                ppn=ppn,
                hostfile=self.hostfiles[num_nodes],
                hermes_conf=config,
                hermes_mode='kScratch',
                file_output=test_out,
                api=api)
            self.ior_write_cmd(spawn_info, io_size, '1g', dev='hdd')

    def test_hermes_ior_write_read(self):
        pass

