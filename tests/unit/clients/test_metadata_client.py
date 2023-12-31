import logging
import unittest
import json

from unittest.mock import Mock, patch, MagicMock
from conductor.client.http.rest import ApiException
from conductor.client.clients.metadata_client import MetadataClient
from conductor.client.http.api.metadata_resource_api import MetadataResourceApi
from conductor.client.configuration.configuration import Configuration
from conductor.client.http.models.workflow_def import WorkflowDef
from conductor.client.http.models.task_def import TaskDef
from conductor.client.exceptions.api_error import APIError

WORKFLOW_NAME = 'ut_wf'
TASK_NAME = 'ut_task'

class TestMetadataClient(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        configuration = Configuration("http://localhost:8080/api")
        cls.metadata_client = MetadataClient(configuration)
        
    def setUp(self):
        self.workflowDef = WorkflowDef(name=WORKFLOW_NAME, version=1)
        self.taskDef = TaskDef(TASK_NAME)
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_init(self):
        message = "metadataResourceApi is not of type MetadataResourceApi"
        self.assertIsInstance(self.metadata_client.metadataResourceApi, MetadataResourceApi, message)

    @patch.object(MetadataResourceApi, 'create')
    def test_registerWorkflowDef(self, mock):
        self.metadata_client.registerWorkflowDef(self.workflowDef)
        self.assertTrue(mock.called)
        mock.assert_called_with(self.workflowDef, overwrite=True)

    @patch.object(MetadataResourceApi, 'create')
    def test_registerWorkflowDef_without_overwrite(self, mock):
        self.metadata_client.registerWorkflowDef(self.workflowDef, False)
        self.assertTrue(mock.called)
        mock.assert_called_with(self.workflowDef, overwrite=False)

    @patch.object(MetadataResourceApi, 'update1')
    def test_updateWorkflowDef(self, mock):
        self.metadata_client.updateWorkflowDef(self.workflowDef)
        self.assertTrue(mock.called)
        mock.assert_called_with([self.workflowDef], overwrite=True)

    @patch.object(MetadataResourceApi, 'update1')
    def test_updateWorkflowDef_without_overwrite(self, mock):
        self.metadata_client.updateWorkflowDef(self.workflowDef, False)
        self.assertTrue(mock.called)
        mock.assert_called_with([self.workflowDef], overwrite=False)

    @patch.object(MetadataResourceApi, 'unregister_workflow_def')
    def test_unregisterWorkflowDef(self, mock):
        self.metadata_client.unregisterWorkflowDef(WORKFLOW_NAME, 1)
        self.assertTrue(mock.called)
        mock.assert_called_with(WORKFLOW_NAME, 1)
        
    @patch.object(MetadataResourceApi, 'get')
    def test_getWorkflowDef_without_version(self, mock):
        mock.return_value = self.workflowDef
        wf = self.metadata_client.getWorkflowDef(WORKFLOW_NAME)
        self.assertEqual(wf, self.workflowDef)
        self.assertTrue(mock.called)
        mock.assert_called_with(WORKFLOW_NAME)
    
    @patch.object(MetadataResourceApi, 'get')
    def test_getWorkflowDef_with_version(self, mock):
        mock.return_value = self.workflowDef
        wf = self.metadata_client.getWorkflowDef(WORKFLOW_NAME, 1)
        self.assertEqual(wf, self.workflowDef)
        mock.assert_called_with(WORKFLOW_NAME, version=1)
    
    @patch.object(MetadataResourceApi, 'get')
    def test_getWorkflowDef_non_existent(self, mock):
        message = 'No such workflow found by name:' + WORKFLOW_NAME + ', version: null'
        error_body = { 'status': 404, 'message': message }
        mock.side_effect = MagicMock(side_effect=ApiException(status=404, body=json.dumps(error_body)))
        with self.assertRaises(APIError):
            self.metadata_client.getWorkflowDef(WORKFLOW_NAME)
        
    @patch.object(MetadataResourceApi, 'get_all_workflows')
    def test_getAllWorkflowDefs(self, mock):
        workflowDef2 = WorkflowDef(name='ut_wf_2', version=1)
        mock.return_value = [self.workflowDef, workflowDef2]
        wfs = self.metadata_client.getAllWorkflowDefs()
        self.assertEqual(len(wfs), 2)
    
    @patch.object(MetadataResourceApi, 'register_task_def')
    def test_registerTaskDef(self, mock):
        self.metadata_client.registerTaskDef(self.taskDef)
        self.assertTrue(mock.called)
        mock.assert_called_with([self.taskDef])
    
    @patch.object(MetadataResourceApi, 'update_task_def')
    def test_updateTaskDef(self, mock):
        self.metadata_client.updateTaskDef(self.taskDef)
        self.assertTrue(mock.called)
        mock.assert_called_with(self.taskDef)
    
    @patch.object(MetadataResourceApi, 'unregister_task_def')
    def test_unregisterTaskDef(self, mock):
        self.metadata_client.unregisterTaskDef(TASK_NAME)
        self.assertTrue(mock.called)
        mock.assert_called_with(TASK_NAME)

    @patch.object(MetadataResourceApi, 'get_task_def')
    def test_getTaskDef(self, mock):
        mock.return_value = self.taskDef
        taskDefinition = self.metadata_client.getTaskDef(TASK_NAME)
        self.assertEqual(taskDefinition, self.taskDef)
        mock.assert_called_with(TASK_NAME)

    @patch.object(MetadataResourceApi, 'get_task_defs')
    def test_getAllTaskDefs(self, mock):
        taskDef2 = TaskDef("ut_task2")
        mock.return_value = [self.taskDef, taskDef2]
        tasks = self.metadata_client.getAllTaskDefs()
        self.assertEqual(len(tasks), 2)
