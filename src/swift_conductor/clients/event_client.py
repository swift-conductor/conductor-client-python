from swift_conductor.configuration import Configuration
from swift_conductor.clients.base_client import BaseClient
from swift_conductor.http.api.event_resource_api import EventResourceApi
from swift_conductor.event_queue.queue_configuration import QueueConfiguration


class EventClient(BaseClient):
    def __init__(self, configuration: Configuration):
        super(EventClient, self).__init__(configuration)
        self.client = EventResourceApi(self.api_client)

    def delete_queue_configuration(self, queue_configuration: QueueConfiguration) -> None:
        return self.client.delete_queue_config(
            queue_name=queue_configuration.queue_name,
            queue_type=queue_configuration.queue_type,
        )

    def get_queue_configuration(self, queue_type: str, queue_name: str):
        return self.client.get_queue_config(queue_type, queue_name)

    def put_queue_configuration(self, queue_configuration: QueueConfiguration):
        return self.client.put_queue_config(
            body=queue_configuration.get_worker_configuration(),
            queue_name=queue_configuration.queue_name,
            queue_type=queue_configuration.queue_type,
        )
