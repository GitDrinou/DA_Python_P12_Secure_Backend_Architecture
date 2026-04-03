import click
from cli.printers import print_collection, print_row, print_success
from cli.validators import require_permission, run_click_app
from security.permissions import (
    PERM_PERMISSIONS_READ_ALL, PERM_PERMISSIONS_CREATE,
    PERM_PERMISSIONS_UPDATE, PERM_PERMISSIONS_DELETE,
    PERM_ROLE_PERMISSIONS_ASSIGN, PERM_ROLE_PERMISSIONS_REMOVE
)
from services.permission_service import PermissionService
from cli.interactions import prompt_if_missing, confirm_if_requested


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


@click.group(help="Manage permissions and role assignments.")
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


@cli.command("list", help="List all permissions.")
@click.pass_context
def list_permissions(ctx):
    require_permission(ctx, PERM_PERMISSIONS_READ_ALL)
    service = PermissionService(ctx.obj["db_session"])
    permissions = service.list_permissions()
    print_collection(
        [permission_to_dict(permission) for permission in permissions],
        title="Permissions",
    )


@cli.command("get", help="Get a permission.")
@click.option("--code", required=False)
@click.pass_context
def get_permission(ctx, code):
    require_permission(ctx, PERM_PERMISSIONS_READ_ALL)

    code = prompt_if_missing(code, "Code")

    service = PermissionService(ctx.obj["db_session"])
    permission = service.get_permission(code)
    print_row(permission_to_dict(permission), title="Permission")


@cli.command("create", help="Create a permission.")
@click.option("--code", required=False)
@click.option("--description", required=False)
@click.pass_context
def create_permission(ctx, code, description):
    require_permission(ctx, PERM_PERMISSIONS_CREATE)

    code = prompt_if_missing(code, "Code")
    description = prompt_if_missing(description, "Description")

    service = PermissionService(ctx.obj["db_session"])
    permission = service.create_permission(code, description)
    print_success(f"Permission created: {permission.code}")


@cli.command("update", help="Update a permission.")
@click.option("--code", required=False, help="Current code.")
@click.option("--new-code", required=False, help="New permission code.")
@click.option("--description", required=False, help="New description.")
@click.pass_context
def update_permission(ctx, code, new_code, description):
    require_permission(ctx, PERM_PERMISSIONS_UPDATE)

    code = prompt_if_missing(code, "Current code")

    service = PermissionService(ctx.obj["db_session"])
    current = service.get_permission(code)

    new_code = prompt_if_missing(
        new_code,
        "New code",
        default=current.code,
        show_default=True,
    )

    description = prompt_if_missing(
        description,
        "New description",
        default=current.description,
        show_default=True,
    )

    permission = service.update_permission(
        permission_code=code,
        new_code=new_code,
        description=description
    )
    print_success(f"Permission updated: {permission.code}")


@cli.command("delete", help="Delete a permission.")
@click.option("--code", required=False)
@click.option(
    "--yes",
    is_flag=True,
    help="Confirm deletion without interactive prompt.",
)
@click.pass_context
def delete_permission(ctx, code, yes):
    require_permission(ctx, PERM_PERMISSIONS_DELETE)

    code = prompt_if_missing(code, "Code")
    confirm_if_requested(yes, "Do you really want to delete this permission ?")

    service = PermissionService(ctx.obj["db_session"])
    service.delete_permission(code)
    print_success("Permission deleted")


@cli.command("assign", help="Assign a permission to a role.")
@click.option("--role", required=False)
@click.option("--code", required=False)
@click.pass_context
def assign_permission(ctx, role, code):
    require_permission(ctx, PERM_ROLE_PERMISSIONS_ASSIGN)

    role = prompt_if_missing(role, "Role")
    code = prompt_if_missing(code, "Code")

    service = PermissionService(ctx.obj["db_session"])
    updated_role = service.assign_permission_to_role(role, code)
    print_success(
        f"Permission {code} assigned to role {updated_role.name}"
    )


@cli.command("remove", help="Remove a permission from a role.")
@click.option("--role", required=False)
@click.option("--code", required=False)
@click.pass_context
def remove_permission(ctx, role, code):
    require_permission(ctx, PERM_ROLE_PERMISSIONS_REMOVE)

    role = prompt_if_missing(role, "Role")
    code = prompt_if_missing(code, "Code")

    service = PermissionService(ctx.obj["db_session"])
    updated_role = service.remove_permission_from_role(role, code)
    print_success(
        f"Permission {code} removed from role {updated_role.name}"
    )


@cli.command("roles", help="List roles and their permissions.")
@click.pass_context
def list_role(ctx):
    require_permission(ctx, PERM_PERMISSIONS_READ_ALL)
    service = PermissionService(ctx.obj["db_session"])
    roles = service.list_roles()
    print_collection([role_to_dict(role) for role in roles], title="Roles")


def main(db_session=None, args=None):
    return run_click_app(
        cli,
        db_session=db_session,
        args=args,
        prog_name="permissions.py"
    )


permissions_group: click.Group = cli
