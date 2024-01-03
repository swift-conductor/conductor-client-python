from typing import Optional, List
from swift_conductor.configuration import Configuration
from swift_conductor.http.models.workflow_def import WorkflowDef
from swift_conductor.http.models.task_def import TaskDef
from swift_conductor.clients.base_client import BaseClient
from swift_conductor.exceptions.api_exception_handler import api_exception_handler, for_all_methods

@for_all_methods(api_exception_handler, ["__init__"])
class MetadataClient(BaseClient):
    def __init__(self, configuration: Configuration):
        super(MetadataClient, self).__init__(configuration)
        
    def register_workflow_def(self, workflowDef: WorkflowDef, overwrite: Optional[bool] = True):
        self.metadataResourceApi.create(workflowDef, overwrite=overwrite)

    def update_workflow_def(self, workflowDef: WorkflowDef, overwrite: Optional[bool] = True):
        self.metadataResourceApi.update1([workflowDef], overwrite=overwrite)

    def unregister_workflow_def(self, name: str, version: int):
        self.metadataResourceApi.unregister_workflow_def(name, version)

    def get_workflow_def(self, name: str, version: Optional[int] = None) -> WorkflowDef:
        workflow = None
        if version:
            workflow = self.metadataResourceApi.get(name, version=version)
        else:
            workflow = self.metadataResourceApi.get(name)

        return workflow

    def get_all_workflow_defs(self) -> List[WorkflowDef]:
        return self.metadataResourceApi.get_all_workflows()

    def register_task_def(self, taskDef: TaskDef):
        self.metadataResourceApi.register_task_def([taskDef])

    def update_task_def(self, taskDef: TaskDef):
        self.metadataResourceApi.update_task_def(taskDef)

    def unregister_task_def(self, taskType: str):
        self.metadataResourceApi.unregister_task_def(taskType)

    def get_task_def(self, taskType: str) -> TaskDef:
        return self.metadataResourceApi.get_task_def(taskType)

    def get_all_task_defs(self) -> List[TaskDef]:
        return self.metadataResourceApi.get_task_defs()
        
    