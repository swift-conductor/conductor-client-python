from configparser import ConfigParser
import logging
import sys
import time
import traceback
import os

from swift_conductor.configuration import Configuration
from swift_conductor.settings.metrics_settings import MetricsSettings

from swift_conductor.http.api_client import ApiClient
from swift_conductor.http.api.task_resource_api import TaskResourceApi

from swift_conductor.http.models.task import Task
from swift_conductor.http.models.task_result import TaskResult
from swift_conductor.http.models.task_exec_log import TaskExecLog
from swift_conductor.telemetry.metrics_collector import MetricsCollector

from swift_conductor.worker.worker_abc import WorkerAbc

logger_name = Configuration.get_logging_formatted_name(__name__)
logger = logging.getLogger(logger_name)

class WorkerProcess:
    def __init__(self, worker: WorkerAbc, 
                 configuration: Configuration = None, 
                 metrics_settings: MetricsSettings = None, worker_config: ConfigParser =  None
    ):
        if not isinstance(worker, WorkerAbc):
            raise Exception('Invalid worker type. Must be of type WorkerAbc.')
        
        self.worker = worker
        self.worker_config = worker_config

        self.__set_worker_properties()
        
        if not isinstance(configuration, Configuration):
            configuration = Configuration()

        self.configuration = configuration
        self.metrics_collector = None
        
        if metrics_settings is not None:
            self.metrics_collector = MetricsCollector(metrics_settings)
        
        self.api_client = ApiClient(configuration=self.configuration)
        self.task_client = TaskResourceApi(self.api_client)

    def run(self) -> None:
        if self.configuration != None:
            self.configuration.apply_logging_config()

        while True:
            try:
                self.run_once()
            except Exception:
                pass

    def run_once(self) -> None:
        task = self._poll_task()
        if task != None and task.task_id != None:
            task_result = self._execute_task(task)
            self._update_task(task_result)
        
        self._wait_for_polling_interval()
        self.worker.clear_task_definition_name_cache()


    def _poll_task(self) -> Task:
        task_definition_name = self.worker.get_task_definition_name()

        if self.worker.paused():
            logger.debug(f'Stop polling task for: {task_definition_name}')
            return None

        if self.metrics_collector is not None:
            self.metrics_collector.increment_task_poll(task_definition_name)

        logger.debug(f'Polling task for: {task_definition_name}')

        try:
            start_time = time.time()
            
            params = {'workerid': self.worker.get_identity()}
            
            domain = self.worker.get_domain()
            if domain != None:
                params['domain'] = domain
            
            task = self.task_client.poll(tasktype=task_definition_name, **params)
            
            finish_time = time.time()
            time_spent = finish_time - start_time

            if self.metrics_collector is not None:
                self.metrics_collector.record_task_poll_time(task_definition_name, time_spent)
        except Exception as e:
            if self.metrics_collector is not None:
                self.metrics_collector.increment_task_poll_error(task_definition_name, type(e))

            logger.error(f'Failed to poll task for: {task_definition_name}, reason: {traceback.format_exc()}')
            return None
        
        if task != None:
            logger.debug(f'Polled task: {task_definition_name}, worker_id: {self.worker.get_identity()}, domain: {self.worker.get_domain()}')

        return task


    def _execute_task(self, task: Task) -> TaskResult:
        if not isinstance(task, Task):
            return None

        task_definition_name = self.worker.get_task_definition_name()

        logger.debug('Executing task, id: {task_id}, workflow_instance_id: {workflow_instance_id}, task_definition_name: {task_definition_name}'.format(
                task_id=task.task_id,
                workflow_instance_id=task.workflow_instance_id,
                task_definition_name=task_definition_name
        ))

        try:
            start_time = time.time()
            
            task_result = self.worker.execute(task)
            
            finish_time = time.time()
            time_spent = finish_time - start_time
        
            if self.metrics_collector is not None:
                self.metrics_collector.record_task_execute_time(task_definition_name, time_spent)
                self.metrics_collector.record_task_result_payload_size(task_definition_name, sys.getsizeof(task_result))
        
            logger.debug('Executed task, id: {task_id}, workflow_instance_id: {workflow_instance_id}, task_definition_name: {task_definition_name}'.format(
                    task_id=task.task_id,
                    workflow_instance_id=task.workflow_instance_id,
                    task_definition_name=task_definition_name
            ))
        except Exception as e:
            if self.metrics_collector is not None:
                self.metrics_collector.increment_task_execution_error(task_definition_name, type(e))
            
            task_result = TaskResult(
                task_id=task.task_id,
                workflow_instance_id=task.workflow_instance_id,
                worker_id=self.worker.get_identity()
            )
            
            task_result.status = 'FAILED'
            task_result.reason_for_incompletion = str(e)
            task_result.logs = [
                TaskExecLog(traceback.format_exc(), task_result.task_id, int(time.time()))
            ]
            
            logger.error('Failed to execute task, id: {task_id}, workflow_instance_id: {workflow_instance_id}, task_definition_name: {task_definition_name}, reason: {reason}'.format(
                    task_id=task.task_id,
                    workflow_instance_id=task.workflow_instance_id,
                    task_definition_name=task_definition_name,
                    reason=traceback.format_exc()
            ))

        return task_result

    def _update_task(self, task_result: TaskResult):
        if not isinstance(task_result, TaskResult):
            return None
        
        task_definition_name = self.worker.get_task_definition_name()
        
        logger.debug('Updating task, id: {task_id}, workflow_instance_id: {workflow_instance_id}, task_definition_name: {task_definition_name}'.format(
                task_id=task_result.task_id,
                workflow_instance_id=task_result.workflow_instance_id,
                task_definition_name=task_definition_name
        ))

        for attempt in range(4):
            if attempt > 0:
                # Wait for [10s, 20s, 30s] before next attempt
                time.sleep(attempt * 10)

            try:
                response = self.task_client.update_task(body=task_result)
                
                logger.debug('Updated task, id: {task_id}, workflow_instance_id: {workflow_instance_id}, task_definition_name: {task_definition_name}, response: {response}'.format(
                        task_id=task_result.task_id,
                        workflow_instance_id=task_result.workflow_instance_id,
                        task_definition_name=task_definition_name,
                        response=response
                ))

                return response
            except Exception as e:
                if self.metrics_collector is not None:
                    self.metrics_collector.increment_task_update_error(task_definition_name, type(e))

                logger.error('Failed to update task, id: {task_id}, workflow_instance_id: {workflow_instance_id}, task_definition_name: {task_definition_name}, reason: {reason}'.format(
                        task_id=task_result.task_id,
                        workflow_instance_id=task_result.workflow_instance_id,
                        task_definition_name=task_definition_name,
                        reason=traceback.format_exc()
                ))

        return None

    def _wait_for_polling_interval(self) -> None:
        polling_interval = self.worker.get_polling_interval_in_seconds()
        logger.debug(f'Sleep for {polling_interval} seconds')
        time.sleep(polling_interval)

    def __set_worker_properties(self) -> None:
        task_type = self.worker.get_task_definition_name()
        
        # Fetch from ENV Variables if present
        domain = self.__get_property_value_from_env("domain", task_type)
        if domain:
            self.worker.domain = domain

        polling_interval_initialized = False
        polling_interval = self.__get_property_value_from_env("polling_interval", task_type)

        if polling_interval:
            try:
                self.worker.poll_interval = float(polling_interval)
                polling_interval_initialized = True
            except Exception as e:
                logger.error("Exception in reading polling interval from environment variable: {0}.".format(str(e)))

        # Fetch from Config if present
        if not domain or not polling_interval_initialized:
            config = self.worker_config

            if config:
                if config.has_section(task_type):
                    section = config[task_type]
                else:
                    section = config[config.default_section]
                
                # Override domain if present in config and not in ENV
                if not domain:
                    self.worker.domain = section.get("domain", self.worker.domain)

                # Override polling interval if present in config and not in ENV
                if not polling_interval_initialized:
                    # Setting to fallback poll interval before reading config
                    default_polling_interval = self.worker.poll_interval

                    try:
                        # Read polling interval from config
                        self.worker.poll_interval = float(section.get("polling_interval", default_polling_interval))
                        logger.debug("Override polling interval to {0} ms".format(self.worker.poll_interval))
                    except Exception as e:
                        logger.error("Exception reading polling interval: {0}. Defaulting to {1} ms".format(str(e), default_polling_interval))


    def __get_property_value_from_env(self, prop, task_type):
        prefix = "conductor_worker"

        # Look for generic property in both case environment variables
        key = prefix + "_" + prop
        value_all = os.getenv(key, os.getenv(key.upper()))

        # Look for task specific property in both case environment variables
        key_small = prefix + "_" + task_type + "_" + prop
        key_upper = prefix.upper() + "_" + task_type + "_" + prop.upper()
        value = os.getenv(key_small, os.getenv(key_upper, value_all))
        return value
