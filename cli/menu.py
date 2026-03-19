from security import has_permission

MENU_ITEMS = [
    {
        "key": "1",
        "label": "Lister les clients",
        "permission": "customers.read_all",
    },
    {
        "key": "2",
        "label": "Créer un client",
        "permission": "customers.create_owned",
    },
    {
        "key": "3",
        "label": "Mettre à jour un client",
        "permission": "customers.update_owned",
    },
    {
        "key": "4",
        "label": "Lister les contrats",
        "permission": "contracts.read_all",
    },
    {
        "key": "5",
        "label": "Créer un contrat",
        "permission": "contracts.create_all",
    },
    {
        "key": "6",
        "label": "Mettre à jour un contrat",
        "permission": "contracts.update_all",
    },
    {
        "key": "7",
        "label": "Lister les événements",
        "permission": "events.read_all",
    },
    {
        "key": "8",
        "label": "Créer un événement",
        "permission": "events.create_for_signed_contract_owned_customers",
    },
    {
        "key": "9",
        "label": "Mettre à jour mes événements",
        "permission": "events.update_assigned",
    },
    {
        "key": "10",
        "label": "Assigner un support à un événement",
        "permission": "events.assign_support",
    },
    {
        "key": "11",
        "label": "Gérer les collaborateurs",
        "permission": "employees.read_all",
    }
]

def build_menu_for_employee(employee):
    visible_items = []

    for item in MENU_ITEMS:
        if has_permission(employee, item['permission']):
            visible_items.append(item)

    visible_items.append({
        "key": "0",
        "label": "Se déconnecter",
        "permission": None,
    })

    return visible_items