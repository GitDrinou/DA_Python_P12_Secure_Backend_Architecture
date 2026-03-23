def print_success(message):
    print(f"[SUCCESS] {message}")


def print_info(message):
    print(f"[INFO] {message}")


def print_row(data):
    for key, value in data.items():
        print(f"{key}: {value}")
    print("-" * 40)


def print_collection(rows):
    if not rows:
        print("[INFO] No results found")
        return

    for row in rows:
        print_row(row)
