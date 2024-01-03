from abc import ABC, abstractmethod
from typing import Optional, List
from swift_conductor.http.models.workflow_def import WorkflowDef
from swift_conductor.http.models.task_def import TaskDef

class MetadataClientABC(ABC):
    @abstractmethod
    def register_workflow_def(self, workflowDef: WorkflowDef, overwrite: Optional[bool]):
        pass

    @abstractmethod
    def update_workflow_def(self, workflowDef: WorkflowDef, overwrite: Optional[bool]):
        pass

    @abstractmethod
    def unregister_workflow_def(self, workflowName: str, version: int):
        pass

    @abstractmethod
    def get_workflow_def(self, name: str, version: Optional[int]) -> WorkflowDef:
        pass

    @abstractmethod
    def get_all_workflow_defs(self) -> List[WorkflowDef]:
        pass

    @abstractmethod
    def register_task_def(self, taskDef: TaskDef):
        pass

    @abstractmethod
    def update_task_def(self, taskDef: TaskDef):
        pass

    @abstractmethod
    def unregister_task_def(self, taskType: str):
        pass

    @abstractmethod
    def get_task_def(self, taskType: str) -> TaskDef:
        pass

    @abstractmethod
    def get_all_task_defs(self) -> List[TaskDef]:
        pass
