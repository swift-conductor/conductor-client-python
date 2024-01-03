from abc import ABC, abstractmethod
from swift_conductor.task.task import TaskInterface
from swift_conductor.task.task_type import TaskType
from typing_extensions import Self


class WaitTask(TaskInterface, ABC):
    @abstractmethod
    def __init__(self, task_ref_name: str) -> Self:
        super().__init__(
            task_reference_name=task_ref_name,
            task_type=TaskType.WAIT
        )


class WaitForDurationTask(WaitTask):
    def __init__(self, task_ref_name: str, duration_time_seconds: int) -> Self:
        super().__init__(task_ref_name)
        self.input_parameters = {
            "duration": str(duration_time_seconds)
        }


class WaitUntilTask(WaitTask):
    def __init__(self, task_ref_name: str, date_time: str) -> Self:
        super().__init__(task_ref_name)
        self.input_parameters = {
            "until": date_time
        }
