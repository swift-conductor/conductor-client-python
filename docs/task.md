# Task Management

## Task Client

### Initialization

```python
from swift_conductor.configuration import Configuration
from swift_conductor.clients.task_client import TaskClient

configuration = Configuration(
    server_api_url=SERVER_API_URL,
    debug=False
)

task_client = TaskClient(configuration)
```

### Task Polling

#### Poll a single task

```python
polledTask = task_client.poll_task("TASK_TYPE")
```

#### Batch poll tasks

```python
batchPolledTasks = task_client.batch_poll_tasks("TASK_TYPE")
```

### Get Task

```python
task = task_client.get_task("task_id")
```

### Updating Task Status

#### Update task using TaskResult object

```python
task_result = TaskResult(
    workflow_instance_id="workflow_instance_id",
    task_id="task_id",
    status=TaskResultStatus.COMPLETED
)

task_client.update_task(task_result)
```

### Task Log Management

#### Add Task logs

```python
task_client.add_task_log("task_id", "Test task log!")
```

#### Get Task logs

```python
taskLogs = task_client.get_task_logs("task_id")
```
