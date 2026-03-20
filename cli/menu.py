from cli.menu_config import MENU_ITEMS, LOGOUT_MENU_ITEM
from security import has_permission


def build_menu_for_employee(employee):
    visible_items = []

    for item in MENU_ITEMS:
        if has_permission(employee, item['permission']):
            visible_items.append(item)

    visible_items.append(LOGOUT_MENU_ITEM.copy())

    return visible_items
