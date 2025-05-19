from unittest.mock import AsyncMock, Mock

import pytest

from ....common.models import DesignProjectModel
from ....components.design_projects import CreateDesignProject, DuplicateDesignProject, GetDesignProjectById
from ....exceptions import BadRequestError
from ....utils.common import generate_uuid


@pytest.fixture
def mock_project():
    return DesignProjectModel(
        name="Test Project",
        thumbnail_url="https://s3-figma-hubfile-images-production.figma.com/hub/file/carousel/img/238a7016bbc93dbc4aa491c39f0f9c4595f31dee",
        owner_id=generate_uuid(),
        organization_id=generate_uuid(),
        elements=[],
    )


class TestDuplicateDesignProject:
    @pytest.mark.asyncio
    async def test_aexecute_success(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_create_design_project: Mock,
        mock_get_design_project_by_id: Mock,
        mock_project,
    ):
        # Arrange
        mock_user_context.configure_mock(organization_id=mock_project.organization_id)
        mock_get_design_project_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetDesignProjectById.Response(design_project=mock_project))
        )
        duplicated_project = DesignProjectModel(
            name=f"Copy of {mock_project.name}",
            thumbnail_url=mock_project.thumbnail_url,
            owner_id=mock_project.owner_id,
            organization_id=mock_project.organization_id,
            elements=mock_project.elements,
        )
        mock_create_design_project.configure_mock(
            aexecute=AsyncMock(return_value=CreateDesignProject.Response(created_project=duplicated_project))
        )
        duplicate_design_project = DuplicateDesignProject(
            db=mock_db,
            logger=mock_logger,
            user_context=mock_user_context,
            create_design_project=mock_create_design_project,
            get_design_project_by_id=mock_get_design_project_by_id,
        )
        request = duplicate_design_project.Request(project_id=mock_project.id)
        # Act
        response = await duplicate_design_project.aexecute(request)
        # Assert
        assert response.duplicated_project.name == f"Copy of {mock_project.name}"
        assert response.duplicated_project.organization_id == mock_project.organization_id
        assert response.duplicated_project.thumbnail_url == mock_project.thumbnail_url
        mock_get_design_project_by_id.aexecute.assert_called_once()
        mock_create_design_project.aexecute.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexecute_no_permission(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_create_design_project: Mock,
        mock_get_design_project_by_id: Mock,
        mock_project,
    ):
        # Arrange: user org does not match project org
        mock_user_context.configure_mock(organization_id=generate_uuid())
        mock_get_design_project_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetDesignProjectById.Response(design_project=mock_project))
        )
        duplicate_design_project = DuplicateDesignProject(
            db=mock_db,
            logger=mock_logger,
            user_context=mock_user_context,
            create_design_project=mock_create_design_project,
            get_design_project_by_id=mock_get_design_project_by_id,
        )
        request = duplicate_design_project.Request(project_id=mock_project.id)
        # Act & Assert
        with pytest.raises(BadRequestError):
            await duplicate_design_project.aexecute(request)
        mock_get_design_project_by_id.aexecute.assert_called_once()
        mock_create_design_project.aexecute.assert_not_called()
