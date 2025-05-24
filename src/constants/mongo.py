from dataclasses import dataclass


@dataclass(frozen=True)
class CollectionName:
    STUDENTS: str = "students"
    USERS: str = "users"
    REFRESH_TOKENS: str = "refresh_tokens"
    ORGANIZATIONS: str = "organizations"
    JOIN_ORGANIZATION_INVITATIONS: str = "join_organization_invitations"
    DESIGN_PROJECTS: str = "design_projects"
    BOTS = "bots"
    AI_CONVERSATIONS = "ai_conversations"
