from logging import Logger
from unittest.mock import Mock

import pytest
from pymongo.collection import Collection
from pymongo.database import Database

from ..common.auth import UserContext
from ..components.organizations import GetOrganizationById
from ..components.users import GetUserById


@pytest.fixture
def mock_get_organization_by_id() -> Mock:
    return Mock(spec=GetOrganizationById)


@pytest.fixture
def mock_get_user_by_id() -> Mock:
    return Mock(spec=GetUserById)


@pytest.fixture
def mock_db() -> Mock:
    return Mock(spec=Database)


@pytest.fixture
def mock_collection() -> Mock:
    return Mock(spec=Collection)


@pytest.fixture
def mock_logger() -> Mock:
    return Mock(spec=Logger)


@pytest.fixture
def mock_user_context() -> Mock:
    return Mock(spec=UserContext)
