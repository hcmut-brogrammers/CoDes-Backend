import typing as t
from abc import ABC, abstractmethod

TRequest = t.TypeVar("TRequest")
TResponse = t.TypeVar("TResponse")


class IBaseComponent(ABC, t.Generic[TRequest, TResponse]):
    @abstractmethod
    async def aexecute(self, request: TRequest) -> TResponse:
        pass


class IBaseComponentWithoutRequest(ABC, t.Generic[TResponse]):
    @abstractmethod
    async def aexecute(self) -> TResponse:
        pass
