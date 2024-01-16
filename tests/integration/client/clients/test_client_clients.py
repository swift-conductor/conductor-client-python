import json
import time
from shortuuid import uuid

from swift_conductor.configuration import Configuration
from swift_conductor.http.api_client import ApiClient
from swift_conductor.exceptions.api_error import APIError, APIErrorCode

from swift_conductor.clients.metadata_client import MetadataClient
from swift_conductor.clients.workflow_client import WorkflowClient
from swift_conductor.clients.task_client import TaskClient

from swift_conductor.workflow.workflow_builder import WorkflowBuilder
from swift_conductor.workflow.workflow_manager import WorkflowManager

from swift_conductor.task.custom_task import CustomTask

from swift_conductor.http.models.workflow_def import WorkflowDef
from swift_conductor.http.models.task_def import TaskDef

from swift_conductor.http.models.task_result import TaskResult
from swift_conductor.http.models.task_result_status import TaskResultStatus

from swift_conductor.http.models.start_workflow_request import StartWorkflowRequest
from swift_conductor.http.models.workflow_test_request import WorkflowTestRequest

SUFFIX = str(uuid())
WORKFLOW_DEF_NAME = 'python_e2e_test_workflow_def_' + SUFFIX
TASK_DEF_NAME = 'python_e2e_test_task_def_' + SUFFIX

TEST_WF_JSON = 'tests/integration/resources/test_data/calculate_loan_workflow.json'
TEST_IP_JSON = 'tests/integration/resources/test_data/loan_workflow_input.json'

WF_OWNER_EMAIL = "test@test.com"

class TestClients:
    def __init__(self, configuration: Configuration):
        self.api_client = ApiClient(configuration)
        
        self.workflow_manager = WorkflowManager(configuration)

        self.metadata_client = MetadataClient(configuration)
        self.workflow_client = WorkflowClient(configuration)
        self.task_client = TaskClient(configuration)

        self.workflow_id = None

        
    def run(self) -> None:
        workflow = WorkflowBuilder(WORKFLOW_DEF_NAME, 1, 'Test Create Workflow').owner_email(WF_OWNER_EMAIL)

        workflow.input_parameters(["a", "b"])
        workflow >> CustomTask("custom_task", "custom_task_ref")
        workflowDef = workflow.to_workflow_def()
        
        self.test_workflow_lifecycle(workflowDef, workflow)
        self.test_task_lifecycle()
        self.__test_unit_test_workflow()

    def test_workflow_lifecycle(self, workflowDef, workflow):
        self.__test_register_workflow_definition(workflowDef)
        self.__test_get_workflow_definition()
        self.__test_update_workflow_definition(workflow)
        self.__test_workflow_execution_lifecycle()
        self.__test_unregister_workflow_definition()

    def test_task_lifecycle(self):
        taskDef = TaskDef(
            name= TASK_DEF_NAME,
            description="Integration Test Task",
            input_keys=["a", "b"]
        )

        taskDef.owner_email = 'test@test.com'

        self.metadata_client.register_task_def(taskDef)

        taskDef = self.metadata_client.get_task_def(TASK_DEF_NAME)
        assert taskDef.name == TASK_DEF_NAME
        assert len(taskDef.input_keys) == 2

        taskDef.description = "Integration Test Task New Description"
        taskDef.input_keys = ["a", "b", "c"]
        self.metadata_client.update_task_def(taskDef)
        fetchedTaskDef = self.metadata_client.get_task_def(taskDef.name)
        assert fetchedTaskDef.description == taskDef.description
        assert len(fetchedTaskDef.input_keys) == 3

        self.__test_task_execution_lifecycle()

        self.metadata_client.unregister_task_def(TASK_DEF_NAME)
        
        try:
            self.metadata_client.get_task_def(TASK_DEF_NAME)
        except APIError as e:
            assert e.code == APIErrorCode.NOT_FOUND
            assert e.message == "No such taskType found by name: {0}".format(TASK_DEF_NAME)


    
    def __test_register_workflow_definition(self, workflowDef: WorkflowDef):
        self.__create_workflow_definition(workflowDef)
    
    def __create_workflow_definition(self, workflowDef) -> str:
        return self.metadata_client.register_workflow_def(workflowDef)

    def __test_get_workflow_definition(self):
        wfDef = self.metadata_client.get_workflow_def(WORKFLOW_DEF_NAME)
        assert wfDef.name == WORKFLOW_DEF_NAME
        assert len(wfDef.tasks) == 1

    def __test_update_workflow_definition(self, workflow: WorkflowBuilder):
        workflow >> CustomTask("custom_task", "custom_task_ref_2")
        workflow >> CustomTask("custom_task", "custom_task_ref_3")
        workflow.workflow_id = self.workflow_id
        updatedWorkflowDef = workflow.to_workflow_def()
        self.metadata_client.update_workflow_def(updatedWorkflowDef)
        wfDef = self.metadata_client.get_workflow_def(WORKFLOW_DEF_NAME)
        assert len(wfDef.tasks) == 3

    def __test_unit_test_workflow(self):
        workflowDef = self.__get_workflow_definition(TEST_WF_JSON)
        assert workflowDef != None
        
        testTaskInputs = self.__get_test_inputs(TEST_IP_JSON)
        assert testTaskInputs != None

        testRequest = WorkflowTestRequest(name=workflowDef.name, workflow_def=workflowDef)

        testRequest.input = {
            "userEmail": "user@example.com",
            "loanAmount": 11000,
        }
        
        testRequest.name = workflowDef.name
        testRequest.version = workflowDef.version
        testRequest.task_ref_to_mock_output = testTaskInputs

        execution = self.workflow_client.test_workflow(testRequest)
        assert execution != None
        
        # Ensure workflow is completed successfully
        assert execution.status == "COMPLETED"
        
        # Ensure the inputs were captured correctly
        assert execution.input["loanAmount"] == testRequest.input["loanAmount"]
        assert execution.input["userEmail"] == testRequest.input["userEmail"]

        # A total of 7 tasks were executed
        assert len(execution.tasks) == 7

        fetchUserDetails = execution.tasks[0]
        getCreditScore = execution.tasks[1]
        calculateLoanAmount = execution.tasks[2]
        phoneNumberValidAttempt1 = execution.tasks[4]
        phoneNumberValidAttempt2 = execution.tasks[5]
        phoneNumberValidAttempt3 = execution.tasks[6]

        # fetch user details received the correct input from the workflow
        assert fetchUserDetails.input_data["userEmail"] == testRequest.input["userEmail"]

        userAccountNo = 12345
        # And that the task produced the right output
        assert fetchUserDetails.output_data["userAccount"] == userAccountNo

        # get credit score received the right account number from the output of the fetch user details
        assert getCreditScore.input_data["userAccountNumber"] == userAccountNo

        # The task produced the right output
        expectedCreditRating = 750
        assert getCreditScore.output_data["creditRating"] == expectedCreditRating

        # Calculate loan amount gets the right loan amount from workflow input
        expectedLoanAmount = testRequest.input["loanAmount"]
        assert calculateLoanAmount.input_data["loanAmount"] == expectedLoanAmount
        
        # Calculate loan amount gets the right credit rating from the previous task
        assert calculateLoanAmount.input_data["creditRating"] == expectedCreditRating
        
        authorizedLoanAmount = 10_000
        assert calculateLoanAmount.output_data["authorizedLoanAmount"] == authorizedLoanAmount
        
        assert not phoneNumberValidAttempt1.output_data["valid"]
        assert not phoneNumberValidAttempt2.output_data["valid"]
        assert phoneNumberValidAttempt3.output_data["valid"]

        # Finally, lets verify the workflow outputs
        assert execution.output["accountNumber"] == userAccountNo
        assert execution.output["creditRating"] == expectedCreditRating
        assert execution.output["authorizedLoanAmount"] == authorizedLoanAmount
        
        # Workflow output takes the latest iteration output of a loopOver task.
        assert execution.output["phoneNumberValid"]

    def __test_unregister_workflow_definition(self):
        self.metadata_client.unregister_workflow_def(WORKFLOW_DEF_NAME, 1)
        
        try:
            self.metadata_client.get_workflow_def(WORKFLOW_DEF_NAME, 1)
        except APIError as e:
            assert e.code == APIErrorCode.NOT_FOUND
            assert e.message ==  'No such workflow found by name: {0}, version: 1'.format(WORKFLOW_DEF_NAME)

    def __test_workflow_execution_lifecycle(self):
        wfInput = { "a" : 5, "b": "+", "c" : [7, 8] }
        workflow_uuid = self.workflow_client.start_workflow_by_name(WORKFLOW_DEF_NAME, wfInput)
        assert workflow_uuid is not None

        workflow = self.workflow_client.get_workflow(workflow_uuid, False)
        assert workflow.input["a"] == 5
        assert workflow.input["b"] == "+"
        assert workflow.input["c"] == [7, 8]
        assert workflow.status == "RUNNING"

        self.workflow_client.pause_workflow(workflow_uuid)
        workflow = self.workflow_client.get_workflow(workflow_uuid, False)
        assert workflow.status == "PAUSED"

        self.workflow_client.resumeWorkflow(workflow_uuid)
        workflow = self.workflow_client.get_workflow(workflow_uuid, False)
        assert workflow.status == "RUNNING"

        self.workflow_client.terminate_workflow(workflow_uuid, "Integration Test")
        workflow = self.workflow_client.get_workflow(workflow_uuid, False)
        assert workflow.status == "TERMINATED"

        self.workflow_client.restart_workflow(workflow_uuid)
        workflow = self.workflow_client.get_workflow(workflow_uuid, False)
        assert workflow.status == "RUNNING"
        
        self.workflow_client.skip_task_from_workflow(workflow_uuid, "custom_task_ref_2")
        workflow = self.workflow_client.get_workflow(workflow_uuid, False)
        assert workflow.status == "RUNNING"

        self.workflow_client.terminate_workflow(workflow_uuid, "Integration Test")
        self.workflow_client.delete_workflow(workflow_uuid)

        try:
            workflow = self.workflow_client.get_workflow(workflow_uuid, False)
        except APIError as e:
            assert e.code == APIErrorCode.NOT_FOUND
            assert e.message == "Workflow with Id: {} not found.".format(workflow_uuid)

    def __test_task_execution_lifecycle(self):
        # Create Workflow definitions    
        workflow_builder = WorkflowBuilder(
            name=WORKFLOW_DEF_NAME + "_inst",
            version=1,
            description='Test Task Client Workflow'
        ).owner_email(WF_OWNER_EMAIL)

        workflow_builder.input_parameters(["a", "b"])
        _ = workflow_builder >> CustomTask(TASK_DEF_NAME, "custom_task_ref_1")
        _ = workflow_builder >> CustomTask(TASK_DEF_NAME, "custom_task_ref_2")
        
        workflow_def = workflow_builder.to_workflow_def()

        # start 2 instances of the same WorkflowDef
        # first instance
        start_workflow_request = StartWorkflowRequest(
            name=WORKFLOW_DEF_NAME + "_inst_1",
            version=1,
            workflow_def=workflow_def,
            input={ "a" : 15, "b": 3, "op" : "+" }
        )
        
        workflow_uuid_1 = self.workflow_client.start_workflow(start_workflow_request)
        workflow_instance_1 = self.workflow_client.get_workflow(workflow_uuid_1, False)

        # second instance
        start_workflow_request = StartWorkflowRequest(
            name=WORKFLOW_DEF_NAME + "_inst_2",
            version=1,
            workflow_def=workflow_def,
            input={ "a" : 15, "b": 3, "op" : "+" }
        )

        workflow_uuid_2 = self.workflow_client.start_workflow(start_workflow_request)
        workflow_instance_2 = self.workflow_client.get_workflow(workflow_uuid_2, False)
        
        # task 1 of each workflow instance is in the queue
        assert self.task_client.get_queue_size_for_task(TASK_DEF_NAME) == 2
        
        polled_task = self.task_client.poll_task(TASK_DEF_NAME)
        assert polled_task.status == TaskResultStatus.IN_PROGRESS
        
        self.task_client.add_task_log(polled_task.task_id, "Polled task...")
        
        # give server time to update it's state
        time.sleep(5)
        
        task_logs = self.task_client.get_task_logs(polled_task.task_id)
        assert task_logs[0].log == '"Polled task..."'
        
        # complete task 1 in workflow 1
        task_result = TaskResult(workflow_instance_id=workflow_uuid_1, task_id=polled_task.task_id, status=TaskResultStatus.COMPLETED)
        self.task_client.update_task(task_result)
        
        task = self.task_client.get_task(polled_task.task_id)
        assert task.status == TaskResultStatus.COMPLETED

        # give server time to update it's state
        time.sleep(5)

        # queue: [task 1 of workflow 2, task 2 of workflow 1]
        task_queue_size = self.task_client.get_queue_size_for_task(TASK_DEF_NAME)
        assert task_queue_size == 2

        # get task 1 from workflow 2
        batch_polled_tasks = self.task_client.batch_poll_tasks(TASK_DEF_NAME)
        assert len(batch_polled_tasks) == 1

        # Complete task 1 of workflow 2
        polled_task = batch_polled_tasks[0]
        task_result = TaskResult(workflow_instance_id=workflow_uuid_2, task_id=polled_task.task_id, status=TaskResultStatus.COMPLETED)
        self.task_client.update_task(task_result)

        batch_polled_tasks = self.task_client.batch_poll_tasks(TASK_DEF_NAME)
        assert len(batch_polled_tasks) == 1

        # Complete task 2 of workflow 1
        polled_task = batch_polled_tasks[0]
        task_result = TaskResult(workflow_instance_id=workflow_uuid_1, task_id=polled_task.task_id, status=TaskResultStatus.COMPLETED)
        self.task_client.update_task(task_result)

        assert self.task_client.get_queue_size_for_task(TASK_DEF_NAME) == 1

        # task 2 of workflow 2 is in the queue
        polled_task = self.task_client.poll_task(TASK_DEF_NAME)

        # Complete task 2 of workflow 2
        task_result = TaskResult(workflow_instance_id=workflow_uuid_2, task_id=polled_task.task_id, status=TaskResultStatus.COMPLETED)
        self.task_client.update_task(task_result)
        
        # queue should be empty
        assert self.task_client.get_queue_size_for_task(TASK_DEF_NAME) == 0


    def __get_workflow_definition(self, path):
        f = open(path, "r")
        workflowJSON = json.loads(f.read())
        workflowDef = self.api_client.deserialize_class(workflowJSON, "WorkflowDef")
        return workflowDef
    
    def __get_test_inputs(self, path):
        f = open(path, "r")
        inputJSON = json.loads(f.read())
        return inputJSON