from typing import Optional, List
from conductor.client.configuration.configuration import Configuration
from conductor.client.http.rest import ApiException
from conductor.client.http.api_client import ApiClient
from conductor.client.http.api.task_resource_api import TaskResourceApi
from conductor.client.http.models.task import Task
from conductor.client.http.models.task_result import TaskResult
from conductor.client.http.models.task_exec_log import TaskExecLog
from conductor.client.http.models.task_result_status import TaskResultStatus
from conductor.client.interfaces.task_client_interface import TaskClientInterface
from conductor.client.http.models.workflow import Workflow

class TaskClient(TaskClientInterface):
    def __init__(self, configuration: Configuration):
        api_client = ApiClient(configuration)
        self.taskResourceApi = TaskResourceApi(api_client)
        
    def pollTask(self, taskType: str, workerId: Optional[str] = None, domain: Optional[str] = None) -> Optional[Task]:
        kwargs = {}
        if workerId:
            kwargs.update({"workerid": workerId})
        if domain:
            kwargs.update({"domain": domain})

        return self.taskResourceApi.poll(taskType, **kwargs)
    
    def batchPollTasks(
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

    def getTask(self, taskId: str) -> (Optional[Task], str):
        task = None
        error = None

        try:
            task = self.taskResourceApi.get_task(taskId)
        except ApiException as e:
            message = e.reason if e.reason else e.body
            error = message

        return task, error

    def updateTask(self, taskResult: TaskResult) -> str:
        return self.taskResourceApi.update_task(taskResult)

    def updateTaskByRefName(
        self,
        workflowId: str,
        taskRefName: str,
        status: str,
        output: object,
        workerId: Optional[str] = None
    ) -> str:
        body = { "result": output }
        kwargs = {}
        if workerId:
            kwargs.update({"workerid": workerId})
        return self.taskResourceApi.update_task1(body, workflowId, taskRefName, status, **kwargs)
    
    def updateTaskSync(
        self,
        workflowId: str,
        taskRefName: str,
        status: str,
        output: object,
        workerId: Optional[str] = None
    ) -> Workflow:
        body = { "result": output }
        kwargs = {}
        if workerId:
            kwargs.update({"workerid": workerId})
        return self.taskResourceApi.update_task_sync(body, workflowId, taskRefName, status, **kwargs)

    def getQueueSizeForTask(self, taskType: str) -> int:
        queueSizesByTaskType = self.taskResourceApi.size(task_type=[taskType])
        queueSize = queueSizesByTaskType.get(taskType, 0)
        return queueSize

    def addTaskLog(self, taskId: str, logMessage: str):
        self.taskResourceApi.log(logMessage, taskId)

    def getTaskLogs(self, taskId: str) -> List[TaskExecLog]:
        return self.taskResourceApi.get_task_logs(taskId)
