from abc import ABC, abstractmethod
from typing import Optional, List
from swift_conductor.http.models.workflow import Workflow
from swift_conductor.http.models.task import Task
from swift_conductor.http.models.task_result import TaskResult
from swift_conductor.http.models.task_result_status import TaskResultStatus
from swift_conductor.http.models.task_exec_log import TaskExecLog

class TaskClientABC(ABC):
    @abstractmethod
    def pollTask(self, taskType: str, workerId: Optional[str] = None, domain: Optional[str] = None) -> Optional[Task]:
        pass
    
    @abstractmethod
    def batchPollTasks(
        self,
        taskType: str,
        workerId: Optional[str] = None,
        count: Optional[int] = None,
        timeoutInMillisecond: Optional[int] = None,
        domain: Optional[str] = None
    ) -> List[Task]:
        pass

    @abstractmethod
    def getTask(self, taskId: str) -> Task:
        pass

    @abstractmethod
    def updateTask(self, taskResult: TaskResult) -> str:
        pass
    
    @abstractmethod
    def updateTaskByRefName(
        self,
        workflowId: str,
        taskRefName: str,
        status: TaskResultStatus,
        output: object,
        workerId: Optional[str] = None
    ) -> str:
        pass
    
    @abstractmethod
    def updateTaskSync(
        self,
        workflowId: str,
        taskRefName: str,
        status: TaskResultStatus,
        output: object,
        workerId: Optional[str] = None
    ) -> Workflow:
        pass
    
    @abstractmethod
    def getQueueSizeForTask(self, taskType: str) -> int:
        pass

    @abstractmethod
    def addTaskLog(self, taskId: str, logMessage: str):
        pass

    @abstractmethod
    def getTaskLogs(self, taskId: str) -> List[TaskExecLog]:
        pass

