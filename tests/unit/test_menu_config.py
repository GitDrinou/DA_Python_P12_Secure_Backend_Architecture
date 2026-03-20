from cli.menu_config import LOGOUT_MENU_ITEM, MENU_ITEMS


def test_menu_keys_are_unique():
    keys = [item["key"] for item in MENU_ITEMS]
    assert len(keys) == len(set(keys))


def test_menu_permissions_are_defined_for_all_action_items():
    for item in MENU_ITEMS:
        assert item["permission"] is not None
        assert isinstance(item["permission"], str)
        assert item["permission"] != ""


def test_logout_menu_item_is_stable():
    assert LOGOUT_MENU_ITEM == {
        "key": "0",
        "label": "Se déconnecter",
        "permission": None,
    }
