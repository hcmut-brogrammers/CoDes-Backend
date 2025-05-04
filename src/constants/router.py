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
    SWITCH_ORGANIZATION = "/switch-organization"

    USERS = "/users"
    ORGANIZATIONS = "/organizations"
    TESTS = "/tests"
    JOIN_WORKSPACE_INVITATIONS = "/join-workspace-invitations"
    DESIGN_PROJECTS = "/design-projects"
    WEBSOCKET = "/ws"

    NODES = "/nodes"
    SHAPES = "/shapes"
