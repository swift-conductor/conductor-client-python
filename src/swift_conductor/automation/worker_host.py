from swift_conductor.automation.worker_process import WorkerProcess
from swift_conductor.configuration import Configuration
from swift_conductor.settings.metrics_settings import MetricsSettings
from swift_conductor.telemetry.metrics_collector import MetricsCollector
from swift_conductor.worker.worker_impl import WorkerImpl
from swift_conductor.worker.worker_abc import WorkerAbc
from multiprocessing import Process, freeze_support
from configparser import ConfigParser
from typing import List
import ast
import astor
import inspect
import logging
import os
import copy

logger = logging.getLogger(
    Configuration.get_logging_formatted_name(
        __name__
    )
)

class WorkerHost:
    def __init__(
            self,
            workers: List[WorkerAbc] = None,
            configuration: Configuration = None,
            metrics_settings: MetricsSettings = None,
    ):
        self.worker_config = load_worker_config()

        if workers is None:
            workers = []
        elif not isinstance(workers, list):
            workers = [workers]

        self.__create_task_runner_processes(
            workers, configuration, metrics_settings
        )

        self.__create_metrics_provider_process(
            metrics_settings
        )
        logger.info('Created all processes')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_processes()

    def stop_processes(self) -> None:
        self.__stop_task_runner_processes()
        self.__stop_metrics_provider_process()
        logger.debug('stopped processes')

    def start_processes(self) -> None:
        logger.info('Starting worker processes...')
        freeze_support()
        self.__start_task_runner_processes()
        self.__start_metrics_provider_process()
        logger.info('Started all processes')

    def join_processes(self) -> None:
        self.__join_task_runner_processes()
        self.__join_metrics_provider_process()
        logger.info('Joined all processes')

    def __create_metrics_provider_process(self, metrics_settings: MetricsSettings) -> None:
        if metrics_settings == None:
            self.metrics_provider_process = None
            return
        
        self.metrics_provider_process = Process(target=MetricsCollector.provide_metrics, args=(metrics_settings))
        logger.info('Created MetricsProvider process')

    def __create_task_runner_processes(self, workers: List[WorkerAbc], configuration: Configuration, metrics_settings: MetricsSettings) -> None:
        self.task_runner_processes = []
        
        for worker in workers:
            self.__create_task_runner_process(worker, configuration, metrics_settings)
        
        logger.info('Created TaskRunner processes')

    def __create_task_runner_process(self, worker: WorkerAbc, configuration: Configuration, metrics_settings: MetricsSettings) -> None:
        task_runner = WorkerProcess(worker, configuration, metrics_settings, self.worker_config)
        process = Process(target=task_runner.run)
        self.task_runner_processes.append(process)

    def __start_metrics_provider_process(self):
        if self.metrics_provider_process == None:
            return
        
        self.metrics_provider_process.start()
        
        logger.info('Started MetricsProvider process')

    def __start_task_runner_processes(self):
        for task_runner_process in self.task_runner_processes:
            task_runner_process.start()
        
        logger.info('Started TaskRunner processes')

    def __join_metrics_provider_process(self):
        if self.metrics_provider_process == None:
            return
        
        self.metrics_provider_process.join()
        
        logger.info('Joined MetricsProvider processes')

    def __join_task_runner_processes(self):
        for task_runner_process in self.task_runner_processes:
            task_runner_process.join()
        
        logger.info('Joined TaskRunner processes')

    def __stop_metrics_provider_process(self):
        self.__stop_process(self.metrics_provider_process)

    def __stop_task_runner_processes(self):
        for task_runner_process in self.task_runner_processes:
            self.__stop_process(task_runner_process)

    def __stop_process(self, process: Process):
        if process == None:
            return
        try:
            process.kill()
            logger.debug(f'Killed process: {process}')
        except Exception as e:
            logger.debug(f'Failed to kill process: {process}, reason: {e}')
            process.terminate()
            logger.debug('Terminated process: {process}')


def __get_client_topmost_package_filepath():
    module = inspect.getmodule(inspect.stack()[-1][0])
    while module:
        if not getattr(module, '__parent__', None):
            logger.debug(f'parent module not found for {module}')
            return getattr(module, '__file__', None)
        module = getattr(module, '__parent__', None)
    return None


def load_worker_config():
    worker_config = ConfigParser()

    try:
        file = __get_config_file_path()
        worker_config.read(file)
    except Exception as e:
        logger.error(str(e))

    return worker_config


def __get_config_file_path() -> str:
    return os.getcwd() + "/worker.ini"
