from typing import Optional, List
from conductor.client.configuration.configuration import Configuration
from conductor.client.clients.models.metadata_tag import MetadataTag
from conductor.client.http.models.workflow_schedule import WorkflowSchedule
from conductor.client.scheduler_client_abc import SchedulerClientABC
from conductor.client.http.models.save_schedule_request import SaveScheduleRequest
from conductor.client.http.models.search_result_workflow_schedule_execution_model import SearchResultWorkflowScheduleExecutionModel
from conductor.client.clients.base_client import BaseClient
from conductor.client.exceptions.api_exception_handler import api_exception_handler, for_all_methods

@for_all_methods(api_exception_handler, ["__init__"])
class SchedulerClient(BaseClient, SchedulerClientABC):
    def __init__(self, configuration: Configuration):
        super(SchedulerClient, self).__init__(configuration)
        
    def saveSchedule(self, saveScheduleRequest: SaveScheduleRequest):
        self.schedulerResourceApi.save_schedule(saveScheduleRequest)
    
    def getSchedule(self, name: str) -> WorkflowSchedule:
        return self.schedulerResourceApi.get_schedule(name)

    def getAllSchedules(self, workflowName: Optional[str] = None) -> List[WorkflowSchedule]:
        kwargs = {}
        if workflowName:
            kwargs.update({"workflow_name": workflowName})

        return self.schedulerResourceApi.get_all_schedules(**kwargs)

    def getNextFewScheduleExecutionTimes(self,
        cronExpression: str,
        scheduleStartTime: Optional[int] = None,
        scheduleEndTime: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[int]:
        kwargs = {}
        if scheduleStartTime:
            kwargs.update({"schedule_start_time": scheduleStartTime})
        if scheduleEndTime:
            kwargs.update({"schedule_end_time": scheduleEndTime})
        if limit:
            kwargs.update({"limit": limit})
        return self.schedulerResourceApi.get_next_few_schedules(cronExpression, **kwargs)

    def deleteSchedule(self, name: str):
        self.schedulerResourceApi.delete_schedule(name)

    def pauseSchedule(self, name: str):
        self.schedulerResourceApi.pause_schedule(name)
    
    def pauseAllSchedules(self):
        self.schedulerResourceApi.pause_all_schedules()

    def resumeSchedule(self, name: str):
        self.schedulerResourceApi.resume_schedule(name)
    
    def resumeAllSchedules(self):
        self.schedulerResourceApi.resume_all_schedules()
    
    def searchScheduleExecutions(self,
        start: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        freeText: Optional[str] = None,
        query: Optional[str] = None,
    ) -> SearchResultWorkflowScheduleExecutionModel:
        kwargs = {}
        if start:
            kwargs.update({"start": start})
        if size:
            kwargs.update({"size": size})
        if sort:
            kwargs.update({"sort": sort})
        if freeText:
            kwargs.update({"freeText": freeText})
        if query:
            kwargs.update({"query": query})
        return self.schedulerResourceApi.search_v21(**kwargs)
    
    def requeueAllExecutionRecords(self):
        self.schedulerResourceApi.requeue_all_execution_records()
    
    def setSchedulerTags(self, tags: List[MetadataTag], name: str):
        self.schedulerResourceApi.put_tag_for_schedule(tags, name)

    def getSchedulerTags(self, name: str) -> List[MetadataTag]:
        return self.schedulerResourceApi.get_tags_for_schedule(name)
        
    def deleteSchedulerTags(self, tags: List[MetadataTag], name: str)  -> List[MetadataTag]:
        self.schedulerResourceApi.delete_tag_for_schedule(tags, name)
