from typing import Literal

Role = Literal["lead", "subagent", "teammate"]

ALL_MANAGERS = [
    "todo",
    "skills",
    "tasks",
    "background",
    "team",
]

SUBAGENT_MANAGERS = [
    "todo",
    "skills",
    "background",
]

TEAMMATE_MANAGERS = [
    "todo",
    "skills",
    "background",   
]

MANAGERS_BY_ROLE: dict[Role, list[str]] = {
    "lead": ALL_MANAGERS,
    "subagent": SUBAGENT_MANAGERS,
    "teammate": TEAMMATE_MANAGERS,
}

def get_managers(role: Role) -> list[str]:
    return MANAGERS_BY_ROLE.get(role, [])