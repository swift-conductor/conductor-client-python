from swift_conductor.automation.worker_host import WorkerHost
from swift_conductor.automation.worker_process import WorkerProcess
from swift_conductor.configuration import Configuration
from tests.unit.resources.workers import ClassWorker
from unittest.mock import Mock
from unittest.mock import patch
from configparser import ConfigParser
import multiprocessing
import unittest
import tempfile


class PickableMock(Mock):
    def __reduce__(self):
        return (Mock, ())


class TestWorkerHost(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_initialization_with_invalid_workers(self):
        expected_exception = Exception('Invalid worker list')
        with self.assertRaises(Exception) as context:
            WorkerHost(
                configuration=Configuration(),
                workers=ClassWorker()
            )
            self.assertEqual(expected_exception, context.exception)

    def test_start_processes(self):
        with patch.object(WorkerProcess, 'run', PickableMock(return_value=None)):
            with _get_valid_worker_host() as worker_host:
                worker_host.start_processes()
                self.assertEqual(len(worker_host.task_runner_processes), 1)
                for process in worker_host.task_runner_processes:
                    self.assertTrue(
                        isinstance(process, multiprocessing.Process)
                    )

    @patch("multiprocessing.Process.kill", Mock(return_value=None))
    def test_initialize_with_no_worker_config(self):
        with _get_valid_worker_host() as worker_host:
            worker_config = worker_host.worker_config
            self.assertIsInstance(worker_config, ConfigParser)
            self.assertEqual(len(worker_config.sections()), 0)

    @patch("multiprocessing.Process.kill", Mock(return_value=None))
    def test_initialize_with_worker_config(self):
        with tempfile.NamedTemporaryFile(mode='w+') as tf:
            configParser = ConfigParser()
            configParser.add_section('task')
            configParser.set('task', 'domain', 'test')
            configParser.set('task', 'polling_interval', '200.0')
            configParser.add_section('task2')
            configParser.set('task2', 'domain', 'test2')
            configParser.set('task2', 'polling_interval', '300.0')
            configParser.write(tf)
            tf.seek(0)
            
            def get_config_file_path_mock():
                return tf.name

            with patch('swift_conductor.automation.worker_host.__get_config_file_path', get_config_file_path_mock):
                with _get_valid_worker_host() as worker_host:
                    config = worker_host.worker_config
                    self.assertIsInstance(config, ConfigParser)
                    self.assertEqual(len(config.sections()), 2)
                    self.assertEqual(config.get('task', 'domain'), "test")
                    self.assertEqual(config.get('task', 'polling_interval'), "200.0")
                    self.assertEqual(config.get('task2', 'domain'), "test2")
                    self.assertEqual(config.get('task2', 'polling_interval'), "300.0")

def _get_valid_worker_host():
    return WorkerHost(
        configuration=Configuration(),
        workers=[
            ClassWorker('task')
        ]
    )
