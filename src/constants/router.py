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
    SWITCH_ORGANIZATION = "/switch_organization"

    USERS = "/users"
    ORGANIZATIONS = "/organizations"
    TESTS = "/tests"
    JOIN_WORKSPACE_INVITATIONS = "/join-workspace-invitations"
    PROJECTS = "/projects"
