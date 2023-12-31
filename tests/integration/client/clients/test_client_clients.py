import json
from shortuuid import uuid
from conductor.client.configuration.configuration import Configuration
from conductor.client.http.api_client import ApiClient
from conductor.client.conductor_clients import ConductorClients
from conductor.client.workflow.conductor_workflow import ConductorWorkflow
from conductor.client.workflow.executor.workflow_executor import WorkflowExecutor
from conductor.client.workflow.task.simple_task import SimpleTask
from conductor.client.clients.models.access_type import AccessType
from conductor.client.clients.models.access_key_status import AccessKeyStatus
from conductor.client.clients.models.metadata_tag import MetadataTag
from conductor.client.http.models.task_def import TaskDef
from conductor.client.http.models.task_result import TaskResult
from conductor.client.http.models.workflow_def import WorkflowDef
from conductor.client.http.models.target_ref import TargetRef, TargetType
from conductor.client.http.models.subject_ref import SubjectRef, SubjectType
from conductor.client.http.models.task_result_status import TaskResultStatus
from conductor.client.http.models.save_schedule_request import SaveScheduleRequest
from conductor.client.http.models.start_workflow_request import StartWorkflowRequest
from conductor.client.http.models.upsert_user_request import UpsertUserRequest
from conductor.client.http.models.upsert_group_request import UpsertGroupRequest
from conductor.client.http.models.create_or_update_application_request import CreateOrUpdateApplicationRequest
from conductor.client.http.models.workflow_test_request import WorkflowTestRequest
from conductor.client.exceptions.api_error import APIError, APIErrorCode

SUFFIX = str(uuid())
WORKFLOW_NAME = 'IntegrationTestClientsWf_' + SUFFIX
TASK_TYPE = 'IntegrationTestClientsTask_' + SUFFIX
SCHEDULE_NAME = 'IntegrationTestSchedulerClientSch_' + SUFFIX
SECRET_NAME = 'IntegrationTestSecretClientSec_' + SUFFIX
APPLICATION_NAME = 'IntegrationTestAuthClientApp_' + SUFFIX
USER_ID = 'integrationtest_' + SUFFIX[0:5].lower() + "@swiftconductor.com"
GROUP_ID = 'integrationtest_group_' + SUFFIX[0:5].lower()
TEST_WF_JSON = 'tests/integration/resources/test_data/calculate_loan_workflow.json'
TEST_IP_JSON = 'tests/integration/resources/test_data/loan_workflow_input.json'

class TestClients:
    def __init__(self, configuration: Configuration):
        self.api_client = ApiClient(configuration)
        self.workflow_executor = WorkflowExecutor(configuration)

        clients = ConductorClients(configuration)
        self.metadata_client = clients.getMetadataClient()
        self.workflow_client = clients.getWorkflowClient()
        self.task_client = clients.getTaskClient()
        self.scheduler_client = clients.getSchedulerClient()
        self.secret_client = clients.getSecretClient()
        self.authorization_client = clients.getAuthorizationClient()
        self.workflow_id = None

    def run(self) -> None:
        workflow = ConductorWorkflow(
            executor=self.workflow_executor,
            name=WORKFLOW_NAME,
            description='Test Create Workflow',
            version=1
        )
        workflow.input_parameters(["a", "b"])
        workflow >> SimpleTask("simple_task", "simple_task_ref")
        workflowDef = workflow.to_workflow_def()
        
        self.test_workflow_lifecycle(workflowDef, workflow)
        self.test_task_lifecycle()
        self.test_secret_lifecycle()
        self.test_scheduler_lifecycle(workflowDef)
        self.test_application_lifecycle()
        self.test_user_group_permissions_lifecycle(workflowDef)
        self.__test_unit_test_workflow()

    def test_workflow_lifecycle(self, workflowDef, workflow):
        self.__test_register_workflow_definition(workflowDef)
        self.__test_get_workflow_definition()
        self.__test_update_workflow_definition(workflow)
        self.__test_workflow_execution_lifecycle()
        self.__test_workflow_tags()
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


    def test_secret_lifecycle(self):
        self.secret_client.putSecret(SECRET_NAME, "secret_value")
        
        assert self.secret_client.getSecret(SECRET_NAME), "secret_value"
        
        self.secret_client.putSecret(SECRET_NAME + "_2", "secret_value_2")
    
        secret_names = self.secret_client.listAllSecretNames()
        
        assert secret_names, [SECRET_NAME, SECRET_NAME + "_2"]
        
        tags = [
            MetadataTag("sec_tag", "val"), MetadataTag("sec_tag_2", "val2")
        ]
        self.secret_client.setSecretTags(tags, SECRET_NAME)
        fetched_tags = self.secret_client.getSecretTags(SECRET_NAME)
        assert len(fetched_tags) == 2
        
        self.secret_client.deleteSecretTags(tags, SECRET_NAME)
        fetched_tags = self.secret_client.getSecretTags(SECRET_NAME)
        assert len(fetched_tags) == 0
        
        assert self.secret_client.secretExists(SECRET_NAME)
        
        self.secret_client.deleteSecret(SECRET_NAME)
        
        assert self.secret_client.secretExists(SECRET_NAME) == False
        
        self.secret_client.deleteSecret(SECRET_NAME + "_2")
        
        try:
            self.secret_client.getSecret(SECRET_NAME + "_2")
        except APIError as e:
            assert e.code == APIErrorCode.NOT_FOUND


    def test_scheduler_lifecycle(self, workflowDef):
        startWorkflowRequest = StartWorkflowRequest(
            name=WORKFLOW_NAME, workflow_def=workflowDef
        )
        saveScheduleRequest = SaveScheduleRequest(
            name=SCHEDULE_NAME,
            start_workflow_request=startWorkflowRequest,
            cron_expression= "0 */5 * ? * *"
        )

        self.scheduler_client.saveSchedule(saveScheduleRequest)

        schedule = self.scheduler_client.getSchedule(SCHEDULE_NAME)
        
        assert schedule['name'] == SCHEDULE_NAME
        
        self.scheduler_client.pauseSchedule(SCHEDULE_NAME)
        
        schedules = self.scheduler_client.getAllSchedules(WORKFLOW_NAME)
        assert len(schedules) == 1
        assert schedules[0].name == SCHEDULE_NAME
        assert schedules[0].paused
        
        self.scheduler_client.resumeSchedule(SCHEDULE_NAME)
        schedule = self.scheduler_client.getSchedule(SCHEDULE_NAME)
        assert not schedule['paused']
        
        times = self.scheduler_client.getNextFewScheduleExecutionTimes("0 */5 * ? * *", limit=1)
        assert(len(times) == 1)
        
        tags = [
            MetadataTag("sch_tag", "val"), MetadataTag("sch_tag_2", "val2")
        ]
        self.scheduler_client.setSchedulerTags(tags, SCHEDULE_NAME)
        fetched_tags = self.scheduler_client.getSchedulerTags(SCHEDULE_NAME)
        assert len(fetched_tags) == 2
        
        self.scheduler_client.deleteSchedulerTags(tags, SCHEDULE_NAME)
        fetched_tags = self.scheduler_client.getSchedulerTags(SCHEDULE_NAME)
        assert len(fetched_tags) == 0
        
        self.scheduler_client.deleteSchedule(SCHEDULE_NAME)
        
        try:
            schedule = self.scheduler_client.getSchedule(SCHEDULE_NAME)
        except APIError as e:
            assert e.code == APIErrorCode.NOT_FOUND
            assert e.message == "Schedule '{0}' not found".format(SCHEDULE_NAME)

    def test_application_lifecycle(self):
        req = CreateOrUpdateApplicationRequest(APPLICATION_NAME)
        created_app = self.authorization_client.createApplication(req)
        assert created_app.name == APPLICATION_NAME
        
        application = self.authorization_client.getApplication(created_app.id)
        assert application.id == created_app.id

        apps = self.authorization_client.listApplications()
        assert True in [app.id == created_app.id for app in apps]

        req.name = APPLICATION_NAME + "_updated"
        app_updated = self.authorization_client.updateApplication(req, created_app.id)
        assert app_updated.name == req.name
        
        self.authorization_client.addRoleToApplicationUser(created_app.id, "USER")
        app_user_id = "app:" + created_app.id
        app_user = self.authorization_client.getUser(app_user_id)
        assert True in [r.name == "USER" for r in app_user.roles]

        self.authorization_client.removeRoleFromApplicationUser(created_app.id, "USER")
        app_user = self.authorization_client.getUser(app_user_id)
        assert True not in [r.name == "USER" for r in app_user.roles]
        
        tags = [MetadataTag("auth_tag", "val"), MetadataTag("auth_tag_2", "val2")]
        self.authorization_client.setApplicationTags(tags, created_app.id)
        fetched_tags = self.authorization_client.getApplicationTags(created_app.id)
        assert len(fetched_tags) == 2

        self.authorization_client.deleteApplicationTags(tags, created_app.id)
        fetched_tags = self.authorization_client.getApplicationTags(created_app.id)
        assert len(fetched_tags) == 0

        created_access_key = self.authorization_client.createAccessKey(created_app.id)
        access_keys = self.authorization_client.getAccessKeys(created_app.id)
        assert(access_keys[0].id == created_access_key.id)
        assert(access_keys[0].status == AccessKeyStatus.ACTIVE)

        access_key = self.authorization_client.toggleAccessKeyStatus(created_app.id, created_access_key.id)
        assert access_key.status == AccessKeyStatus.INACTIVE
        
        self.authorization_client.deleteAccessKey(created_app.id, created_access_key.id)
        
        self.authorization_client.deleteApplication(created_app.id)
        try:
            application = self.authorization_client.getApplication(created_app.id)
        except APIError as e:
            assert e.code == APIErrorCode.NOT_FOUND
            assert e.message == "Application '{0}' not found".format(created_app.id)

    def test_user_group_permissions_lifecycle(self, workflowDef):
        req = UpsertUserRequest("Integration User", ["USER"])
        created_user = self.authorization_client.upsertUser(req, USER_ID)
        assert created_user.id == USER_ID

        user = self.authorization_client.getUser(USER_ID)
        assert user.id == USER_ID
        assert user.name == req.name
        
        users = self.authorization_client.listUsers()
        assert [user.id == USER_ID for u in users]
        
        req.name = "Integration " + "Updated"
        updated_user = self.authorization_client.upsertUser(req, USER_ID)
        assert updated_user.name == req.name
        
        # Test Groups
        req = UpsertGroupRequest("Integration Test Group", ["USER"])
        created_group = self.authorization_client.upsertGroup(req, GROUP_ID)
        assert created_group.id == GROUP_ID
        
        group = self.authorization_client.getGroup(GROUP_ID)
        assert group.id == GROUP_ID
        
        groups = self.authorization_client.listGroups()
        assert True in [group.id == GROUP_ID for group in groups]
        
        self.authorization_client.addUserToGroup(GROUP_ID, USER_ID)
        users = self.authorization_client.getUsersInGroup(GROUP_ID)
        assert users[0].id == USER_ID
        
        # Test Granting Permissions
        workflowDef.name = WORKFLOW_NAME + "_permissions"
        self.__create_workflow_definition(workflowDef)
        
        target = TargetRef(TargetType.WORKFLOW_DEF, WORKFLOW_NAME + "_permissions")
        subject_group = SubjectRef(SubjectType.GROUP, GROUP_ID)
        access_group = [AccessType.EXECUTE]
        
        subject_user = SubjectRef(SubjectType.USER, USER_ID)
        access_user = [AccessType.EXECUTE, AccessType.READ]
        
        self.authorization_client.grantPermissions(subject_group, target, access_group)
        self.authorization_client.grantPermissions(subject_user, target, access_user)
        
        target_perms = self.authorization_client.getPermissions(target)
        assert True in [s == subject_group for s in target_perms[AccessType.EXECUTE]]
        assert True in [s == subject_user for s in target_perms[AccessType.EXECUTE]]
        assert True in [s == subject_user for s in target_perms[AccessType.READ]]
        
        group_perms = self.authorization_client.getGrantedPermissionsForGroup(GROUP_ID)
        assert len(group_perms) == 1
        assert group_perms[0].target == target
        assert group_perms[0].access == access_group
        
        user_perms = self.authorization_client.getGrantedPermissionsForUser(USER_ID)
        assert len(user_perms) == 1
        assert user_perms[0].target == target
        assert sorted(user_perms[0].access) == sorted(access_user)
        
        self.authorization_client.removePermissions(subject_group, target, access_group)
        self.authorization_client.removePermissions(subject_user, target, access_user)
        target_perms = self.authorization_client.getPermissions(target)
        
        assert True not in [s == subject_group for s in target_perms[AccessType.EXECUTE]]
        assert True not in [s == subject_user for s in target_perms[AccessType.EXECUTE]]
        assert True not in [s == subject_user for s in target_perms[AccessType.READ]]
        
        self.authorization_client.removeUserFromGroup(GROUP_ID, USER_ID)
        
        self.authorization_client.deleteUser(USER_ID)
        try:
            self.authorization_client.getUser(USER_ID)
        except APIError as e:
            assert e.code == APIErrorCode.NOT_FOUND
            assert e.message ==  "User '{0}' not found".format(USER_ID)
        
        self.authorization_client.deleteGroup(GROUP_ID)
        try:
            self.authorization_client.getGroup(GROUP_ID)
        except APIError as e:
            assert e.code == APIErrorCode.NOT_FOUND
            assert e.message ==  "Group '{0}' not found".format(GROUP_ID)
            

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

    def __test_task_tags(self):
        tags = [
            MetadataTag("tag1", "val1"),
            MetadataTag("tag2", "val2"),
            MetadataTag("tag3", "val3")
        ]

        self.metadata_client.addTaskTag(tags[0], TASK_TYPE)
        fetchedTags = self.metadata_client.getTaskTags(TASK_TYPE)
        assert len(fetchedTags) == 1
        assert fetchedTags[0].key == tags[0].key

        self.metadata_client.setTaskTags(tags, TASK_TYPE)
        fetchedTags = self.metadata_client.getTaskTags(TASK_TYPE)
        assert len(fetchedTags) == 3

        tagStr = MetadataTag("tag2", "val2")
        self.metadata_client.deleteTaskTag(tagStr, TASK_TYPE)
        assert(len(self.metadata_client.getTaskTags(TASK_TYPE))) == 2

    def __test_workflow_tags(self):
        singleTag = MetadataTag("wftag", "val")

        self.metadata_client.addWorkflowTag(singleTag, WORKFLOW_NAME)
        fetchedTags = self.metadata_client.getWorkflowTags(WORKFLOW_NAME)
        assert len(fetchedTags) == 1
        assert fetchedTags[0].key == singleTag.key

        tags = [
            MetadataTag("wftag", "val"),
            MetadataTag("wftag2", "val2"),
            MetadataTag("wftag3", "val3")
        ]

        self.metadata_client.setWorkflowTags(tags, WORKFLOW_NAME)
        fetchedTags = self.metadata_client.getWorkflowTags(WORKFLOW_NAME)
        assert len(fetchedTags) == 3

        tag = MetadataTag("wftag2", "val2")
        self.metadata_client.deleteWorkflowTag(tag, WORKFLOW_NAME)
        assert(len(self.metadata_client.getWorkflowTags(WORKFLOW_NAME))) == 2

    def __test_workflow_rate_limit(self):
        assert self.metadata_client.getWorkflowRateLimit(WORKFLOW_NAME) == None

        self.metadata_client.setWorkflowRateLimit(2, WORKFLOW_NAME)
        assert self.metadata_client.getWorkflowRateLimit(WORKFLOW_NAME) == 2

        self.metadata_client.setWorkflowRateLimit(10, WORKFLOW_NAME)
        assert self.metadata_client.getWorkflowRateLimit(WORKFLOW_NAME) == 10

        self.metadata_client.removeWorkflowRateLimit(WORKFLOW_NAME)
        assert self.metadata_client.getWorkflowRateLimit(WORKFLOW_NAME) == None

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