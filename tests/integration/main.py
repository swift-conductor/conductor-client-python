from swift_conductor.configuration import Configuration
from swift_conductor.http.api_client import ApiClient
from swift_conductor.workflow.workflow_manager import WorkflowManager
from metadata.test_workflow_definition import run_workflow_definition_tests
from workflow.test_workflow_execution import run_workflow_execution_tests
from client.clients.test_client_clients import TestClients

import logging
import sys
import os

_logger = logging.getLogger(
    Configuration.get_logging_formatted_name(
        __name__
    )
)

def generate_configuration():
    required_envs = {
        'URL': 'CONDUCTOR_SERVER_URL',
    }
    envs = {}
    for key, env in required_envs.items():
        value = os.getenv(env)
        if value is None or value == '':
            _logger.warning(f'ENV not set - {env}')
        else:
            envs[key] = value
    params = {
        'server_api_url': envs['URL'],
        'debug': True,
    }

    configuration = Configuration(**params)
    configuration.apply_logging_config()
    return configuration


def main():
    args = sys.argv[1:]
    configuration = generate_configuration()
    workflow_manager = WorkflowManager(configuration)

    if len(args) == 1 and args[0] == '--clients-only':
        test_clients = TestClients(configuration=configuration)
        test_clients.run()
    elif len(args) == 1 and args[0] == '--workflow-execution-only':
        run_workflow_execution_tests(configuration, workflow_manager)
    else:
        run_workflow_definition_tests(workflow_manager)
        run_workflow_execution_tests(configuration, workflow_manager)
        TestClients(configuration=configuration).run()


if __name__ == "__main__":
    main()
