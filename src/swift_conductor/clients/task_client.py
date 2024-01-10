from typing import Optional, List
from swift_conductor.configuration import Configuration
from swift_conductor.http.models.task import Task
from swift_conductor.http.models.task_result import TaskResult
from swift_conductor.http.models.task_exec_log import TaskExecLog
from swift_conductor.http.models.workflow import Workflow
from swift_conductor.clients.base_client import BaseClient
from swift_conductor.exceptions.api_exception_handler import api_exception_handler, for_all_methods

@for_all_methods(api_exception_handler, ["__init__"])
class TaskClient(BaseClient):
    def __init__(self, configuration: Configuration):
        super(TaskClient, self).__init__(configuration)

    def poll_task(self, taskType: str, workerId: Optional[str] = None, domain: Optional[str] = None) -> Optional[Task]:
        kwargs = {}
        if workerId:
            kwargs.update({"workerid": workerId})
        if domain:
            kwargs.update({"domain": domain})

        return self.taskResourceApi.poll(taskType, **kwargs)

    def batch_poll_tasks(
        self,
        taskType: str,
        workerId: Optional[str] = None,
        count: Optional[int] = None,
        timeoutInMillisecond: Optional[int] = None,
        domain: Optional[str] = None
    ) -> List[Task]:
        kwargs = {}
        if workerId:
            kwargs.update({"workerid": workerId})
        if count:
            kwargs.update({"count": count})
        if timeoutInMillisecond:
            kwargs.update({"timeout": timeoutInMillisecond})
        if domain:
            kwargs.update({"domain": domain})

        return self.taskResourceApi.batch_poll(taskType, **kwargs)

    def get_task(self, taskId: str) -> Task:
        return self.taskResourceApi.get_task(taskId)

    def update_task(self, taskResult: TaskResult) -> str:
        return self.taskResourceApi.update_task(taskResult)


    def get_queue_size_for_task(self, taskType: str) -> int:
        queueSizesByTaskType = self.taskResourceApi.size(task_type=[taskType])
        queueSize = queueSizesByTaskType.get(taskType, 0)
        return queueSize

    def add_task_log(self, taskId: str, logMessage: str):
        self.taskResourceApi.log(logMessage, taskId)

    def get_task_logs(self, taskId: str) -> List[TaskExecLog]:
        return self.taskResourceApi.get_task_logs(taskId)
