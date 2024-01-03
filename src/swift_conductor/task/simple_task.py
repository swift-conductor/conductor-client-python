from typing_extensions import Self
from swift_conductor.task.task_type import TaskType
from swift_conductor.task.task import TaskInterface


class SimpleTask(TaskInterface):
    def __init__(self, task_def_name: str, task_reference_name: str) -> Self:
        super().__init__(
            task_reference_name=task_reference_name,
            task_type=TaskType.SIMPLE,
            task_name=task_def_name,
        )
