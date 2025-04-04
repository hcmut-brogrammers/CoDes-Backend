import pytest

from ...utils.logger import execute_service_method


class MockService:
    def __init__(self) -> None:
        self.__class__.__name__ = "MockService"


class TestExecuteServiceMethod:
    def test_execute_service_method_without_request(self) -> None:
        # Create a real service instance
        service_instance = MockService()

        # Define a dummy method to simulate the caller
        def dummy_method() -> str:
            return execute_service_method(service_instance)

        # Call the dummy method and assert the result
        result = dummy_method()
        assert result == "Executing service method MockService.dummy_method"

    def test_execute_service_method_with_request(self) -> None:
        # Create a real service instance
        service_instance = MockService()

        # Define a dummy method to simulate the caller
        def dummy_method() -> str:
            return execute_service_method(service_instance, {"key": "value"})

        # Call the dummy method and assert the result
        result = dummy_method()
        assert result == "Executing service method MockService.dummy_method with request: {'key': 'value'}"

    def test_execute_service_method_missing_class_name(self) -> None:
        # Create a service instance with no class name
        class ServiceWithoutName:
            def __init__(self) -> None:
                self.__class__.__name__ = ""

        service_instance = ServiceWithoutName()

        with pytest.raises(ValueError, match="Unable to retrieve the class name."):
            execute_service_method(service_instance)
