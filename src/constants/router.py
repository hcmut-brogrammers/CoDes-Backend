from dataclasses import dataclass


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
    JOIN_ORGANIZATION_INVITATIONS = "/join-organization-invitations"
    DESIGN_PROJECTS = "/design-projects"
    WEBSOCKET = "/ws"

    ELEMENTS = "/elements"
    BOTS = "/bots"
    AI_CONVERSATIONS = "/ai-conversations"
