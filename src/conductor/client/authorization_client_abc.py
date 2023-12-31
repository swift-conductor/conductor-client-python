from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from conductor.client.clients.models.metadata_tag import MetadataTag
from conductor.client.clients.models.access_type import AccessType
from conductor.client.clients.models.granted_permission import GrantedPermission
from conductor.client.clients.models.access_key import AccessKey
from conductor.client.clients.models.created_access_key import CreatedAccessKey
from conductor.client.http.models.group import Group
from conductor.client.http.models.target_ref import TargetRef
from conductor.client.http.models.subject_ref import SubjectRef
from conductor.client.http.models.conductor_user import ConductorUser
from conductor.client.http.models.conductor_application import ConductorApplication
from conductor.client.http.models.upsert_user_request import UpsertUserRequest
from conductor.client.http.models.upsert_group_request import UpsertGroupRequest
from conductor.client.http.models.authorization_request import AuthorizationRequest
from conductor.client.http.models.create_or_update_application_request import CreateOrUpdateApplicationRequest

class AuthorizationClientABC(ABC):
    # Applications
    @abstractmethod
    def createApplication(
        self,
        createOrUpdateApplicationRequest: CreateOrUpdateApplicationRequest
    ) -> ConductorApplication:
        pass
    
    @abstractmethod
    def getApplication(self, applicationId: str) -> ConductorApplication:
        pass
    
    @abstractmethod
    def listApplications(self) -> List[ConductorApplication]:
        pass
    
    @abstractmethod
    def updateApplication(
        self,
        createOrUpdateApplicationRequest: CreateOrUpdateApplicationRequest,
        applicationId: str
    ) -> ConductorApplication:
        pass

    @abstractmethod
    def deleteApplication(self, applicationId: str):
        pass
    
    @abstractmethod
    def addRoleToApplicationUser(self, applicationId: str, role: str):
        pass
    
    @abstractmethod
    def removeRoleFromApplicationUser(self, applicationId: str, role: str):
        pass
    
    @abstractmethod
    def setApplicationTags(self, tags: List[MetadataTag], applicationId: str):
        pass

    @abstractmethod
    def getApplicationTags(self, applicationId: str) -> List[MetadataTag]:
        pass

    @abstractmethod
    def deleteApplicationTags(self, tags: List[MetadataTag], applicationId: str):
        pass

    @abstractmethod
    def createAccessKey(self, applicationId: str) -> CreatedAccessKey:
        pass
    
    @abstractmethod
    def getAccessKeys(self, applicationId: str) -> List[AccessKey]:
        pass
    
    @abstractmethod
    def toggleAccessKeyStatus(self, applicationId: str, keyId: str) -> AccessKey:
        pass

    @abstractmethod
    def deleteAccessKey(self, applicationId: str, keyId: str):
        pass
    
    # Users
    @abstractmethod
    def upsertUser(self, upsertUserRequest: UpsertUserRequest, userId: str) -> ConductorUser:
        pass
    
    @abstractmethod
    def getUser(self, userId: str) -> ConductorUser:
        pass
    
    @abstractmethod
    def listUsers(self, apps: Optional[bool] = False) -> List[ConductorUser]:
        pass

    @abstractmethod
    def deleteUser(self, userId: str):
        pass
    
    # Groups
    @abstractmethod
    def upsertGroup(self, upsertGroupRequest: UpsertGroupRequest, groupId: str) -> Group:
        pass
        
    @abstractmethod
    def getGroup(self, groupId: str) -> Group:
        pass
    
    @abstractmethod
    def listGroups(self) -> List[Group]:
        pass

    @abstractmethod
    def deleteGroup(self, groupId: str):
        pass
    
    @abstractmethod
    def addUserToGroup(self, groupId: str, userId: str):
        pass
    
    @abstractmethod
    def getUsersInGroup(self, groupId: str) -> List[ConductorUser]:
        pass
    
    @abstractmethod
    def removeUserFromGroup(self, groupId: str, userId: str):
        pass

    # Permissions
    @abstractmethod
    def grantPermissions(self, subject: SubjectRef, target: TargetRef, access: List[AccessType]):
        pass
    
    @abstractmethod
    def getPermissions(self, target: TargetRef) -> Dict[str, List[SubjectRef]]:
        pass

    @abstractmethod
    def getGrantedPermissionsForGroup(self, groupId: str) -> List[GrantedPermission]:
        pass

    @abstractmethod
    def getGrantedPermissionsForUser(self, userId: str) -> List[GrantedPermission]:
        pass

    @abstractmethod
    def removePermissions(self, subject: SubjectRef, target: TargetRef, access: List[AccessType]):
        pass
