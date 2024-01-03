from typing import List
from swift_conductor.http.models.workflow_task import WorkflowTask
from swift_conductor.task.join_task import JoinTask
from swift_conductor.task.task import TaskInterface
from swift_conductor.task.task_type import TaskType
from copy import deepcopy
from typing_extensions import Self


class DynamicForkTask(TaskInterface):
    def __init__(self, task_ref_name: str, pre_fork_task: TaskInterface, join_task: JoinTask = None) -> Self:
        super().__init__(
            task_reference_name=task_ref_name,
            task_type=TaskType.FORK_JOIN_DYNAMIC
        )
        self._pre_fork_task = deepcopy(pre_fork_task)
        self._join_task = deepcopy(join_task)

    def to_workflow_task(self) -> WorkflowTask:
        workflow = super().to_workflow_task()
        workflow.dynamic_fork_join_tasks_param = 'forkedTasks'
        workflow.dynamic_fork_tasks_input_param_name = 'forkedTasksInputs'
        workflow.input_parameters['forkedTasks'] = self._pre_fork_task.output_ref(
            'forkedTasks'
        )
        workflow.input_parameters['forkedTasksInputs'] = self._pre_fork_task.output_ref(
            'forkedTasksInputs'
        )
        tasks = [
            self._pre_fork_task.to_workflow_task(),
            workflow,
        ]
        if self._join_task != None:
            tasks.append(self._join_task.to_workflow_task())
        return tasks
