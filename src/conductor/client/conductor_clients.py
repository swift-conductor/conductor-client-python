from conductor.client.configuration.configuration import Configuration
from conductor.client.clients.metadata_client import MetadataClient
from conductor.client.clients.workflow_client import WorkflowClient
from conductor.client.clients.task_client import TaskClient
from conductor.client.clients.scheduler_client import SchedulerClient
from conductor.client.clients.secret_client import SecretClient
from conductor.client.clients.authorization_client import AuthorizationClient

class ConductorClients:
    def __init__(self, configuration: Configuration):
        self.configuration = configuration
        
    def getWorkflowClient(self) -> WorkflowClient:
        return WorkflowClient(self.configuration)

    def getAuthorizationClient(self) -> AuthorizationClient:
        return AuthorizationClient(self.configuration)

    def getMetadataClient(self) -> MetadataClient:
        return MetadataClient(self.configuration)
    
    def getSchedulerClient(self) -> SchedulerClient:
        return SchedulerClient(self.configuration)
    
    def getSecretClient(self) -> SecretClient:
        return SecretClient(self.configuration)
    
    def getTaskClient(self) -> TaskClient:
        return TaskClient(self.configuration)
    
    