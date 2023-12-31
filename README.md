# Swift Conductor SDK - Python

The `conductor-client-python` repository provides the client SDKs to manage:
1. Task workers
2. Tasks & Workflows
3. Schedules & Secrets
4. Role Based Access Control (RBAC)

## Task Workers

Building the task workers in Python mainly consists of the following steps:

1. Setup conductor-client-python package
2. Create and run task workers

### Setup Conductor Python Package​

* Create a virtual environment to build your package
```shell
virtualenv conductor
source conductor/bin/activate
```

* Get Conductor Python SDK
```shell
python3 -m pip install conductor-client-python
```

#### Server Settings

Everything related to server settings should be done within the `Configuration` class by setting the required parameter (when initializing an object) like this:

```python
from conductor.client.configuration.configuration import Configuration

configuration = Configuration(
    server_api_url='http://localhost:8080/api',
    debug=True
)
```

* server_api_url : Conductor server address. For example, if you are running locally, it would look like; `http://localhost:8080/api`.
* debug: It can take the values true/false. `true` for verbose logging `false` to display only the errors


```python
from conductor.client.configuration.configuration import Configuration

configuration = Configuration()
```

#### Metrics Settings (Optional)

Conductor uses [Prometheus](https://prometheus.io/) to collect metrics.

```python
metrics_settings = MetricsSettings(
    directory='/path/to/folder',
    file_name='metrics_file_name.extension',
    update_interval=0.1,
)
```

* `directory`: Directory to store the metrics.
  * Ensure that you have already created this folder, or the program should have permission to create it for you.
* `file_name`: File where the metrics are stored.
  * example: `metrics.log`
* `update_interval`: Time interval in seconds to refresh metrics into the file.
  * example: `0.1` means metrics are updated every  0.1s or 100ms.

### Create and Run Task Workers

The next step is to [create and run task workers](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/worker).

## Tasks & Workflows

Builing tasks and workflows involve usage of Swift Conductor Clients that can be used to do the following:

### Create task and workflow definitions

We can use the metadata client to [manage task and workflow definitions](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/metadata).

### Execute Workflows using Code

You can [execute workflows using code](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/workflow).

### Task Management

You can [manage tasks using code](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/task).

### Unit Testing Workflows

You can [unit test your conductor workflows on a remote server before running them on production.](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/testing).

### Error Handling

You can [handle errors returned from any of the Python Client SDK methods](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/exceptions).

## Schedules & Secrets

### Schedule Management

You can [manage schedules using code](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/schedule).

### Secret Management

You can [manage secrets using code](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/secret).

## Role Based Access Control (RBAC)

### Access Control Management

You can [manage applications, users, groups and permissions using code](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/authorization).
