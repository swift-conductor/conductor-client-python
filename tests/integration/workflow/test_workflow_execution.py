import logging
from time import sleep
from multiprocessing import set_start_method

from swift_conductor.automation.task_handler import TaskHandler
from swift_conductor.configuration import Configuration
from swift_conductor.http.models import StartWorkflowRequest
from swift_conductor.http.models import TaskDef
from swift_conductor.worker.worker import ExecuteTaskFunction
from swift_conductor.worker.worker import Worker
from swift_conductor.workflow.workflow import Workflow
from swift_conductor.workflow.workflow_manager import WorkflowManager
from swift_conductor.task.simple_task import SimpleTask

from resources.worker.python.python_worker import *

WORKFLOW_NAME = "sdk_python_integration_test_workflow"
WORKFLOW_DESCRIPTION= "Python SDK Integration Test"
TASK_NAME = "python_integration_test_task"
WORKFLOW_VERSION = 1234
WORKFLOW_OWNER_EMAIL = "test@test"

logger = logging.getLogger(
    Configuration.get_logging_formatted_name(
        __name__
    )
)


def run_workflow_execution_tests(configuration: Configuration, workflow_manager: WorkflowManager):
    workers=[
        ClassWorker(TASK_NAME),
        ClassWorkerWithDomain(TASK_NAME),
        generate_worker(worker_with_generic_input_and_generic_output),
        generate_worker(worker_with_generic_input_and_task_result_output),
        generate_worker(worker_with_task_input_and_generic_output),
        generate_worker(worker_with_task_input_and_task_result_output),
    ]
    task_handler = TaskHandler(
        workers=workers,
        configuration=configuration,
        scan_for_annotated_workers=True,
    )
    set_start_method('fork')
    task_handler.start_processes()
    try:
        test_get_workflow_by_correlation_ids(workflow_manager)
        logger.debug('finished workflow correlation ids test')
        test_workflow_registration(workflow_manager)
        logger.debug('finished workflow registration tests')
        test_workflow_execution(
            workflow_quantity=6,
            workflow_name=WORKFLOW_NAME,
            workflow_manager=workflow_manager,
            workflow_completion_timeout=5.0
        )
        test_decorated_workers(workflow_manager)
    except Exception as e:
        task_handler.stop_processes()
        raise Exception(f'failed integration tests, reason: {e}')
    task_handler.stop_processes()


def generate_tasks_defs():
    python_simple_task_from_code = TaskDef(
        description="desc python_simple_task_from_code",
        owner_app="python_integration_test_app",
        timeout_seconds=3,
        response_timeout_seconds=2,
        created_by=WORKFLOW_OWNER_EMAIL,
        name=TASK_NAME,
        input_keys=["input1"],
        output_keys=[],
        owner_email=WORKFLOW_OWNER_EMAIL,
    )
    return [python_simple_task_from_code]


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
    workflow = generate_workflow(workflow_manager)
    try:
        workflow_manager.metadata_client.unregister_workflow_def_with_http_info(
            workflow.name, workflow.version
        )
    except Exception as e:
        if '404' not in str(e):
            raise e
    workflow.register(overwrite=True) == None
    workflow_manager.register_workflow(
        workflow.to_workflow_def(), overwrite=True
    )


def test_decorated_workers(
        workflow_manager: WorkflowManager,
        workflow_name: str = 'TestPythonDecoratedWorkerWf',
) -> None:
    wf = generate_workflow(
        workflow_manager=workflow_manager,
        workflow_name=workflow_name,
        task_name='test_python_decorated_worker',
    )
    wf.register(True)
    workflow_id = workflow_manager.start_workflow(StartWorkflowRequest(name=workflow_name))
    logger.debug(f'started TestPythonDecoratedWorkerWf with id: {workflow_id}')
    
    td_map = {
        'test_python_decorated_worker': 'cool'
    }
    start_wf_req = StartWorkflowRequest(name=workflow_name, task_to_domain=td_map)
    workflow_id_2 = workflow_manager.start_workflow(start_wf_req)
    
    logger.debug(f'started TestPythonDecoratedWorkerWf with domain:cool and id: {workflow_id_2}')
    sleep(5)
    
    _run_with_retry_attempt(
        validate_workflow_status,
        {
            'workflow_id': workflow_id,
            'workflow_manager': workflow_manager
        }
    )
    
    _run_with_retry_attempt(
        validate_workflow_status,
        {
            'workflow_id': workflow_id_2,
            'workflow_manager': workflow_manager
        }
    )
    
    workflow_manager.metadata_client.unregister_workflow_def(wf.name, wf.version)
    

def test_workflow_execution(
    workflow_quantity: int,
    workflow_name: str,
    workflow_manager: WorkflowManager,
    workflow_completion_timeout: float,
) -> None:
    start_workflow_requests = [''] * workflow_quantity
    for i in range(workflow_quantity):
        start_workflow_requests[i] = StartWorkflowRequest(name=workflow_name)
    workflow_ids = workflow_manager.start_workflows(*start_workflow_requests)
    sleep(workflow_completion_timeout)
    for workflow_id in workflow_ids:
        _run_with_retry_attempt(
            validate_workflow_status,
            {
                'workflow_id': workflow_id,
                'workflow_manager': workflow_manager
            }
        )


def generate_workflow(workflow_manager: WorkflowManager, workflow_name: str = WORKFLOW_NAME, task_name: str = TASK_NAME) -> Workflow:
    return Workflow(
        manager=workflow_manager,
        name=workflow_name,
        description=WORKFLOW_DESCRIPTION,
        version=WORKFLOW_VERSION,
    ).owner_email(
        WORKFLOW_OWNER_EMAIL
    ).add(
        SimpleTask(
            task_def_name=task_name,
            task_reference_name=task_name,
        )
    )


def validate_workflow_status(workflow_id: str, workflow_manager: WorkflowManager) -> None:
    workflow = workflow_manager.get_workflow(
        workflow_id=workflow_id,
        include_tasks=False,
    )
    if workflow.status != 'COMPLETED':
        raise Exception(
            f'workflow expected to be COMPLETED, but received {workflow.status}, workflow_id: {workflow_id}'
        )
    workflow_status = workflow_manager.get_workflow_status(
        workflow_id=workflow_id,
        include_output=False,
        include_variables=False,
    )
    if workflow_status.status != 'COMPLETED':
        raise Exception(
            f'workflow expected to be COMPLETED, but received {workflow_status.status}, workflow_id: {workflow_id}'
        )


def generate_worker(execute_function: ExecuteTaskFunction) -> Worker:
    return Worker(
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
