import json
from shortuuid import uuid

from conductor.client.configuration.configuration import Configuration
from conductor.client.http.api_client import ApiClient
from conductor.client.conductor_clients import ConductorClients
from conductor.client.workflow.conductor_workflow import ConductorWorkflow
from conductor.client.workflow.executor.workflow_executor import WorkflowExecutor
from conductor.client.workflow.task.simple_task import SimpleTask
from conductor.client.http.models.task_def import TaskDef
from conductor.client.http.models.task_result import TaskResult
from conductor.client.http.models.workflow_def import WorkflowDef
from conductor.client.http.models.target_ref import TargetRef, TargetType
from conductor.client.http.models.task_result_status import TaskResultStatus
from conductor.client.http.models.start_workflow_request import StartWorkflowRequest
from conductor.client.http.models.workflow_test_request import WorkflowTestRequest
from conductor.client.exceptions.api_error import APIError, APIErrorCode

SUFFIX = str(uuid())
WORKFLOW_NAME = 'IntegrationTestClientsWf_' + SUFFIX
TASK_TYPE = 'IntegrationTestClientsTask_' + SUFFIX
TEST_WF_JSON = 'tests/integration/resources/test_data/calculate_loan_workflow.json'
TEST_IP_JSON = 'tests/integration/resources/test_data/loan_workflow_input.json'
WORKFLOW_OWNER_EMAIL = "test@test"

class TestClients:
    def __init__(self, configuration: Configuration):
        self.api_client = ApiClient(configuration)
        self.workflow_executor = WorkflowExecutor(configuration)

        clients = ConductorClients(configuration)
        self.metadata_client = clients.getMetadataClient()
        self.workflow_client = clients.getWorkflowClient()
        self.task_client = clients.getTaskClient()
        self.workflow_id = None

    def run(self) -> None:
        workflow = ConductorWorkflow(
            executor=self.workflow_executor,
            name=WORKFLOW_NAME,
            description='Test Create Workflow',
            version=1
        )
        
        workflow.owner_email(WORKFLOW_OWNER_EMAIL)

        workflow.input_parameters(["a", "b"])
        workflow >> SimpleTask("simple_task", "simple_task_ref")
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
            name= TASK_TYPE,
            description="Integration Test Task",
            input_keys=["a", "b"]
        )

        self.metadata_client.registerTaskDef(taskDef)

        taskDef = self.metadata_client.getTaskDef(TASK_TYPE)
        assert taskDef.name == TASK_TYPE
        assert len(taskDef.input_keys) == 2

        taskDef.description = "Integration Test Task New Description"
        taskDef.input_keys = ["a", "b", "c"]
        self.metadata_client.updateTaskDef(taskDef)
        fetchedTaskDef = self.metadata_client.getTaskDef(taskDef.name)
        assert fetchedTaskDef.description == taskDef.description
        assert len(fetchedTaskDef.input_keys) == 3

        self.__test_task_tags()
        self.__test_task_execution_lifecycle()

        self.metadata_client.unregisterTaskDef(TASK_TYPE)
        try:
            self.metadata_client.getTaskDef(TASK_TYPE)
        except APIError as e:
            assert e.code == APIErrorCode.NOT_FOUND
            assert e.message == "Task {0} not found".format(TASK_TYPE)


    
    def __test_register_workflow_definition(self, workflowDef: WorkflowDef):
        self.__create_workflow_definition(workflowDef)
    
    def __create_workflow_definition(self, workflowDef) -> str:
        return self.metadata_client.registerWorkflowDef(workflowDef, True)

    def __test_get_workflow_definition(self):
        wfDef = self.metadata_client.getWorkflowDef(WORKFLOW_NAME)
        assert wfDef.name == WORKFLOW_NAME
        assert len(wfDef.tasks) == 1

    def __test_update_workflow_definition(self, workflow: ConductorWorkflow):
        workflow >> SimpleTask("simple_task", "simple_task_ref_2")
        workflow >> SimpleTask("simple_task", "simple_task_ref_3")
        workflow.workflow_id = self.workflow_id
        updatedWorkflowDef = workflow.to_workflow_def()
        self.metadata_client.updateWorkflowDef(updatedWorkflowDef, True)
        wfDef = self.metadata_client.getWorkflowDef(WORKFLOW_NAME)
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

        execution = self.workflow_client.testWorkflow(testRequest)
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
        self.metadata_client.unregisterWorkflowDef(WORKFLOW_NAME, 1)
        
        try:
            self.metadata_client.getWorkflowDef(WORKFLOW_NAME, 1)
        except APIError as e:
            assert e.code == APIErrorCode.NOT_FOUND
            assert e.message ==  'No such workflow found by name: {0}, version: 1'.format(WORKFLOW_NAME)

    def __test_workflow_execution_lifecycle(self):
        wfInput = { "a" : 5, "b": "+", "c" : [7, 8] }
        workflow_uuid = self.workflow_client.startWorkflowByName(WORKFLOW_NAME, wfInput)
        assert workflow_uuid is not None

        workflow = self.workflow_client.getWorkflow(workflow_uuid, False)
        assert workflow.input["a"] == 5
        assert workflow.input["b"] == "+"
        assert workflow.input["c"] == [7, 8]
        assert workflow.status == "RUNNING"

        self.workflow_client.pauseWorkflow(workflow_uuid)
        workflow = self.workflow_client.getWorkflow(workflow_uuid, False)
        assert workflow.status == "PAUSED"

        self.workflow_client.resumeWorkflow(workflow_uuid)
        workflow = self.workflow_client.getWorkflow(workflow_uuid, False)
        assert workflow.status == "RUNNING"

        self.workflow_client.terminateWorkflow(workflow_uuid, "Integration Test")
        workflow = self.workflow_client.getWorkflow(workflow_uuid, False)
        assert workflow.status == "TERMINATED"

        self.workflow_client.restartWorkflow(workflow_uuid)
        workflow = self.workflow_client.getWorkflow(workflow_uuid, False)
        assert workflow.status == "RUNNING"
        
        self.workflow_client.skipTaskFromWorkflow(workflow_uuid, "simple_task_ref_2")
        workflow = self.workflow_client.getWorkflow(workflow_uuid, False)
        assert workflow.status == "RUNNING"

        self.workflow_client.deleteWorkflow(workflow_uuid)
        try:
            workflow = self.workflow_client.getWorkflow(workflow_uuid, False)
        except APIError as e:
            assert e.code == APIErrorCode.NOT_FOUND
            assert e.message == "Workflow with Id: {} not found.".format(workflow_uuid)

    def __test_task_execution_lifecycle(self):
        
        workflow = ConductorWorkflow(
            executor=self.workflow_executor,
            name=WORKFLOW_NAME + "_task",
            description='Test Task Client Workflow',
            version=1
        )
        workflow.input_parameters(["a", "b"])
        workflow >> SimpleTask(TASK_TYPE, "simple_task_ref")
        workflow >> SimpleTask(TASK_TYPE, "simple_task_ref_2")
        
        startWorkflowRequest = StartWorkflowRequest(
            name=WORKFLOW_NAME + "_task",
            version=1,
            workflow_def=workflow.to_workflow_def(),
            input={ "a" : 15, "b": 3, "op" : "+" }
        )
        
        workflow_uuid = self.workflow_client.startWorkflow(startWorkflowRequest)
        workflow = self.workflow_client.getWorkflow(workflow_uuid, False)
        
        workflow_uuid_2 = self.workflow_client.startWorkflow(startWorkflowRequest)
        
        # First task of each workflow is in the queue
        assert self.task_client.getQueueSizeForTask(TASK_TYPE) == 2
        
        polledTask = self.task_client.pollTask(TASK_TYPE)
        assert polledTask.status == TaskResultStatus.IN_PROGRESS
        
        self.task_client.addTaskLog(polledTask.task_id, "Polled task...")
        
        taskExecLogs = self.task_client.getTaskLogs(polledTask.task_id)
        taskExecLogs[0].log == "Polled task..."
        
        # First task of second workflow is in the queue
        assert self.task_client.getQueueSizeForTask(TASK_TYPE) == 1
        
        taskResult = TaskResult(
            workflow_instance_id=workflow_uuid,
            task_id=polledTask.task_id,
            status=TaskResultStatus.COMPLETED
        )
        
        self.task_client.updateTask(taskResult)
        
        task = self.task_client.getTask(polledTask.task_id)
        assert task.status == TaskResultStatus.COMPLETED
        
        batchPolledTasks = self.task_client.batchPollTasks(TASK_TYPE)
        assert len(batchPolledTasks) == 1

        polledTask = batchPolledTasks[0]
        # Update first task of second workflow
        self.task_client.updateTaskByRefName(
            workflow_uuid_2,
            polledTask.reference_task_name,
            "COMPLETED",
            "task 2 op 2nd wf"
        )
        
        # Update second task of first workflow
        self.task_client.updateTaskByRefName(
            workflow_uuid_2, "simple_task_ref_2", "COMPLETED", "task 2 op 1st wf"
        )
        
        # # Second task of second workflow is in the queue
        # assert self.task_client.getQueueSizeForTask(TASK_TYPE) == 1
        polledTask = self.task_client.pollTask(TASK_TYPE)

        # Update second task of second workflow
        self.task_client.updateTaskSync(
            workflow_uuid, "simple_task_ref_2", "COMPLETED", "task 1 op 2nd wf"
        )
        
        assert self.task_client.getQueueSizeForTask(TASK_TYPE) == 0

    def __get_workflow_definition(self, path):
        f = open(path, "r")
        workflowJSON = json.loads(f.read())
        workflowDef = self.api_client.deserialize_class(workflowJSON, "WorkflowDef")
        return workflowDef
    
    def __get_test_inputs(self, path):
        f = open(path, "r")
        inputJSON = json.loads(f.read())
        return inputJSON