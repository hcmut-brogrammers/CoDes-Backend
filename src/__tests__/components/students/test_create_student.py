from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4  # Import uuid4 to generate valid UUIDs

import pytest
from pydantic import BaseModel, ConfigDict

from ....common.models import StudentModel
from ....components.students.create_student import CreateStudent
from ....constants.mongo import CollectionName


class MockSetup(BaseModel):
    db: MagicMock
    logger: MagicMock
    collection: AsyncMock

    model_config = ConfigDict(arbitrary_types_allowed=True)


@pytest.fixture
def mock_setup() -> MockSetup:
    mock_db = MagicMock()
    mock_logger = MagicMock()
    mock_collection = AsyncMock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return MockSetup(db=mock_db, logger=mock_logger, collection=mock_collection)


class TestCreateStudent:
    def verify_interactions(self, mock_logger, mock_db, mock_collection, student_data) -> None:
        mock_logger.info.assert_called_once_with("Creating a new student in the database.")
        mock_db.get_collection.assert_called_once_with(CollectionName.STUDENTS)
        mock_collection.insert_one.assert_called_once_with(student_data)
        mock_collection.find_one.assert_called_once_with({"_id": mock_collection.insert_one.return_value.inserted_id})

    @pytest.mark.asyncio
    async def test_aexecute(self, mock_setup: MockSetup) -> None:
        # Setup mocks
        mocks = mock_setup

        # Mock request and database response
        student = StudentModel(name="John Doe", email="johndoe@gmail.com", course="Math", gpa=3.5)
        mock_request = student
        mock_inserted_id = uuid4()  # Use uuid4 to generate a valid UUID object
        mocks.collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=mock_inserted_id)),
            find_one=Mock(return_value={**student.model_dump(), "_id": mock_inserted_id}),
        )

        # Initialize the component
        create_student = CreateStudent(db=mocks.db, logger=mocks.logger)

        # Execute the component
        request = CreateStudent.Request(**student.model_dump())
        response = await create_student.aexecute(request)

        # Assertions
        assert response.student is not None
        assert response.student.id == mock_inserted_id
        assert response.student.name == student.name
        assert response.student.email == student.email
        assert response.student.course == student.course
        assert response.student.gpa == student.gpa

        # Verify interactions
        self.verify_interactions(
            mocks.logger,
            mocks.db,
            mocks.collection,
            mock_request.model_dump(by_alias=True, exclude={"id"}),
        )

    @pytest.mark.asyncio
    async def test_aexecute_student_not_created(self, mock_setup: MockSetup) -> None:
        # Setup mocks
        mocks = mock_setup

        # Mock request and database response
        student = StudentModel(name="Jane Doe", email="janedoe@gmail.com", course="Science", gpa=3.8)
        mock_request = student
        mocks.collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=None)),
            find_one=Mock(return_value=None),
        )

        # Initialize the component
        create_student = CreateStudent(db=mocks.db, logger=mocks.logger)

        # Execute the component
        request = CreateStudent.Request(**student.model_dump())
        response = await create_student.aexecute(request)

        # Assertions
        assert response.student is None

        # Verify interactions
        self.verify_interactions(
            mocks.logger,
            mocks.db,
            mocks.collection,
            mock_request.model_dump(by_alias=True, exclude={"id"}),
        )
