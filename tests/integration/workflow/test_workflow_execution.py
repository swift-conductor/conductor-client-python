import logging
from time import sleep
from multiprocessing import set_start_method

from resources.worker.python.python_worker import (
    PythonWorker,
    PythonWorkerWithDomain,

    worker_with_generic_input_and_generic_output,
    worker_with_generic_input_and_task_result_output,
    worker_with_task_input_and_generic_output,
    worker_with_task_input_and_task_result_output
)

from swift_conductor.automation.worker_host import WorkerHost
from swift_conductor.configuration import Configuration
from swift_conductor.http.models import StartWorkflowRequest
from swift_conductor.http.models import TaskDef
from swift_conductor.worker.worker_impl import ExecuteTaskFunction
from swift_conductor.worker.worker_impl import WorkerImpl
from swift_conductor.workflow.workflow_builder import WorkflowBuilder
from swift_conductor.workflow.workflow_manager import WorkflowManager
from swift_conductor.task.custom_task import CustomTask


WORKFLOW_NAME = "sdk_python_integration_test_workflow"
WORKFLOW_DESCRIPTION = "Python SDK Integration Test"
WORKFLOW_VERSION = 1234
WORKFLOW_OWNER_EMAIL = "test@test.com"

TASK_NAME = "python_integration_test_task"

logger_name = Configuration.get_logging_formatted_name(__name__)
logger = logging.getLogger(logger_name)


def run_workflow_execution_tests(configuration: Configuration, workflow_manager: WorkflowManager):
    workers = [
        PythonWorker(TASK_NAME),
        PythonWorkerWithDomain(TASK_NAME),

        generate_worker(worker_with_generic_input_and_generic_output),
        generate_worker(worker_with_generic_input_and_task_result_output),
        generate_worker(worker_with_task_input_and_generic_output),
        generate_worker(worker_with_task_input_and_task_result_output),
    ]

    worker_host = WorkerHost(workers=workers, configuration=configuration)

    set_start_method('spawn')
    worker_host.start_processes()

    try:
        test_get_workflow_by_correlation_ids(workflow_manager)
        logger.debug('finished workflow correlation ids test')

        test_workflow_registration(workflow_manager)
        logger.debug('finished workflow registration tests')

        test_workflow_execution(
            workflow_quantity=1,
            workflow_name=WORKFLOW_NAME,
            workflow_manager=workflow_manager,
            workflow_completion_wait=5.0
        )
    finally:
        worker_host.stop_processes()


def generate_tasks_defs():
    python_custom_task_from_code = TaskDef(
        description="desc python_custom_task_from_code",
        owner_app="python_integration_test_app",
        timeout_seconds=3,
        response_timeout_seconds=2,
        created_by=WORKFLOW_OWNER_EMAIL,
        name=TASK_NAME,
        input_keys=["input1"],
        output_keys=[],
        owner_email=WORKFLOW_OWNER_EMAIL,
    )
    return [python_custom_task_from_code]


def test_get_workflow_by_correlation_ids(workflow_manager: WorkflowManager):
    _run_with_retry_attempt(
        workflow_manager.get_by_correlation_ids,
        {
            'workflow_name': WORKFLOW_NAME,
            'correlation_ids': [
                '2', '5', '33', '4', '32', '7', '34', '1', '3', '6', '1440'
            ]
        }
    )


def test_workflow_registration(workflow_manager: WorkflowManager):
    workflow = generate_workflow()

    try:
        workflow_manager.metadata_client.unregister_workflow_def_with_http_info(
            workflow.name, workflow.version)
    except Exception as e:
        if '404' not in str(e):
            raise e

    workflow_manager.register_workflow(workflow.to_workflow_def())


def test_workflow_execution(workflow_quantity: int, workflow_name: str, workflow_manager: WorkflowManager, workflow_completion_wait: float) -> None:
    start_workflow_requests = [''] * workflow_quantity
    for i in range(workflow_quantity):
        start_workflow_requests[i] = StartWorkflowRequest(name=workflow_name)

    workflow_ids = workflow_manager.start_workflows(*start_workflow_requests)
    sleep(workflow_completion_wait)

    for workflow_id in workflow_ids:
        _run_with_retry_attempt(validate_workflow_status, {
            'workflow_id': workflow_id,
            'workflow_manager': workflow_manager
        })


def generate_workflow(workflow_name: str = WORKFLOW_NAME, task_name: str = TASK_NAME) -> WorkflowBuilder:
    return WorkflowBuilder(
        name=workflow_name,
        description=WORKFLOW_DESCRIPTION,
        version=WORKFLOW_VERSION,
    ).add(
        CustomTask(
            task_def_name=task_name,
            task_reference_name=task_name,
        )
    ).owner_email(WORKFLOW_OWNER_EMAIL)


def validate_workflow_status(workflow_id: str, workflow_manager: WorkflowManager) -> None:
    workflow = workflow_manager.get_workflow(
        workflow_id=workflow_id,
        include_tasks=False,
    )

    if workflow.status != 'COMPLETED':
        raise Exception(
            f'workflow expected to be COMPLETED, but received {workflow.status}, workflow_id: {workflow_id}')


def generate_worker(execute_function: ExecuteTaskFunction) -> WorkerImpl:
    return WorkerImpl(
        task_definition_name=TASK_NAME,
        execute_function=execute_function,
        poll_interval=750.0
    )


def _run_with_retry_attempt(f, params, retries=4) -> None:
    for attempt in range(retries):
        try:
            return f(**params)
        except Exception as e:
            if attempt == retries - 1:
                raise e
            sleep(1 << attempt)
