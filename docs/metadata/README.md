# Authoring Workflows

## Workflow Definition Management

### Register Workflow Definition

In order to define a workflow, you must provide a `MetadataClient` and a `WorkflowManager`, which requires a `Configuration` object with the Conductor Server info. Here's an example on how to do that:

```python
from conductor.client.configuration.configuration import Configuration
from conductor.client.clients.metadata_client import MetadataClient
from conductor.client.workflow.conductor_workflow import ConductorWorkflow
from conductor.client.workflow.manager.workflow_manager import WorkflowManager

configuration = Configuration(
    server_api_url=SERVER_API_URL,
    debug=False
)

metadata_client = MetadataClient(configuration)

workflow_manager = WorkflowManager(configuration)
workflow = ConductorWorkflow(
    manager=workflow_manager,
    name='python_workflow_example_from_code',
    description='Python workflow example from code'
)
```

After creating an instance of a `ConductorWorkflow`, you can start adding tasks to it. There are two possible ways to do that:
* method: `add`
* operator: `>>`

```python
from conductor.client.workflow.task.simple_task import SimpleTask

simple_task_1 = SimpleTask(
    task_def_name='python_simple_task_from_code_1',
    task_reference_name='python_simple_task_from_code_1'
)
workflow.add(simple_task_1)

simple_task_2 = SimpleTask(
    task_def_name='python_simple_task_from_code_2',
    task_reference_name='python_simple_task_from_code_2'
)
workflow >> simple_task_2
```

You can add input parameters to your workflow:

```python
workflow.input_parameters(["a", "b"])
```

You should be able to register your workflow at the Conductor Server:

```python
from conductor.client.http.models.workflow_def import WorkflowDef

workflowDef = workflow.to_workflow_def()
metadata_client.registerWorkflowDef(workflowDef, True)
```

### Get Workflow Definition

You should be able to get your workflow definition that you added previously:

```python
wfDef = metadata_client.getWorkflowDef('python_workflow_example_from_code')
```

In case there is an error in fetching the definition, errorStr will be populated.

### Update Workflow Definition

You should be able to update your workflow after adding new tasks:

```python
workflow >> SimpleTask("simple_task", "simple_task_ref_2")
updatedWorkflowDef = workflow.to_workflow_def()
metadata_client.updateWorkflowDef(updatedWorkflowDef, True)
```

### Unregister Workflow Definition

You should be able to unregister your workflow by passing name and version:

```python
metadata_client.unregisterWorkflowDef('python_workflow_example_from_code', 1)
```

## Task Definition Management

### Register Task Definition

You should be able to register your task at the Conductor Server:

```python
from conductor.client.http.models.task_def import TaskDef

taskDef = TaskDef(
    name= "PYTHON_TASK",
    description="Python Task Example",
    input_keys=["a", "b"]
)
metadata_client.registerTaskDef(taskDef)
```

### Get Task Definition

You should be able to get your task definition that you added previously:

```python
taskDef = metadata_client.getTaskDef('PYTHON_TASK')
```

### Update Task Definition

You should be able to update your task definition by modifying field values:

```python
taskDef.description = "Python Task Example New Description"
taskDef.input_keys = ["a", "b", "c"]
metadata_client.updateTaskDef(taskDef)
```

### Unregister Task Definition

You should be able to unregister your task at the Conductor Server:

```python
metadata_client.unregisterTaskDef('python_task_example_from_code')
```
