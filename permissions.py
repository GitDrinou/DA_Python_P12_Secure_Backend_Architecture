import argparse
from cli.printers import print_collection, print_row, print_success
from cli.verificators import permission_required, handle_cli_errors
from database.session import SessionLocal
from security.permissions import (
    PERM_PERMISSIONS_READ_ALL,
    PERM_PERMISSIONS_CREATE,
    PERM_PERMISSIONS_UPDATE,
    PERM_PERMISSIONS_DELETE,
    PERM_ROLE_PERMISSIONS_ASSIGN,
    PERM_ROLE_PERMISSIONS_REMOVE,
)
from services.permission_service import PermissionService


def build_parser():
    parser = argparse.ArgumentParser(prog="permissions.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List all permissions")

    get_parser = subparsers.add_parser("get", help="Get one permission")
    get_parser.add_argument("--code", required=True)

    create_parser = subparsers.add_parser("create", help="Create a permission")
    create_parser.add_argument("--code", required=True)
    create_parser.add_argument("--description", required=True)

    update_parser = subparsers.add_parser("update", help="Update a permission")
    update_parser.add_argument("--code", required=True)
    update_parser.add_argument("--new-code")
    update_parser.add_argument("--description")

    delete_parser = subparsers.add_parser("delete", help="Delete a permission")
    delete_parser.add_argument("--code", required=True)

    assign_parser = subparsers.add_parser(
        "assign",
        help="Assign a permission to a role",
    )
    assign_parser.add_argument("--role", required=True)
    assign_parser.add_argument("--code", required=True)

    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove a permission from a role",
    )
    remove_parser.add_argument("--role", required=True)
    remove_parser.add_argument("--code", required=True)

    subparsers.add_parser("roles", help="List roles and their permissions")

    return parser


def permission_to_dict(permission):
    return {
        "code": permission.code,
        "description": permission.description,
    }


def role_to_dict(role):
    return {
        "role": role.name,
        "permissions": ", ".join(
            sorted(permission.code for permission in role.permissions)
        ),
    }


@permission_required(PERM_PERMISSIONS_READ_ALL)
def handle_list(current_employee=None, db_session=None):
    service = PermissionService(db_session)
    permissions = service.list_permissions()
    print_collection([permission_to_dict(item) for item in permissions])
    return 0


@permission_required(PERM_PERMISSIONS_READ_ALL)
def handle_get(code, current_employee=None, db_session=None):
    service = PermissionService(db_session)
    permission = service.get_permission(code)
    print_row(permission_to_dict(permission))
    return 0


@permission_required(PERM_PERMISSIONS_CREATE)
def handle_create(args, current_employee=None, db_session=None):
    service = PermissionService(db_session)
    permission = service.create_permission(args.code, args.description)
    print_success(f"Permission created: {permission.code}")
    return 0


@permission_required(PERM_PERMISSIONS_UPDATE)
def handle_update(args, current_employee=None, db_session=None):
    service = PermissionService(db_session)
    permission = service.update_permission(
        permission_code=args.code,
        new_code=args.new_code,
        description=args.description,
    )
    print_success(f"Permission updated: {permission.code}")
    return 0


@permission_required(PERM_PERMISSIONS_DELETE)
def handle_delete(code, current_employee=None, db_session=None):
    service = PermissionService(db_session)
    service.delete_permission(code)
    print_success("Permission deleted")
    return 0


@permission_required(PERM_ROLE_PERMISSIONS_ASSIGN)
def handle_assign(args, current_employee=None, db_session=None):
    service = PermissionService(db_session)
    role = service.assign_permission_to_role(args.role, args.code)
    print_success(f"Permission {args.code} assigned to role {role.name}")
    return 0


@permission_required(PERM_ROLE_PERMISSIONS_REMOVE)
def handle_remove(args, current_employee=None, db_session=None):
    service = PermissionService(db_session)
    role = service.remove_permission_from_role(args.role, args.code)
    print_success(f"Permission {args.code} removed from role {role.name}")
    return 0


@permission_required(PERM_PERMISSIONS_READ_ALL)
def handle_roles(current_employee=None, db_session=None):
    service = PermissionService(db_session)
    roles = service.list_roles()
    print_collection([role_to_dict(role) for role in roles])
    return 0


@handle_cli_errors
def main(db_session=None):
    parser = build_parser()
    args = parser.parse_args()

    created_session = False
    if db_session is None:
        db_session = SessionLocal()
        created_session = True

    try:
        if args.command == "list":
            return handle_list(db_session=db_session)

        if args.command == "get":
            return handle_get(args.code, db_session=db_session)

        if args.command == "create":
            return handle_create(args, db_session=db_session)

        if args.command == "update":
            return handle_update(args, db_session=db_session)

        if args.command == "delete":
            return handle_delete(args.code, db_session=db_session)

        if args.command == "assign":
            return handle_assign(args, db_session=db_session)

        if args.command == "remove":
            return handle_remove(args, db_session=db_session)

        if args.command == "roles":
            return handle_roles(db_session=db_session)

        return 1
    finally:
        if created_session:
            db_session.close()


if __name__ == "__main__":
    raise SystemExit(main())
