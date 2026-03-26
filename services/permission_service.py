from sqlalchemy.orm import joinedload
from database.models import Permission, Role


class PermissionService:
    def __init__(self, db_session):
        self.db_session = db_session

    def list_permissions(self):
        return (
            self.db_session.query(Permission)
            .order_by(Permission.code.asc())
            .all()
        )

    def get_permission(self, permission_code):
        permission = (
            self.db_session.query(Permission)
            .filter(Permission.code == permission_code)
            .first()
        )

        if permission is None:
            raise ValueError("Permission not found")

        return permission

    def create_permission(self, code, description):
        if not code:
            raise ValueError("Permission code is required")

        if not description:
            raise ValueError("Permission description is required")

        existing = (
            self.db_session.query(Permission)
            .filter(Permission.code == code)
            .first()
        )
        if existing is not None:
            raise ValueError("Permission already exists")

        permission = Permission(
            code=code,
            description=description,
        )

        self.db_session.add(permission)
        self.db_session.commit()
        self.db_session.refresh(permission)

        return permission

    def update_permission(
            self,
            permission_code,
            new_code=None,
            description=None
    ):
        permission = self.get_permission(permission_code)

        if new_code is None and description is None:
            raise ValueError("Nothing to update")

        if new_code is not None:
            if not new_code:
                raise ValueError("Permission code is required")

            if new_code != permission.code:
                existing = (
                    self.db_session.query(Permission)
                    .filter(Permission.code == new_code)
                    .first()
                )
                if existing is not None:
                    raise ValueError("Permission already exists")

                permission.code = new_code

        if description is not None:
            if not description:
                raise ValueError("Permission description is required")

            permission.description = description

        self.db_session.commit()
        self.db_session.refresh(permission)

        return permission

    def delete_permission(self, permission_code):
        permission = self.get_permission(permission_code)

        self.db_session.delete(permission)
        self.db_session.commit()

        return True

    def list_roles(self):
        return (
            self.db_session.query(Role)
            .options(joinedload(Role.permissions))
            .order_by(Role.name.asc())
            .all()
        )

    def get_role(self, role_name):
        role = (
            self.db_session.query(Role)
            .options(joinedload(Role.permissions))
            .filter(Role.name == role_name)
            .first()
        )

        if role is None:
            raise ValueError("Role not found")

        return role

    def assign_permission_to_role(self, role_name, permission_code):
        role = self.get_role(role_name)
        permission = self.get_permission(permission_code)

        if any(item.permission_id == permission.permission_id for item in
               role.permissions):
            return role

        role.permissions.append(permission)
        self.db_session.commit()
        self.db_session.refresh(role)

        return self.get_role(role_name)

    def remove_permission_from_role(self, role_name, permission_code):
        role = self.get_role(role_name)
        permission = self.get_permission(permission_code)

        if any(item.permission_id == permission.permission_id for item in
               role.permissions):
            role.permissions = [
                item
                for item in role.permissions
                if item.permission_id != permission.permission_id
            ]
            self.db_session.commit()
            self.db_session.refresh(role)

        return self.get_role(role_name)
