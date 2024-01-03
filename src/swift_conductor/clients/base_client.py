from swift_conductor.configuration import Configuration
from swift_conductor.http.api_client import ApiClient
from swift_conductor.http.api.metadata_resource_api import MetadataResourceApi
from swift_conductor.http.api.workflow_resource_api import WorkflowResourceApi
from swift_conductor.http.api.task_resource_api import TaskResourceApi

import logging

class BaseClient(object):
    def __init__(self, configuration: Configuration):
        self.api_client = ApiClient(configuration)
        self.logger = logging.getLogger(
            Configuration.get_logging_formatted_name(__name__)
        )
        self.metadataResourceApi = MetadataResourceApi(self.api_client)
        self.taskResourceApi = TaskResourceApi(self.api_client)
        self.workflowResourceApi = WorkflowResourceApi(self.api_client)
    