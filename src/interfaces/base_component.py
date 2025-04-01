import typing as t
from abc import ABC, abstractmethod

TRequest = t.TypeVar("TRequest")
TResponse = t.TypeVar("TResponse")


class IBaseComponent(ABC, t.Generic[TRequest, TResponse]):
    @t.overload
    @abstractmethod
    async def aexecute(self, request: TRequest) -> TResponse:
        pass

    @t.overload
    @abstractmethod
    async def aexecute(self) -> TResponse:
        pass

    async def aexecute(self, request: TRequest | None = None) -> TResponse:
        """
        Executes the component asynchronously.

        :param request: Optional request parameter of type TRequest.
        :return: Response of type TResponse.
        """
        raise NotImplementedError("This method should be overridden in subclasses.")
