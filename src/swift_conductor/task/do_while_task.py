from swift_conductor.http.models.workflow_task import WorkflowTask
from swift_conductor.task.task import TaskInterface, get_task_interface_list_as_workflow_task_list
from swift_conductor.task.task_type import TaskType
from copy import deepcopy
from typing import List
from typing_extensions import Self


def get_for_loop_condition(task_ref_name: str, iterations: int) -> str:
    return f"if ( $.{task_ref_name}.iteration < $.{iterations} ) {{ true; }} else {{ false; }}"


class DoWhileTask(TaskInterface):
    # termination_condition is a Javascript expression that evaluates to True or False
    def __init__(self, task_ref_name: str, termination_condition: str, tasks: List[TaskInterface]) -> Self:
        super().__init__(
            task_reference_name=task_ref_name,
            task_type=TaskType.DO_WHILE,
        )
        self._loop_condition = deepcopy(termination_condition)
        if isinstance(tasks, List):
            self._loop_over = deepcopy(tasks)
        else:
            self._loop_over = [deepcopy(tasks)]

    def to_workflow_task(self) -> WorkflowTask:
        workflow = super().to_workflow_task()
        workflow.loop_condition = self._loop_condition
        workflow.loop_over = get_task_interface_list_as_workflow_task_list(
            *self._loop_over,
        )
        return workflow


class LoopTask(DoWhileTask):
    def __init__(self, task_ref_name: str, iterations: int, tasks: List[TaskInterface]) -> Self:
        super().__init__(
            task_ref_name=task_ref_name,
            termination_condition=get_for_loop_condition(
                task_ref_name, iterations,
            ),
            tasks=tasks,
        )
