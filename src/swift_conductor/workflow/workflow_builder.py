from swift_conductor.task.fork_task import ForkTask
from swift_conductor.task.join_task import JoinTask
from swift_conductor.task.task import TaskInterface
from swift_conductor.task.timeout_policy import TimeoutPolicy
from swift_conductor.http.models import *
from copy import deepcopy
from typing import Any, Dict, List, Union
from typing_extensions import Self
from shortuuid import uuid


class WorkflowBuilder:
    SCHEMA_VERSION = 2

    def __init__(self,
                 name: str,
                 version: int = None,
                 description: str = None) -> Self:
        self.name = name
        self.version = version
        self.description = description
        self._tasks = []
        self._owner_email = None
        self._timeout_policy = None
        self._timeout_seconds = 60
        self._failure_workflow = ''
        self._input_parameters = []
        self._output_parameters = {}
        self._input_template = {}
        self._variables = {}
        self._restartable = True

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        if not isinstance(name, str):
            raise Exception('invalid type')
        self._name = deepcopy(name)

    @property
    def version(self) -> int:
        return self._version

    @version.setter
    def version(self, version: int) -> None:
        if version != None and not isinstance(version, int):
            raise Exception('invalid type')
        self._version = deepcopy(version)

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, description: str) -> None:
        if description != None and not isinstance(description, str):
            raise Exception('invalid type')
        self._description = deepcopy(description)

    def timeout_policy(self, timeout_policy: TimeoutPolicy) -> Self:
        if not isinstance(timeout_policy, TimeoutPolicy):
            raise Exception('invalid type')
        self._timeout_policy = deepcopy(timeout_policy)
        return self

    def timeout_seconds(self, timeout_seconds: int) -> Self:
        if not isinstance(timeout_seconds, int):
            raise Exception('invalid type')
        self._timeout_seconds = deepcopy(timeout_seconds)
        return self

    def owner_email(self, owner_email: str) -> Self:
        if not isinstance(owner_email, str):
            raise Exception('invalid type')
        self._owner_email = deepcopy(owner_email)
        return self

    # Name of the workflow to execute when this workflow fails.
    # Failure workflows can be used for handling compensation logic
    def failure_workflow(self, failure_workflow: str) -> Self:
        if not isinstance(failure_workflow, str):
            raise Exception('invalid type')
        self._failure_workflow = deepcopy(failure_workflow)
        return self

    # If the workflow can be restarted after it has reached terminal state.
    # Set this to false if restarting workflow can have side effects
    def restartable(self, restartable: bool) -> Self:
        if not isinstance(restartable, bool):
            raise Exception('invalid type')
        self._restartable = deepcopy(restartable)
        return self

    # Workflow output follows similar structure as task input
    # See https://swiftconductor.com/devguide/how-tos/Tasks/task-inputs.html for more details
    def output_parameters(self, output_parameters: Dict[str, Any]) -> Self:
        if output_parameters == None:
            self._output_parameters = {}
            return
        if not isinstance(output_parameters, dict):
            raise Exception('invalid type')
        for key in output_parameters.keys():
            if not isinstance(key, str):
                raise Exception('invalid type')
        self._output_parameters = deepcopy(output_parameters)
        return self

    # InputTemplate template input to the workflow.  Can have combination of variables (e.g. ${workflow.input.abc}) and static values
    def input_template(self, input_template: Dict[str, Any]) -> Self:
        if input_template == None:
            self._input_template = {}
            return
        if not isinstance(input_template, dict):
            raise Exception('invalid type')
        for key in input_template.keys():
            if not isinstance(key, str):
                raise Exception('invalid type')
        self._input_template = deepcopy(input_template)
        return self

    # Variables are set using SET_VARIABLE task. Excellent way to maintain business state
    # e.g. Variables can maintain business/user specific states which can be queried and inspected to find out the state of the workflow
    def variables(self, variables: Dict[str, Any]) -> Self:
        if variables == None:
            self._variables = {}
            return
        if not isinstance(variables, dict):
            raise Exception('invalid type')
        for key in variables.keys():
            if not isinstance(key, str):
                raise Exception('invalid type')
        self._variables = deepcopy(variables)
        return self

    # List of the input parameters to the workflow. Usage: documentation ONLY
    def input_parameters(self, input_parameters: List[str]) -> Self:
        if not isinstance(input_parameters, list):
            raise Exception('invalid type')
        for input_parameter in input_parameters:
            if not isinstance(input_parameter, str):
                raise Exception('invalid type')
        self._input_parameters = deepcopy(input_parameters)
        return self

    # Converts the workflow to the JSON serializable format
    def to_workflow_def(self) -> WorkflowDef:
        return WorkflowDef(
            name=self._name,
            description=self._description,
            version=self._version,
            tasks=self.__get_workflow_task_list(),
            input_parameters=self._input_parameters,
            output_parameters=self._output_parameters,
            failure_workflow=self._failure_workflow,
            schema_version=WorkflowBuilder.SCHEMA_VERSION,
            owner_email=self._owner_email,
            timeout_policy=self._timeout_policy,
            timeout_seconds=self._timeout_seconds,
            variables=self._variables,
            input_template=self._input_template,
        )

    def __get_workflow_task_list(self) -> List[WorkflowTask]:
        workflow_task_list = []
        for task in self._tasks:
            converted_task = task.to_workflow_task()
            if isinstance(converted_task, list):
                for subtask in converted_task:
                    workflow_task_list.append(subtask)
            else:
                workflow_task_list.append(converted_task)
        return workflow_task_list

    # Append task with the right shift operator `>>`
    def __rshift__(self, task: Union[TaskInterface, List[TaskInterface], List[List[TaskInterface]]]) -> Self:
        if isinstance(task, list):
            forked_tasks = []
            for fork_task in task:
                if isinstance(fork_task, list):
                    forked_tasks.append(fork_task)
                else:
                    forked_tasks.append([fork_task])
            return self.__add_fork_join_tasks(forked_tasks)
        return self.__add_task(task)

    # Append task
    def add(self, task: TaskInterface) -> Self:
        return self.__add_task(task)

    def __add_task(self, task: TaskInterface) -> Self:
        if not issubclass(type(task), TaskInterface):
            raise Exception('invalid type')
        self._tasks.append(deepcopy(task))
        return self

    def __add_fork_join_tasks(self, forked_tasks: List[List[TaskInterface]]) -> Self:
        for single_fork in forked_tasks:
            for task in single_fork:
                if not issubclass(type(task), TaskInterface):
                    raise Exception('invalid type')

        suffix = str(uuid())

        fork_task = ForkTask(
            task_ref_name='forked_' + suffix,
            forked_tasks=forked_tasks
        )
        
        join_task = JoinTask(
            task_ref_name='join_' + suffix,
            join_on=fork_task.to_workflow_task().join_on
        )
        
        self._tasks.append(fork_task)
        self._tasks.append(join_task)
        return self
