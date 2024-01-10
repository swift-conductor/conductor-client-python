import logging
import unittest
import json

from unittest.mock import Mock, patch, MagicMock

from swift_conductor.clients.task_client import TaskClient
from swift_conductor.configuration import Configuration
from swift_conductor.http.models.task import Task
from swift_conductor.http.rest import ApiException
from swift_conductor.http.api.task_resource_api import TaskResourceApi
from swift_conductor.task.task_type import TaskType
from swift_conductor.http.models.task_exec_log import TaskExecLog
from swift_conductor.http.models.task_result import TaskResult
from swift_conductor.http.models.task_result_status import TaskResultStatus
from swift_conductor.http.models.workflow import Workflow
from swift_conductor.exceptions.api_error import APIError

TASK_NAME = 'ut_task'
TASK_ID = 'task_id_1'
TASK_NAME_2 = 'ut_task_2'
WORKER_ID = "ut_worker_id"
DOMAIN = "test_domain"

class TestTaskClient(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        configuration = Configuration("http://localhost:8080/api")
        cls.task_client = TaskClient(configuration)
        
    def setUp(self):
        self.tasks = [
            Task(task_type=TaskType.CUSTOM, task_def_name=TASK_NAME, reference_task_name="custom_task_ref_1", task_id=TASK_ID),
            Task(task_type=TaskType.CUSTOM, task_def_name=TASK_NAME, reference_task_name="custom_task_ref_2", task_id="task_id_2"),
            Task(task_type=TaskType.CUSTOM, task_def_name=TASK_NAME, reference_task_name="custom_task_ref_3", task_id="task_id_3"),
        ]
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_init(self):
        message = "taskResourceApi is not of type TaskResourceApi"
        self.assertIsInstance(self.task_client.taskResourceApi, TaskResourceApi, message)

    @patch.object(TaskResourceApi, 'poll')
    def test_pollTask(self, mock):
        mock.return_value = self.tasks[0]
        polledTask = self.task_client.poll_task(TASK_NAME)
        mock.assert_called_with(TASK_NAME)
        self.assertEqual(polledTask, self.tasks[0])

    @patch.object(TaskResourceApi, 'poll')
    def test_pollTask_with_worker_and_domain(self, mock):
        mock.return_value = self.tasks[0]
        polledTask = self.task_client.poll_task(TASK_NAME, WORKER_ID, DOMAIN)
        mock.assert_called_with(TASK_NAME, workerid=WORKER_ID, domain=DOMAIN)
        self.assertEqual(polledTask, self.tasks[0])
    
    @patch.object(TaskResourceApi, 'poll')
    def test_pollTask_no_tasks(self, mock):
        mock.return_value = None
        polledTask = self.task_client.poll_task(TASK_NAME)
        mock.assert_called_with(TASK_NAME)
        self.assertIsNone(polledTask)
    
    @patch.object(TaskResourceApi, 'batch_poll')
    def test_batchPollTasks(self, mock):
        mock.return_value = self.tasks
        polledTasks = self.task_client.batch_poll_tasks(TASK_NAME, WORKER_ID, 3, 200)
        mock.assert_called_with(TASK_NAME, workerid=WORKER_ID, count=3, timeout=200)
        self.assertEqual(len(polledTasks), len(self.tasks))
    
    @patch.object(TaskResourceApi, 'batch_poll')
    def test_batchPollTasks_in_domain(self, mock):
        mock.return_value = self.tasks
        polledTasks = self.task_client.batch_poll_tasks(TASK_NAME, WORKER_ID, 3, 200, DOMAIN)
        mock.assert_called_with(TASK_NAME, workerid=WORKER_ID, domain=DOMAIN, count=3, timeout=200)
        self.assertEqual(len(polledTasks), len(self.tasks))
    
    @patch.object(TaskResourceApi, 'get_task')
    def test_getTask(self, mock):
        mock.return_value = self.tasks[0]
        task = self.task_client.get_task(TASK_ID)
        mock.assert_called_with(TASK_ID)
        self.assertEqual(task.task_id, TASK_ID)

    @patch.object(TaskResourceApi, 'get_task')
    def test_getTask_non_existent(self, mock):
        error_body = { 'status': 404, 'message': 'Task not found' }
        mock.side_effect = MagicMock(side_effect=ApiException(status=404, body=json.dumps(error_body)))
        with self.assertRaises(APIError):
            self.task_client.get_task(TASK_ID)
            mock.assert_called_with(TASK_ID)
        
    @patch.object(TaskResourceApi, 'update_task')
    def test_updateTask(self, mock):
        taskResultStatus = TaskResult(task_id=TASK_ID, status=TaskResultStatus.COMPLETED)
        self.task_client.update_task(taskResultStatus)
        mock.assert_called_with(taskResultStatus)
    
    @patch.object(TaskResourceApi, 'size')
    def test_getQueueSizeForTask(self, mock):
        mock.return_value = { TASK_NAME: 4 }
        size = self.task_client.get_queue_size_for_task(TASK_NAME)
        mock.assert_called_with(task_type=[TASK_NAME])
        self.assertEqual(size, 4)
    
    @patch.object(TaskResourceApi, 'size')
    def test_getQueueSizeForTask_empty(self, mock):
        mock.return_value = {}
        size = self.task_client.get_queue_size_for_task(TASK_NAME)
        mock.assert_called_with(task_type=[TASK_NAME])
        self.assertEqual(size, 0)

    @patch.object(TaskResourceApi, 'log')
    def test_addTaskLog(self, mock):
        logMessage = "Test log"
        self.task_client.add_task_log(TASK_ID, logMessage)
        mock.assert_called_with(logMessage, TASK_ID)

    @patch.object(TaskResourceApi, 'get_task_logs')
    def test_getTaskLogs(self, mock):
        taskExecLog1 = TaskExecLog("Test log 1", TASK_ID)
        taskExecLog2 = TaskExecLog("Test log 2", TASK_ID)
        mock.return_value = [taskExecLog1, taskExecLog2]
        logs = self.task_client.get_task_logs(TASK_ID)
        mock.assert_called_with(TASK_ID)
        self.assertEqual(len(logs), 2)
