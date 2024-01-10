from swift_conductor.http.models.task import Task
from swift_conductor.http.models.task_result import TaskResult
from swift_conductor.http.models.task_result_status import TaskResultStatus
from swift_conductor.worker.worker_abc import WorkerAbc
from swift_conductor.worker.worker_function import WorkerFunction


class FaultyExecutionWorker(WorkerAbc):
    def execute(self, task: Task) -> TaskResult:
        raise Exception('faulty execution')


class PythonWorker(WorkerAbc):
    def __init__(self, task_definition_name):
        super().__init__(task_definition_name)
        self.poll_interval = 375.0

    def execute(self, task: Task) -> TaskResult:
        task_result = self.get_task_result_from_task(task)
        task_result.add_output_data('worker_style', 'class')
        task_result.add_output_data('secret_number', 1234)
        task_result.add_output_data('is_it_true', False)
        task_result.status = TaskResultStatus.COMPLETED
        return task_result


class PythonWorkerWithDomain(WorkerAbc):
    def __init__(self, task_definition_name):
        super().__init__(task_definition_name)
        self.poll_interval = 850.0
        self.domain = 'custom_python_worker'

    def execute(self, task: Task) -> TaskResult:
        task_result = self.get_task_result_from_task(task)
        task_result.add_output_data('worker_style', 'class')
        task_result.add_output_data('secret_number', 1234)
        task_result.add_output_data('is_it_true', False)
        task_result.status = TaskResultStatus.COMPLETED
        return task_result

def worker_with_task_input_and_task_result_output(task: Task) -> TaskResult:
    task_result = TaskResult(
        task_id=task.task_id,
        workflow_instance_id=task.workflow_instance_id,
        worker_id='your_custom_id'
    )
    task_result.add_output_data('worker_style', 'function')
    task_result.add_output_data('worker_input', 'Task')
    task_result.add_output_data('worker_output', 'TaskResult')
    task_result.status = TaskResultStatus.COMPLETED
    return task_result


def worker_with_task_input_and_generic_output(task: Task) -> object:
    return {
        'worker_style': 'function',
        'worker_input': 'Task',
        'worker_output': 'object',
        'task_id': task.task_id,
        'task_input': task.input_data,
    }


def worker_with_generic_input_and_task_result_output(obj: object) -> TaskResult:
    task_result = TaskResult(
        task_id='',
        workflow_instance_id='',
        worker_id=''
    )
    task_result.add_output_data('worker_style', 'function')
    task_result.add_output_data('worker_input', 'object')
    task_result.add_output_data('worker_output', 'TaskResult')
    task_result.status = TaskResultStatus.COMPLETED
    return task_result


def worker_with_generic_input_and_generic_output(obj: object) -> object:
    return {
        'worker_style': 'function',
        'worker_input': 'object',
        'worker_output': 'object',
        'input': obj,
    }
