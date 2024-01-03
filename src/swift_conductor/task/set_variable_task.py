from typing_extensions import Self
from swift_conductor.task.task_type import TaskType
from swift_conductor.task.task import TaskInterface


class SetVariableTask(TaskInterface):
    def __init__(self, task_ref_name: str) -> Self:
        super().__init__(
            task_reference_name=task_ref_name,
            task_type=TaskType.SET_VARIABLE
        )
