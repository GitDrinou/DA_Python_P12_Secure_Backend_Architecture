ROLE_ADMIN = "admin"
ROLE_MANAGEMENT = "gestion"
ROLE_SALES = "commercial"
ROLE_SUPPORT = "support"

ROLES = {
    ROLE_ADMIN,
    ROLE_MANAGEMENT,
    ROLE_SALES,
    ROLE_SUPPORT,
}

# Customer permissions
PERM_CUSTOMERS_READ_ALL = "customers.read_all"
PERM_CUSTOMERS_CREATE_OWNED = "customers.create_owned"
PERM_CUSTOMERS_UPDATE_OWNED = "customers.update_owned"
PERM_CUSTOMERS_DELETE_OWNED = "customers.delete_owned"

# Contract permissions
PERM_CONTRACTS_READ_ALL = "contracts.read_all"
PERM_CONTRACTS_CREATE_ALL = "contracts.create_all"
PERM_CONTRACTS_UPDATE_ALL = "contracts.update_all"
PERM_CONTRACTS_UPDATE_OWNED_CUSTOMERS = "contracts.update_owned_customers"
PERM_CONTRACTS_FILTER_UNSIGNED_OR_UNPAID = \
    "contracts.filter_unsigned_or_unpaid"

# Event permissions
PERM_EVENTS_READ_ALL = "events.read_all"
PERM_EVENTS_FILTER_WITHOUT_SUPPORT = "events.filter_without_support"
PERM_EVENTS_ASSIGN_SUPPORT = "events.assign_support"
PERM_EVENTS_CREATE_FOR_SIGNED_CONTRACT_OWNED_CUSTOMERS = \
    "events.create_for_signed_contract_owned_customers"
PERM_EVENTS_FILTER_ASSIGNED_TO_ME = "events.filter_assigned_to_me"
PERM_EVENTS_UPDATE_ASSIGNED = "events.update_assigned"

# Employee permissions
PERM_EMPLOYEES_READ_ALL = "employees.read_all"
PERM_EMPLOYEES_CREATE = "employees.create"
PERM_EMPLOYEES_UPDATE = "employees.update"
PERM_EMPLOYEES_DELETE = "employees.delete"

# Permissions / role-permission management
PERM_PERMISSIONS_READ_ALL = "permissions.read_all"
PERM_PERMISSIONS_CREATE = "permissions.create"
PERM_PERMISSIONS_UPDATE = "permissions.update"
PERM_PERMISSIONS_DELETE = "permissions.delete"
PERM_ROLE_PERMISSIONS_ASSIGN = "role_permissions.assign"
PERM_ROLE_PERMISSIONS_REMOVE = "role_permissions.remove"

COMMON_PERMISSIONS = {
    PERM_CUSTOMERS_READ_ALL: "Lire tous les clients",
    PERM_CONTRACTS_READ_ALL: "Lire tous les contrats",
    PERM_EVENTS_READ_ALL: "Lire tous les événements",
}

MANAGEMENT_PERMISSIONS = {
    PERM_EMPLOYEES_READ_ALL: "Lire tous les collaborateurs",
    PERM_EMPLOYEES_CREATE: "Créer un collaborateur",
    PERM_EMPLOYEES_UPDATE: "Mettre à jour un collaborateur",
    PERM_EMPLOYEES_DELETE: "Supprimer un collaborateur",
    PERM_CONTRACTS_CREATE_ALL: "Créer tous les contrats",
    PERM_CONTRACTS_UPDATE_ALL: "Modifier tous les contrats",
    PERM_EVENTS_FILTER_WITHOUT_SUPPORT: (
        "Filtrer les événements sans contact support"
    ),
    PERM_EVENTS_ASSIGN_SUPPORT: "Assigner un contact support à un événement",
    PERM_PERMISSIONS_READ_ALL: "Lire toutes les permissions",
    PERM_PERMISSIONS_CREATE: "Créer une permission",
    PERM_PERMISSIONS_UPDATE: "Modifier une permission",
    PERM_PERMISSIONS_DELETE: "Supprimer une permission",
    PERM_ROLE_PERMISSIONS_ASSIGN: "Assigner une permission à un rôle",
    PERM_ROLE_PERMISSIONS_REMOVE: "Retirer une permission d'un rôle",
}

SALES_PERMISSIONS = {
    PERM_CUSTOMERS_CREATE_OWNED: (
        "Créer un client rattaché au commercial connecté"
    ),
    PERM_CUSTOMERS_UPDATE_OWNED: "Modifier ses propres clients",
    PERM_CUSTOMERS_DELETE_OWNED: "Supprimer ses propres clients",
    PERM_CONTRACTS_UPDATE_OWNED_CUSTOMERS: (
        "Modifier les contrats dont le commercial est responsable"
    ),
    PERM_CONTRACTS_FILTER_UNSIGNED_OR_UNPAID: (
        "Filtrer les contrats non signés ou non totalement payés"
    ),
    PERM_EVENTS_CREATE_FOR_SIGNED_CONTRACT_OWNED_CUSTOMERS: (
        "Créer un événement pour un contrat signé par un client du commercial"
    ),
}

SUPPORT_PERMISSIONS = {
    PERM_EVENTS_FILTER_ASSIGNED_TO_ME: (
        "Filtrer les événements attribué au support connecté"
    ),
    PERM_EVENTS_UPDATE_ASSIGNED: (
        "Modifier les événements attribués au support connecté"
    ),
}

ALL_PERMISSIONS = {
    **COMMON_PERMISSIONS,
    **MANAGEMENT_PERMISSIONS,
    **SALES_PERMISSIONS,
    **SUPPORT_PERMISSIONS,
}

ROLE_PERMISSION_MAPPER = {
    ROLE_ADMIN: set(ALL_PERMISSIONS),
    ROLE_MANAGEMENT: set(COMMON_PERMISSIONS) | set(MANAGEMENT_PERMISSIONS),
    ROLE_SALES: set(COMMON_PERMISSIONS) | set(SALES_PERMISSIONS),
    ROLE_SUPPORT: set(COMMON_PERMISSIONS) | set(SUPPORT_PERMISSIONS),
}
