from dataclasses import dataclass

@dataclass
class Permission:
    id: int
    name: str

@dataclass
class RolePermission:
    permission: Permission
    denied: bool = False

@dataclass
class Role:
    id: int
    name: str
    order: int
    permissions: list[RolePermission]

