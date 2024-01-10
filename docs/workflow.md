# Workflow Management

## Workflow Client

### Initialization

```python
from swift_conductor.configuration import Configuration
from swift_conductor.clients.workflow_client import WorkflowClient

configuration = Configuration(
    server_api_url=SERVER_API_URL,
    debug=False
)

workflow_client = WorkflowClient(configuration)
```

### Start Workflow Execution

#### Start using StartWorkflowRequest

```python
workflow = WorkflowBuilder(
    name="WORKFLOW_NAME",
    description='Test Create Workflow',
    version=1
)

workflow.input_parameters(["a", "b"])

workflow >> CustomTask("custom_task", "custom_task_ref")

workflowDef = workflow.to_workflow_def()

startWorkflowRequest = StartWorkflowRequest(
    name="WORKFLOW_NAME",
    version=1,
    workflow_def=workflowDef,
    input={ "a" : 15, "b": 3 }
)

workflow_id = workflow_client.start_workflow(startWorkflowRequest)
```

#### Start using Workflow Name

```python
wfInput = { "a" : 5, "b": "+", "c" : [7, 8] }
workflow_id = workflow_client.start_workflow_by_name("WORKFLOW_NAME", wfInput)
```

### Fetch a workflow execution

#### Exclude tasks

```python
workflow = workflow_client.get_workflow(workflow_id, False)
```

#### Include tasks

```python
workflow = workflow_client.get_workflow(workflow_id, True)
```

### Workflow Execution Management

### Pause workflow

```python
workflow_client.pause_workflow(workflow_id)
```

### Resume workflow

```python
workflow_client.resumeWorkflow(workflow_id)
```

### Terminate workflow

```python
workflow_client.terminate_workflow(workflow_id, "Termination reason")
```

### Restart workflow

This operation has no effect when called on a workflow that is in a non-terminal state. If useLatestDef is set, the restarted workflow uses the latest workflow definition.

```python
workflow_client.restart_workflow(workflow_id, useLatestDef=True)
```

### Retry failed workflow

When called, the task in the failed state is scheduled again, and the workflow moves to RUNNING status. If resumeSubworkflowTasks is set and the last failed task was a sub-workflow, the server restarts the sub-workflow from the failed task. If set to false, the sub-workflow is re-executed.

```python
workflow_client.retry_workflow(workflow_id, resumeSubworkflowTasks=True)
```

### Skip task from workflow

Skips a given task execution from a currently running workflow.

```python
workflow_client.skip_task_from_workflow(workflow_id, "custom_task_ref")
```

### Delete workflow

```python
workflow_client.delete_workflow(workflow_id)
```
