from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from ....common.models import OrganizationModel
from ....components.organizations.create_organization import CreateOrganization
from ....exceptions import InternalServerError

# from ....exceptions import InternalServerError

# from src.common.models.base import PyObjectUUID
# from src.common.models.organization import OrganizationModel
# from src.components.organizations.create_organization import CreateOrganization


MockSetUp = tuple[Mock, Mock, Mock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_user_context = Mock()
    mock_collection = AsyncMock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_user_context, mock_collection


class TestCreateOrganization:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_collection = mock_setup

        # Mock user_context
        # TODO: implement...
        user_id = uuid4()
        # mock_user_context.configure_mock(user_id=Mock(return_value=user_id))
        # # mock behavious: mock_user_context.user_id() -> return value: user_id
        mock_user_context.configure_mock(user_id=user_id)
        # mock behaviour: mock_user_context.user_id -> return_value: user_id

        # Mock request and database response
        organization = OrganizationModel(
            name="org_test",
            avatar_url="http://example.com/avatar.png",
            owner_id=user_id,
        )
        # mock_inserted_id = uuid4()  # Use uuid4 to generate a valid UUID object
        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=organization.id)),
            find_one=Mock(return_value=organization.model_dump(by_alias=True)),
        )
        # organization
        # ->
        # {
        #     "_id": "123",
        #     "name": "org_test"
        #     "avatar_url": "http://example.com/avatar.png",
        #     "owner_id": user_id,
        # }

        # Initialize the component
        create_organization = CreateOrganization(db=mock_db, logger=mock_logger, user_context=mock_user_context)

        # Execute the component
        request = CreateOrganization.Request(name=organization.name, avatar_url=organization.avatar_url)
        response = await create_organization.aexecute(request)

        # Assertions
        assert response.created_organization is not None
        assert response.created_organization.owner_id == user_id
        assert response.created_organization.name == organization.name
        assert response.created_organization.avatar_url == organization.avatar_url

        print("here_is_organization_id: " + str(organization.id))
        # fail do 2 organization.id khác khau
        # organization ở expect và actual là 2 instances khác khau?
        mock_collection.insert_one.assert_called_once_with(organization.model_dump(by_alias=True))
        mock_collection.find_one.assert_called_once_with({"_id": organization.id})

    @pytest.mark.asyncio
    async def test_aexecute_when_organization_not_found_throws_internal_server_error(
        self, mock_setup: MockSetUp
    ) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_collection = mock_setup

        # Mock user_cont
        user_id = uuid4()
        mock_user_context.configure_mock(user_id=user_id)

        # Mock request and database response
        organization = OrganizationModel(
            name="org_test",
            avatar_url="http://example.com/avatar.png",
            owner_id=user_id,
        )
        # mock_inserted_id = uuid4()  # Use uuid4 to generate a valid UUID object
        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=organization.id)),
            find_one=Mock(return_value=None),
        )

        # Initialize the component
        create_organization = CreateOrganization(db=mock_db, logger=mock_logger, user_context=mock_user_context)

        # Execute the component
        request = CreateOrganization.Request(
            name=organization.name,
            avatar_url=organization.avatar_url,
        )
        with pytest.raises(InternalServerError):
            await create_organization.aexecute(request)

        # Verify interactions
        mock_collection.insert_one.assert_called_once()
        mock_collection.find_one.assert_called_once_with({"_id": organization.id})
