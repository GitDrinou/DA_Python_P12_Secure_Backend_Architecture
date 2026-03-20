from security.permissions import (
    PERM_CUSTOMERS_READ_ALL,
    PERM_CUSTOMERS_CREATE_OWNED,
    PERM_CONTRACTS_READ_ALL,
    PERM_CONTRACTS_CREATE_ALL,
    PERM_CONTRACTS_UPDATE_ALL,
    PERM_EVENTS_READ_ALL,
    PERM_EVENTS_CREATE_FOR_SIGNED_CONTRACT_OWNED_CUSTOMERS,
    PERM_EVENTS_UPDATE_ASSIGNED, PERM_EVENTS_ASSIGN_SUPPORT,
    PERM_EMPLOYEES_READ_ALL, PERM_CUSTOMERS_UPDATE_OWNED
)

MENU_ITEMS = [
    {
        "key": "1",
        "label": "Lister les clients",
        "permission": PERM_CUSTOMERS_READ_ALL,
    },
    {
        "key": "2",
        "label": "Créer un client",
        "permission": PERM_CUSTOMERS_CREATE_OWNED,
    },
    {
        "key": "3",
        "label": "Mettre à jour un client",
        "permission": PERM_CUSTOMERS_UPDATE_OWNED,
    },
    {
        "key": "4",
        "label": "Lister les contrats",
        "permission": PERM_CONTRACTS_READ_ALL,
    },
    {
        "key": "5",
        "label": "Créer un contrat",
        "permission": PERM_CONTRACTS_CREATE_ALL,
    },
    {
        "key": "6",
        "label": "Mettre à jour un contrat",
        "permission": PERM_CONTRACTS_UPDATE_ALL,
    },
    {
        "key": "7",
        "label": "Lister les événements",
        "permission": PERM_EVENTS_READ_ALL,
    },
    {
        "key": "8",
        "label": "Créer un événement",
        "permission": PERM_EVENTS_CREATE_FOR_SIGNED_CONTRACT_OWNED_CUSTOMERS,
    },
    {
        "key": "9",
        "label": "Mettre à jour mes événements",
        "permission": PERM_EVENTS_UPDATE_ASSIGNED,
    },
    {
        "key": "10",
        "label": "Assigner un support à un événement",
        "permission": PERM_EVENTS_ASSIGN_SUPPORT,
    },
    {
        "key": "11",
        "label": "Gérer les collaborateurs",
        "permission": PERM_EMPLOYEES_READ_ALL,
    },
]

LOGOUT_MENU_ITEM = {
    "key": "0",
    "label": "Se déconnecter",
    "permission": None,
}
