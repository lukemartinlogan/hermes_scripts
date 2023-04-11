"""
USAGE: test_manager.py [TEST_NAME]
"""
from jarvis_util.jutil_manager import JutilManager
from jarvis_util.shell.mpi_exec import MpiExec
from jarvis_util.shell.kill import Kill
from jarvis_util.shell.local_exec import LocalExec
import time
import os, sys

class TestManager:
    instance_ = None
    tests_ = {}

    @staticmethod
    def get_instance():
        if TestManager.instance_ is None:
            TestManager.instance_ = TestManager()
        return TestManager.instance_

    def __init__(self):
        """
        Initialize test manager
        """
        jutil = JutilManager.get_instance()
        jutil.collect_output = False
        self.HERMES_SCRIPTS_ROOT = os.getcwd()
        self.CMAKE_SOURCE_DIR = os.path.join(os.getenv('MY_PROJECTS'),
                                             'hermes')
        self.CMAKE_BINARY_DIR = os.path.join(self.CMAKE_SOURCE_DIR,
                                             'cmake-build-release-gcc')
        self.HERMES_TRAIT_PATH = os.path.join(self.CMAKE_BINARY_DIR, 'bin')
        self.HERMES_CONF = os.path.join(self.HERMES_SCRIPTS_ROOT,
                                        'local', 'conf', 'hermes_server.yaml')
        self.HERMES_CLIENT_CONF = os.path.join(self.HERMES_SCRIPTS_ROOT,
                                               'local', 'conf',
                                               'hermes_client.yaml')
        self.find_tests()

    def find_tests(self):
        # Filter the list to include only attributes that start with "test"
        test_attributes = [attr for attr in dir(TestManager) if
                           attr.startswith("test")]

        # Get a reference to each test method
        for attr in test_attributes:
            if callable(getattr(TestManager, attr)):
                TestManager.tests_[attr] = getattr(TestManager, attr)

    def call(self, test_name):
        test_name = test_name.strip()
        if test_name in self.tests_:
            print(f"Running test: {test_name}")
            self.tests_[test_name](self)
        else:
            print(f"{test_name} was not found. Available tests: ")
            for i, test in enumerate(self.tests_):
                print(f"{i}: {test}")
            exit(1)

    def set_hermes_conf(self, name):
        """
        Choose the hermes configuration from the "local" directory

        :param name: the name of the YAML file
        :return: None
        """
        self.HERMES_CONF = os.path.join(self.HERMES_SCRIPTS_ROOT,
                                        'local', 'conf', name)

    def get_env(self):
        """
        Get the current Hermes environment variables
        :return: Dict of strings
        """
        return {
            'HERMES_CONF': self.HERMES_CONF,
            'HERMES_CLIENT_CONF': self.HERMES_CLIENT_CONF,
            'HERMES_TRAIT_PATH': self.HERMES_TRAIT_PATH,
        }

    def start_daemon(self, env):
        """
        Helper function. Start the Hermes daemon

        :param env: Hermes environment variables
        :return: None
        """
        Kill("hermes_daemon")

        print("Start daemon")
        self.daemon = LocalExec(f"{self.CMAKE_BINARY_DIR}/bin/hermes_daemon",
                                env=env,
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
        LocalExec(f"{self.CMAKE_BINARY_DIR}/bin/finalize_hermes", env=env)
        self.daemon.wait()
        print ("Stopped daemon")

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

if len(sys.argv) != 2:
    print("USAGE: ./test_manager.py [TEST_NAME]")
    exit(1)
test_name = sys.argv[1]
tests = TestManager.get_instance()
tests.call(test_name)
