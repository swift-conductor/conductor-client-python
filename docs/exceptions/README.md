# Exception Handling

## APIErrorCode

These are the error codes that are returned when any of the Conductor Clients throw an exception.

| Code  | Accessor | Description |
| --- | --- | --- |
|"NOT_FOUND"|APIErrorCode.NOT_FOUND|Object not found|
|"FORBIDDEN"|APIErrorCode.FORBIDDEN|Access to object is forbidden|
|"CONFLICT"|APIErrorCode.CONFLICT|Object already exists|
|"BAD_REQUEST"|APIErrorCode.BAD_REQUEST|Request not formed correctly|
|"REQUEST_TIMEOUT"|APIErrorCode.REQUEST_TIMEOUT|Request timed out|
|"UNKNOWN"|APIErrorCode.UNKNOWN|Unknown error|

## APIError

This is the exception that is thrown when an Conductor Client related SDK API method fails or returns an error.

```python
from conductor.client.exceptions.api_error import APIError, APIErrorCode
from conductor.client.configuration.configuration import Configuration
from conductor.client.clients.metadata_client import MetadataClient

WORKFLOW_NAME = 'test_workflow'

config = Configuration(server_api_url=SERVER_API_URL)
metadata_client = MetadataClient(config)

try:
    metadata_client.getWorkflowDef(WORKFLOW_NAME, 1)
except APIError as e:
    if e.code == APIErrorCode.NOT_FOUND:
        print(f"Error finding {WORKFLOW_NAME}: {e.message}")
    elif e.code == APIErrorCode.FORBIDDEN:
        print(f"Error accessing {WORKFLOW_NAME}: {e.message}")
    else:
        print(f"Error fetching {WORKFLOW_NAME}: {e.message}")
    
```
