from typing import Optional, Dict
from swift_conductor.configuration import Configuration
from swift_conductor.http.models.workflow import Workflow
from swift_conductor.http.models.workflow_run import WorkflowRun
from swift_conductor.http.models.start_workflow_request import StartWorkflowRequest
from swift_conductor.http.models.rerun_workflow_request import RerunWorkflowRequest
from swift_conductor.http.models.workflow_test_request import WorkflowTestRequest
from swift_conductor.clients.base_client import BaseClient
from swift_conductor.exceptions.api_exception_handler import api_exception_handler, for_all_methods

@for_all_methods(api_exception_handler, ["__init__"])
class WorkflowClient(BaseClient):
    def __init__(
        self,
        configuration: Configuration
        ):
        super(WorkflowClient, self).__init__(configuration)

    def start_workflow_by_name(
        self,
        name: str,
        input: Dict[str, object],
        version: Optional[int] = None,
        correlationId: Optional[str] = None,
        priority: Optional[int] = None,
    ) -> str:
        kwargs = {}
        if version:
            kwargs.update({"version": version})
        if correlationId:
            kwargs.update({"correlation_id": correlationId})
        if priority:
            kwargs.update({"priority": priority})

        return self.workflowResourceApi.start_workflow1(input, name, **kwargs)

    def start_workflow(self, startWorkflowRequest: StartWorkflowRequest) -> str:
        return self.workflowResourceApi.start_workflow(startWorkflowRequest)

    def execute_workflow(
        self,
        startWorkflowRequest: StartWorkflowRequest,
        requestId: str,
        name: str,
        version: int,
        waitUntilTaskRef: Optional[str] = None
    ) -> WorkflowRun:
        kwargs = { "wait_until_task_ref" : waitUntilTaskRef } if waitUntilTaskRef else {}
        return self.workflowResourceApi.execute_workflow(startWorkflowRequest, requestId, name, version, **kwargs)

    def pause_workflow(self, workflowId: str):
        self.workflowResourceApi.pause_workflow1(workflowId)

    def resumeWorkflow(self, workflowId: str):
        self.workflowResourceApi.resume_workflow1(workflowId)

    def restart_workflow(self, workflowId: str, useLatestDef: Optional[bool] = False):
        self.workflowResourceApi.restart1(workflowId, use_latest_definitions=useLatestDef)

    def rerun_workflow(self, workflowId: str, rerunWorkflowRequest: RerunWorkflowRequest):
        self.workflowResourceApi.rerun(rerunWorkflowRequest, workflowId)

    def retry_workflow(self, workflowId: str, resumeSubworkflowTasks: Optional[bool] = False):
        self.workflowResourceApi.retry1(workflowId, resume_subworkflow_tasks=resumeSubworkflowTasks)

    def terminate_workflow(self, workflowId: str, reason: Optional[str] = None):
        kwargs = { "reason" : reason } if reason else {}
        self.workflowResourceApi.terminate1(workflowId, **kwargs)

    def get_workflow(self, workflowId: str, includeTasks: Optional[bool] = True) -> Workflow:
        return self.workflowResourceApi.get_execution_status(workflowId, include_tasks=includeTasks)

    def delete_workflow(self, workflowId: str, archiveWorkflow: Optional[bool] = True):
        self.workflowResourceApi.delete(workflowId, archive_workflow=archiveWorkflow)

    def skip_task_from_workflow(self, workflowId: str, taskReferenceName: str):
        self.workflowResourceApi.skip_task_from_workflow(workflowId, taskReferenceName)

    def test_workflow(self, testRequest: WorkflowTestRequest) -> Workflow:
        return self.workflowResourceApi.test_workflow(testRequest)