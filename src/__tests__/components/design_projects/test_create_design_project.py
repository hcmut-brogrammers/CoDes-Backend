from unittest.mock import Mock
from uuid import UUID

import pytest

from ....common.models import DesignProjectModel, UserRole
from ....components.design_projects import CreateDesignProject
from ....exceptions import BadRequestError, InternalServerError
from ....utils.common import generate_uuid


@pytest.fixture
def mock_user_id() -> UUID:
    return generate_uuid()


@pytest.fixture
def mock_organization_id() -> UUID:
    return generate_uuid()


@pytest.fixture
def mock_user_context_admin(mock_user_id, mock_organization_id):
    mock = Mock()
    mock.configure_mock(
        user_id=mock_user_id,
        organization_id=mock_organization_id,
        role=UserRole.OrganizationAdmin,
    )
    return mock


@pytest.fixture
def mock_user_context_non_admin(mock_user_id, mock_organization_id):
    mock = Mock()
    mock.configure_mock(
        user_id=mock_user_id,
        organization_id=mock_organization_id,
        role=UserRole.OrganizationMember,
    )
    return mock


@pytest.fixture
def mock_project(mock_user_id, mock_organization_id):
    return DesignProjectModel(
        name="Test Project",
        thumbnail_url="https://s3-figma-hubfile-images-production.figma.com/hub/file/carousel/img/238a7016bbc93dbc4aa491c39f0f9c4595f31dee",
        owner_id=mock_user_id,
        organization_id=mock_organization_id,
        elements=[],
    )


class TestCreateDesignProject:
    @pytest.mark.asyncio
    async def test_aexecute_success(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_collection: Mock,
        mock_user_context_admin: Mock,
        mock_project: DesignProjectModel,
    ) -> None:
        # Arrange
        mock_collection.configure_mock(
            find_one=Mock(return_value=mock_project.model_dump(by_alias=True)),
            insert_one=Mock(return_value=Mock(inserted_id=mock_project.id)),
        )
        create_design_project = CreateDesignProject(
            db=mock_db, logger=mock_logger, user_context=mock_user_context_admin
        )

        # Act
        request = CreateDesignProject.Request(
            name=mock_project.name, thumbnail_url="https://example.com/thumbnail.png", elements=[]
        )
        response = await create_design_project.aexecute(request)

        # Assert
        assert response.created_project is not None
        assert response.created_project.name == mock_project.name
        assert response.created_project.owner_id == mock_project.owner_id
        assert response.created_project.organization_id == mock_project.organization_id
        assert response.created_project.thumbnail_url == mock_project.thumbnail_url
        mock_collection.insert_one.assert_called_once()
        mock_collection.find_one.assert_called_once_with({"_id": mock_project.id})

    @pytest.mark.asyncio
    async def test_aexecute_when_user_is_not_admin_should_raise_bad_request(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_collection: Mock,
        mock_user_context_non_admin: Mock,
        mock_project: DesignProjectModel,
    ) -> None:
        # Arrange
        create_design_project = CreateDesignProject(
            db=mock_db, logger=mock_logger, user_context=mock_user_context_non_admin
        )

        # Act & Assert
        request = CreateDesignProject.Request(
            name=mock_project.name, thumbnail_url="https://example.com/thumbnail.png", elements=[]
        )
        with pytest.raises(BadRequestError):
            await create_design_project.aexecute(request)
        mock_collection.find_one.assert_not_called()
        mock_collection.insert_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_aexecute_when_inserted_but_not_found_should_raise_internal_server_error(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_collection: Mock,
        mock_user_context_admin: Mock,
        mock_project: DesignProjectModel,
    ) -> None:
        # Arrange
        mock_collection.configure_mock(
            find_one=Mock(return_value=None),
            insert_one=Mock(return_value=Mock(inserted_id=mock_project.id)),
        )
        create_design_project = CreateDesignProject(
            db=mock_db, logger=mock_logger, user_context=mock_user_context_admin
        )

        # Act & Assert
        request = CreateDesignProject.Request(
            name=mock_project.name, thumbnail_url="https://example.com/thumbnail.png", elements=[]
        )
        with pytest.raises(InternalServerError):
            await create_design_project.aexecute(request)
        mock_collection.insert_one.assert_called_once()
        mock_collection.find_one.assert_called_once_with({"_id": mock_project.id})
