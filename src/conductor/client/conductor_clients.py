from conductor.client.configuration.configuration import Configuration
from conductor.client.clients.metadata_client import MetadataClient
from conductor.client.clients.workflow_client import WorkflowClient
from conductor.client.clients.task_client import TaskClient

class ConductorClients:
    def __init__(self, configuration: Configuration):
        self.configuration = configuration
        
    def getWorkflowClient(self) -> WorkflowClient:
        return WorkflowClient(self.configuration)

    def getMetadataClient(self) -> MetadataClient:
        return MetadataClient(self.configuration)
    
    def getTaskClient(self) -> TaskClient:
        return TaskClient(self.configuration)
    
    