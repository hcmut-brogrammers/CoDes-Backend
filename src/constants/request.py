from dataclasses import dataclass


@dataclass(frozen=True)
class RequestMethod:
    """
    Enum for HTTP request methods.
    """

    GET: str = "GET"
    POST: str = "POST"
    PUT: str = "PUT"
    DELETE: str = "DELETE"
    PATCH: str = "PATCH"
    OPTIONS: str = "OPTIONS"
    HEAD: str = "HEAD"


@dataclass(frozen=True)
class HeaderKey:
    AUTHORIZATION: str = "Authorization"
