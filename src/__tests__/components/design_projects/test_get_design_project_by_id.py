from unittest.mock import Mock

import pytest

from ....common.models import DesignProjectModel
from ....components.design_projects import GetDesignProjectById
from ....exceptions import NotFoundError
from ....utils.common import generate_uuid


@pytest.fixture
def mock_project():
    return DesignProjectModel(
        name="Test Project",
        thumbnail_url="https://s3-figma-hubfile-images-production.figma.com/hub/file/carousel/img/238a7016bbc93dbc4aa491c39f0f9c4595f31dee",
        owner_id=generate_uuid(),
        organization_id=generate_uuid(),
    )


class TestGetDesignProjectById:
    @pytest.mark.asyncio
    async def test_aexecute_success(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_collection: Mock,
        mock_project: DesignProjectModel,
    ) -> None:
        # Arrange
        mock_collection.configure_mock(find_one=Mock(return_value=mock_project.model_dump(by_alias=True)))
        create_design_project = GetDesignProjectById(db=mock_db, logger=mock_logger)

        # Act
        request = GetDesignProjectById.Request(project_id=mock_project.id)
        response = await create_design_project.aexecute(request)

        # Assert
        assert response.design_project is not None
        assert response.design_project.name == mock_project.name
        assert response.design_project.owner_id == mock_project.owner_id
        assert response.design_project.organization_id == mock_project.organization_id
        assert response.design_project.thumbnail_url == mock_project.thumbnail_url

        mock_collection.find_one.assert_called_once_with({"_id": request.project_id})

    @pytest.mark.asyncio
    async def test_aexecute_when_project_id_not_exists_should_raise_not_found_error(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_collection: Mock,
    ) -> None:
        # Arrange
        mock_collection.configure_mock(find_one=Mock(return_value=None))
        create_design_project = GetDesignProjectById(db=mock_db, logger=mock_logger)

        # Act & Assert
        request = GetDesignProjectById.Request(project_id=generate_uuid())
        with pytest.raises(NotFoundError):
            await create_design_project.aexecute(request)

        mock_collection.find_one.assert_called_once_with({"_id": request.project_id})
