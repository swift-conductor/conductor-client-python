# Swift Conductor Client SDK for Python

## ⭐ Swift Conductor

Show support for Swift Conductor.  Please help spread the awareness by starring Swift Conductor repo.

[![GitHub stars](https://img.shields.io/github/stars/swift-conductor/conductor.svg?style=social&label=Star&maxAge=)](https://GitHub.com/swift-conductor/conductor/)


Install:

```shell
pip install swift-conductor-client
```

## Create Tasks and Workflows

[Create task and workflow definitions](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/metadata.md).  

[Execute workflows](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/workflow.md).

[Manage tasks](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/task.md).

## Create Task Workers

[Create and run task workers](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/worker.md)

## Testing Workflows

[Test your workflows](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/testing.md)

### Error Handling

[Handle errors returned Client SDK methods](https://github.com/swift-conductor/conductor-client-python/tree/main/docs/exceptions.md)

## Configuration

Configure Swift Conductor API URL like this: 

```python
from swift_conductor.configuration import Configuration

configuration = Configuration(
    server_api_url='http://localhost:8080/api',
    debug=True
)
```

* server_api_url : Swift Conductor API URL. For example, if you are running a local server the URL will look like this `http://localhost:8080/api`.
* debug: Set to `True` for verbose logging and `False` to print only errors.

## Metrics Configuration for WorkerHost (Optional)

Swift Conductor uses [Prometheus](https://prometheus.io/) to collect metrics.

```python
metrics_settings = MetricsSettings(
    directory='/path/to/folder',
    file_name='metrics_file_name.extension',
    update_interval=0.1,
)
```

* `directory`: Directory to store the metrics. Ensure that you have already created this folder, or the program should have permission to create it for you.
* `file_name`: File where the metrics are stored. Example: `metrics.log`
* `update_interval`: Time interval in seconds to refresh metrics into the file. Example: `0.1` means metrics are updated every  0.1s or 100ms.

Pass the `MetricsSettings` object to the `WorkerHost` constructor. 

