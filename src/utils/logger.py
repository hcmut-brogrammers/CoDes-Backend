import inspect
from typing import Protocol


class ServiceInstance(Protocol):
    __class__: type  # Ensures the object has a class attribute


def execute_service_method(instance: ServiceInstance, request: dict | None = None) -> str:
    class_name = instance.__class__.__name__
    if not class_name:
        raise ValueError("Unable to retrieve the class name.")

    current_frame = inspect.currentframe()
    if not current_frame:
        raise ValueError("Unable to retrieve the current frame.")

    previous_frame = current_frame.f_back
    if not previous_frame:
        raise ValueError("Unable to retrieve the previous frame.")

    method_name = previous_frame.f_code.co_name
    message = f"Executing service method {class_name}.{method_name}"
    if not request:
        return message

    message = f"{message} with request: {request}"
    return message
