from cli.menu import build_menu_for_employee
from security.session_store import clear_session


def render_menu(employee):
    lines = [
        f"\nConnecté : {employee.full_name} ({employee.role.name})",
        "_" * 40,
    ]

    for item in build_menu_for_employee(employee):
        lines.append(f"{item['key']}. {item['label']}")

    return "\n".join(lines)


def run_main_menu(employee, input_func=input, print_func=print):
    while True:
        print_func(render_menu(employee))
        choice = input_func("Votre choix : ").strip()

        if choice == "0":
            clear_session()
            print_func("Déconnexion réussie.")
            break

        print_func(f"Option choisie : {choice}")
