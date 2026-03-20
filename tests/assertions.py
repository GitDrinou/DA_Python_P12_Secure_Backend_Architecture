def menu_labels(menu):
    return {item["label"] for item in menu}


def menu_keys(menu):
    return {item["key"] for item in menu}


def assert_contains_labels(menu, *expected_labels):
    labels = menu_labels(menu)
    missing = [label for label in expected_labels if label not in labels]
    assert not missing, f"Missing labels in menu: {missing}"


def assert_not_contains_labels(menu, *unexpected_labels):
    labels = menu_labels(menu)
    present = [label for label in unexpected_labels if label in labels]
    assert not present, f"Unexpected labels found in menu: {present}"
