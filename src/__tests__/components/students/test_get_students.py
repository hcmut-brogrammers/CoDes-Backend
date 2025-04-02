from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from pydantic import BaseModel, ConfigDict

from ....common.models import StudentModel
from ....components.students.get_students import GetStudents
from ....constants.mongo import CollectionName


class MockSetup(BaseModel):
    db: MagicMock
    logger: MagicMock
    collection: AsyncMock

    model_config = ConfigDict(arbitrary_types_allowed=True)


class TestGetStudents:
    def setup_mocks(self) -> MockSetup:
        mock_db = MagicMock()
        mock_logger = MagicMock()
        mock_collection = AsyncMock()
        mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
        return MockSetup(db=mock_db, logger=mock_logger, collection=mock_collection)

    def verify_interactions(self, mock_logger, mock_db, mock_collection) -> None:
        mock_logger.info.assert_called_once_with("Fetching all students from the database.")
        mock_db.get_collection.assert_called_once_with(CollectionName.STUDENTS)
        mock_collection.find.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_aexecute(self) -> None:
        # Setup mocks
        mocks = self.setup_mocks()

        # Mock database response
        students = [
            StudentModel(
                _id="1",
                name="John Doe",
                email="johndoe@gmail.com",
                course="Math",
                gpa=3.5,
            ),
            StudentModel(
                _id="2",
                name="David",
                email="david@gmail.com",
                course="Science",
                gpa=3.8,
            ),
        ]
        mock_students_data = [student.model_dump() for student in students]
        mocks.collection.configure_mock(find=Mock(return_value=mock_students_data))

        # Initialize the component
        get_students = GetStudents(db=mocks.db, logger=mocks.logger)

        # Execute the component
        response = await get_students.aexecute()

        # Assertions
        assert len(response.students) == len(mock_students_data)
        for student, mock_data in zip(response.students, mock_students_data):
            assert isinstance(student, StudentModel)
            assert student.id == mock_data["id"]
            assert student.name == mock_data["name"]
            assert student.email == mock_data["email"]
            assert student.course == mock_data["course"]
            assert student.gpa == mock_data["gpa"]

        # Verify interactions
        self.verify_interactions(mocks.logger, mocks.db, mocks.collection)

    @pytest.mark.asyncio
    async def test_aexecute_no_students(self) -> None:
        # Setup mocks
        mocks = self.setup_mocks()

        # Mock database response with no students
        mocks.collection.configure_mock(find=Mock(return_value=[]))

        # Initialize the component
        get_students = GetStudents(db=mocks.db, logger=mocks.logger)

        # Execute the component
        response = await get_students.aexecute()

        # Assertions
        assert len(response.students) == 0

        # Verify interactions
        self.verify_interactions(mocks.logger, mocks.db, mocks.collection)
