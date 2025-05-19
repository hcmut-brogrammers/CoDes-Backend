from logging import Logger
from unittest.mock import Mock

import pytest
from pymongo.collection import Collection
from pymongo.database import Database

from ..common.auth import UserContext
from ..components.authenticate import (
    AuthenticateUser,
    CreateRefreshToken,
    RefreshAccessToken,
    RevokeRefreshToken,
    SignUp,
)
from ..components.design_projects import (
    CreateDesignProject,
    DeleteDesignProjectById,
    GetDesignProjectById,
    GetDesignProjectsByOrganizationId,
    UpdateDesignProject,
)
from ..components.join_organization_invitations import (
    AcceptOrRejectInvitation,
    CreateBatchJoinOrganizationInvitation,
    CreateJoinOrganizationInvitation,
    GetUserInvitations,
    MarkInvitationReadOrUnread,
)
from ..components.organizations import (
    CreateOrganization,
    CreateUserDefaultOrganization,
    CreateUserOrganization,
    DeleteOrganizationById,
    GetOrganizationById,
    GetOrganizationMembers,
    GetUserDefaultOrganization,
    GetUserOrganizationMembers,
    GetUserOrganizations,
    LeaveOrganization,
    UninviteOrganzationMember,
    UpdateUserOrganization,
)
from ..components.switch_organization import SwitchOrganization
from ..components.users import (
    AddUserToOrganization,
    CreateUser,
    DeleteUserById,
    GetMe,
    GetUserByEmail,
    GetUserByEmailFragment,
    GetUserById,
    RemoveUserFromOrganization,
    UpdateUser,
)
from ..services.jwt_service import JwtService


# NOTE: mock authenticate-related components
@pytest.fixture
def mock_sign_up() -> Mock:
    return Mock(spec=SignUp)


@pytest.fixture
def mock_authenticate_user() -> Mock:
    return Mock(spec=AuthenticateUser)


@pytest.fixture
def mock_refresh_access_token() -> Mock:
    return Mock(spec=RefreshAccessToken)


@pytest.fixture
def mock_revoke_refresh_token() -> Mock:
    return Mock(spec=RevokeRefreshToken)


@pytest.fixture
def mock_create_refresh_token() -> Mock:
    return Mock(spec=CreateRefreshToken)


@pytest.fixture
def mock_switch_organization() -> Mock:
    return Mock(spec=SwitchOrganization)


# NOTE: mock design project-related components
@pytest.fixture
def mock_create_design_project() -> Mock:
    return Mock(spec=CreateDesignProject)


@pytest.fixture
def mock_get_design_projects_by_organization_id() -> Mock:
    return Mock(spec=GetDesignProjectsByOrganizationId)


@pytest.fixture
def mock_update_design_project() -> Mock:
    return Mock(spec=UpdateDesignProject)


@pytest.fixture
def mock_delete_design_project_by_id() -> Mock:
    return Mock(spec=DeleteDesignProjectById)


@pytest.fixture
def mock_get_design_project_by_id() -> Mock:
    return Mock(spec=GetDesignProjectById)


# NOTE: mock join organization invitation-related components
@pytest.fixture
def mock_create_join_organization_invitation() -> Mock:
    return Mock(spec=CreateJoinOrganizationInvitation)


@pytest.fixture
def mock_create_batch_join_organization_invitation() -> Mock:
    return Mock(spec=CreateBatchJoinOrganizationInvitation)


@pytest.fixture
def mock_get_user_invitations() -> Mock:
    return Mock(spec=GetUserInvitations)


@pytest.fixture
def mock_accept_or_reject_invitation() -> Mock:
    return Mock(spec=AcceptOrRejectInvitation)


@pytest.fixture
def mock_mark_invitation_read_or_unread() -> Mock:
    return Mock(spec=MarkInvitationReadOrUnread)


# NOTE: mock organization-related components


@pytest.fixture
def mock_get_organization_by_id() -> Mock:
    return Mock(spec=GetOrganizationById)


@pytest.fixture
def mock_get_user_organizations() -> Mock:
    return Mock(spec=GetUserOrganizations)


@pytest.fixture
def mock_get_user_default_organization() -> Mock:
    return Mock(spec=GetUserDefaultOrganization)


@pytest.fixture
def mock_get_user_organization_members() -> Mock:
    return Mock(spec=GetUserOrganizationMembers)


@pytest.fixture
def mock_get_organization_members() -> Mock:
    return Mock(spec=GetOrganizationMembers)


@pytest.fixture
def mock_create_organization() -> Mock:
    return Mock(spec=CreateOrganization)


@pytest.fixture
def mock_create_user_organization() -> Mock:
    return Mock(spec=CreateUserOrganization)


@pytest.fixture
def mock_update_user_organization() -> Mock:
    return Mock(spec=UpdateUserOrganization)


@pytest.fixture
def mock_delete_organization_by_id() -> Mock:
    return Mock(spec=DeleteOrganizationById)


@pytest.fixture
def mock_leave_organization() -> Mock:
    return Mock(spec=LeaveOrganization)


@pytest.fixture
def mock_uninvite_organization_member() -> Mock:
    return Mock(spec=UninviteOrganzationMember)


@pytest.fixture
def mock_create_user_default_organization() -> Mock:
    return Mock(spec=CreateUserDefaultOrganization)


# NOTE: mock user-related components


@pytest.fixture
def mock_get_user_by_id() -> Mock:
    return Mock(spec=GetUserById)


@pytest.fixture
def mock_create_user() -> Mock:
    return Mock(spec=CreateUser)


@pytest.fixture
def mock_get_user_by_email_fragment() -> Mock:
    return Mock(spec=GetUserByEmailFragment)


@pytest.fixture
def mock_update_user() -> Mock:
    return Mock(spec=UpdateUser)


@pytest.fixture
def mock_delete_user_by_id() -> Mock:
    return Mock(spec=DeleteUserById)


@pytest.fixture
def mock_add_user_to_organization() -> Mock:
    return Mock(spec=AddUserToOrganization)


@pytest.fixture
def mock_remove_user_from_organization() -> Mock:
    return Mock(spec=RemoveUserFromOrganization)


@pytest.fixture
def mock_get_me() -> Mock:
    return Mock(spec=GetMe)


@pytest.fixture
def mock_get_user_by_email() -> Mock:
    return Mock(spec=GetUserByEmail)


# NOTE: mock service-related components
@pytest.fixture
def mock_jwt_service() -> Mock:
    return Mock(spec=JwtService)


# NOTE: mock other components


@pytest.fixture
def mock_collection() -> Mock:
    return Mock(spec=Collection)


@pytest.fixture
def mock_db(mock_collection: Mock) -> Mock:
    mock = Mock(spec=Database)
    mock.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock


@pytest.fixture
def mock_logger() -> Mock:
    return Mock(spec=Logger)


@pytest.fixture
def mock_user_context() -> Mock:
    return Mock(spec=UserContext)
