# Worker

Considering real use cases, the goal is to run multiple workers in parallel. Due to some limitations with Python, a multiprocessing architecture was chosen in order to enable real parallelization.

You can write your workers independently and append them to a list. The `TaskHandler` class will spawn a unique and independent process for each worker, making sure it will behave as expected, by running an infinite loop like this:
* Poll for a `Task` at Conductor Server
* Generate `TaskResult` from given `Task`
* Update given `Task` with `TaskResult` at Conductor Server

## Write workers

Currently, there are three ways of writing a Python worker:
1. [Worker as a function](#worker-as-a-function)
2. [Worker as a class](#worker-as-a-class)
3. [Worker as an annotation](#worker-as-an-annotation)


### Worker as a function

The function should follow this signature:

```python
ExecuteTaskFunction = Callable[[Union[Task, object]], Union[TaskResult, object]]
```

In other words:
* Input must be either a `Task` or an `object`. If it isn't a `Task`, the assumption is that you are expecting to receive the `Task.input_data` as the object
* Output must be either a `TaskResult` or an `object`. If it isn't a `TaskResult`, the assumption is you are expecting to use the object as the `TaskResult.output_data`

Quick example below:

```python
from swift_conductor.http.models import Task, TaskResult
from swift_conductor.http.models.task_result_status import TaskResultStatus

def execute(task: Task) -> TaskResult:
    task_result = TaskResult(
        task_id=task.task_id,
        workflow_instance_id=task.workflow_instance_id,
        worker_id='your_custom_id'
    )
    task_result.add_output_data('worker_style', 'function')
    task_result.status = TaskResultStatus.COMPLETED
    return task_result
```

In the case you like more details, you can take a look at all possible combinations of workers [here](../../tests/integration/resources/worker/python/python_worker.py)

### Worker as a class

The class must implement `WorkerInterface` class, which requires an `execute` method. The remaining ones are inherited, but can be easily overridden. Example with a custom polling interval:

```python
from swift_conductor.http.models import Task, TaskResult
from swift_conductor.http.models.task_result_status import TaskResultStatus
from swift_conductor.worker.worker_interface import WorkerInterface

class SimplePythonWorker(WorkerInterface):
    def execute(self, task: Task) -> TaskResult:
        task_result = self.get_task_result_from_task(task)
        task_result.add_output_data('worker_style', 'class')
        task_result.add_output_data('secret_number', 1234)
        task_result.add_output_data('is_it_true', False)
        task_result.status = TaskResultStatus.COMPLETED
        return task_result

    def get_polling_interval_in_seconds(self) -> float:
        # poll every 500ms
        return 0.5
```

### Worker as an annotation

A worker can also be invoked by adding a WorkerTask decorator as shown in the below example.
As long as the annotated worker is in any file inside the root folder of your worker application, it will be picked up by the `TaskHandler`, see [Run Workers](#run-workers)

The arguments that can be passed when defining the decorated worker are:
1. task_definition_name: The task definition name of the condcutor task that needs to be polled for.
2. domain: Optional routing domain of the worker to execute tasks with a specific domain
3. worker_id: An optional worker id used to identify the polling worker
4. poll_interval: Polling interval in seconds. Defaulted to 1 second if not passed.

```python
from swift_conductor.worker.worker_task import WorkerTask

@WorkerTask(task_definition_name='python_annotated_task', worker_id='decorated', poll_interval=200.0)
def python_annotated_task(input) -> object:
    return {'message': 'python is so cool :)'}
```

## Run Workers

Now you can run your workers by calling a `TaskHandler`, example:

```python
from swift_conductor.configuration import Configuration
from swift_conductor.automation.task_handler import TaskHandler
from swift_conductor.worker.worker import Worker

#### Add these lines if running on a mac####
from multiprocessing import set_start_method
set_start_method('fork')
############################################

SERVER_API_URL = 'http://localhost:8080/api'

configuration = Configuration(
    server_api_url=SERVER_API_URL,
    debug=True
    ),
)

workers = [
    SimplePythonWorker(
        task_definition_name='python_task_example'
    ),
    Worker(
        task_definition_name='python_execute_function_task',
        execute_function=execute,
        poll_interval=250,
        domain='test'
    )
]

# If there are decorated workers in your application, scan_for_annotated_workers should be set
# default value of scan_for_annotated_workers is False
with TaskHandler(workers, configuration, scan_for_annotated_workers=True) as task_handler:
    task_handler.start_processes()
```

## Task Domains

Workers can be configured to start polling for work that is tagged by a task domain. See more on domains [here](https://swiftconductor.com/documentation/configuration/taskdomains.html).


```python
from swift_conductor.worker.worker_task import WorkerTask

@WorkerTask(task_definition_name='python_annotated_task', domain='cool')
def python_annotated_task(input) -> object:
    return {'message': 'python is so cool :)'}
```

The above code would run a worker polling for task of type, `python_annotated_task`, but only for workflows that have a task to domain mapping specified with domain for this task as `cool`.

```json
"taskToDomain": {
   "python_annotated_task": "cool"
}
```

## Worker Configuration

### Using Config File

You can choose to pass an `worker.ini` file for specifying worker arguments like domain and polling_interval. This allows for configuring your workers dynamically and hence provides the flexibility along with cleaner worker code. This file has to be in the same directory as the main.py of your worker application.

#### Format

```ini
[task_definition_name]
domain = <domain>
polling_interval = <polling-interval-in-ms>
```

#### Generic Properties

There is an option for specifying common set of properties which apply to all workers by putting them in the `DEFAULT` section. All workers who don't have a domain or/and polling_interval specified will default to these values.

```ini
[DEFAULT]
domain = <domain>
polling_interval = <polling-interval-in-ms>
```

#### Example File

```
[DEFAULT]
domain = nice
polling_interval = 2000

[python_annotated_task_1]
domain = cool
polling_interval = 500

[python_annotated_task_2]
domain = hot
polling_interval = 300
```

With the presence of the above config file, you don't need to specify domain and poll_interval for any of the worker task types.

##### Without config

```python
from swift_conductor.worker.worker_task import WorkerTask

@WorkerTask(task_definition_name='python_annotated_task_1', domain='cool', poll_interval=500.0)
def python_annotated_task(input) -> object:
    return {'message': 'python is so cool :)'}

@WorkerTask(task_definition_name='python_annotated_task_2', domain='hot', poll_interval=300.0)
def python_annotated_task_2(input) -> object:
    return {'message': 'python is so hot :)'}

@WorkerTask(task_definition_name='python_annotated_task_3', domain='nice', poll_interval=2000.0)
def python_annotated_task_3(input) -> object:
    return {'message': 'python is so nice :)'}

@WorkerTask(task_definition_name='python_annotated_task_4', domain='nice', poll_interval=2000.0)
def python_annotated_task_4(input) -> object:
    return {'message': 'python is very nice :)'}
```

##### With config

```python
from swift_conductor.worker.worker_task import WorkerTask

@WorkerTask(task_definition_name='python_annotated_task_1')
def python_annotated_task(input) -> object:
    return {'message': 'python is so cool :)'}

@WorkerTask(task_definition_name='python_annotated_task_2')
def python_annotated_task_2(input) -> object:
    return {'message': 'python is so hot :)'}

@WorkerTask(task_definition_name='python_annotated_task_3')
def python_annotated_task_3(input) -> object:
    return {'message': 'python is so nice :)'}

@WorkerTask(task_definition_name='python_annotated_task_4')
def python_annotated_task_4(input) -> object:
    return {'message': 'python is very nice :)'}

```

### Using Environment Variables

Workers can also be configured at run time by using environment variables which override configuration files as well.

#### Format

```
conductor_worker_polling_interval=<polling-interval-in-ms>
conductor_worker_domain=<domain>
conductor_worker_<task_definition_name>_polling_interval=<polling-interval-in-ms>
conductor_worker_<task_definition_name>_domain=<domain>
```

#### Example

```
conductor_worker_polling_interval=2000
conductor_worker_domain=nice
conductor_worker_python_annotated_task_1_polling_interval=500
conductor_worker_python_annotated_task_1_domain=cool
conductor_worker_python_annotated_task_2_polling_interval=300
conductor_worker_python_annotated_task_2_domain=hot
```

### Order of Precedence

If the worker configuration is initialized using multiple mechanisms mentioned above then the following order of priority will be considered from highest to lowest:

1. Environment Variables
2. Config File
3. Worker Constructor Arguments

## Performance

If you're looking for better performance (i.e. more workers of the same type) - you can simply append more instances of the same worker, like this:

```python
workers = [
    SimplePythonWorker(
        task_definition_name='python_task_example'
    ),
    SimplePythonWorker(
        task_definition_name='python_task_example'
    ),
    SimplePythonWorker(
        task_definition_name='python_task_example'
    ),
    ...
]
```

```python
workers = [
    Worker(
        task_definition_name='python_task_example',
        execute_function=execute,
        poll_interval=0.25,
    ),
    Worker(
        task_definition_name='python_task_example',
        execute_function=execute,
        poll_interval=0.25,
    ),
    Worker(
        task_definition_name='python_task_example',
        execute_function=execute,
        poll_interval=0.25,
    )
    ...
]
```

### Next: [Create workflows using Code](../workflow/README.md)
