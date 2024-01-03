from swift_conductor.http.models.workflow_task import WorkflowTask
from swift_conductor.task.task import TaskInterface
from swift_conductor.task.task_type import TaskType
from copy import deepcopy
from typing import List
from typing_extensions import Self


def get_join_task(task_reference_name: str) -> str:
    return task_reference_name + '_join'


class ForkTask(TaskInterface):
    def __init__(self, task_ref_name: str, forked_tasks: List[List[TaskInterface]]) -> Self:
        super().__init__(
            task_reference_name=task_ref_name,
            task_type=TaskType.FORK_JOIN
        )
        self._forked_tasks = deepcopy(forked_tasks)

    def to_workflow_task(self) -> WorkflowTask:
        workflow_task = super().to_workflow_task()
        workflow_task.fork_tasks = []
        workflow_task.join_on = []
        for inner_forked_tasks in self._forked_tasks:
            converted_inner_forked_tasks = []
            for inner_forked_task in inner_forked_tasks:
                converted_inner_forked_tasks.append(
                    inner_forked_task.to_workflow_task()
                )
            workflow_task.fork_tasks.append(converted_inner_forked_tasks)
            workflow_task.join_on.append(
                converted_inner_forked_tasks[-1].task_reference_name
            )
        return workflow_task
