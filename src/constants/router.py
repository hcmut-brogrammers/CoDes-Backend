from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class ApiPath:
    """
    Enum for URL segments.
    """

    AUTHENTICATE = "/authenticate"
    SIGN_UP = "/sign-up"
    AUTHENTICATE_USER = "/authenticate-user"
    REFRESH_ACCESS_TOKEN = "/refresh-access-token"

    USERS = "/users"
    ORGANIZATIONS = "/organizations"
    TESTS = "/tests"
    PRODUCTS = "/products"
