import logging
import os
import re
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.scrubber import EventScrubber


APP_LOGGER_NAME = "epic_events"
AUDIT_LOGGER_NAME = "epic_events.audit"
_OBSERVABILITY_INITIALIZED = False
SENSITIVE_KEYS = {
    "password",
    "plain_password",
    "password_hash",
    "access_token",
    "refresh_token",
    "authorization",
    "cookie",
    "set-cookie",
    "token",
    "jwt",
    "secret",
    "api_key",
}
JWT_LIKE_RE = re.compile(
    r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+"
)


class AuditLoggerAdapter(logging.LoggerAdapter):
    """Inject a marker so audit logs can be filtered separately if needed."""

    def process(self, msg, kwargs):
        extra = dict(kwargs.pop("extra", {}) or {})
        extra["is_audit"] = True
        kwargs["extra"] = extra
        return msg, kwargs


class ExcludeAuditLogsFilter(logging.Filter):
    """Prevent audit logs from being duplicated on the app console handler."""

    def filter(self, record: logging.LogRecord) -> bool:
        return not bool(getattr(record, "is_audit", False))


def _mask_value(value):
    if value is None:
        return None

    if isinstance(value, str):
        if JWT_LIKE_RE.search(value):
            return "[REDACTED]"
        return value

    if isinstance(value, dict):
        return {
            key: ("[REDACTED]"
                  if str(key).lower() in SENSITIVE_KEYS else _mask_value(val))
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [_mask_value(item) for item in value]

    if isinstance(value, tuple):
        return tuple(_mask_value(item) for item in value)

    return value


def _scrub_event_data(obj):
    if isinstance(obj, dict):
        cleaned = {}
        for key, value in obj.items():
            lowered = str(key).lower()
            if lowered in SENSITIVE_KEYS:
                cleaned[key] = "[REDACTED]"
            else:
                cleaned[key] = _scrub_event_data(value)
        return cleaned

    if isinstance(obj, list):
        return [_scrub_event_data(item) for item in obj]

    if isinstance(obj, tuple):
        return tuple(_scrub_event_data(item) for item in obj)

    if isinstance(obj, str):
        if JWT_LIKE_RE.search(obj):
            return "[REDACTED]"
        return obj

    return obj


def _before_send(event, hint):
    return _scrub_event_data(event)


def _before_send_log(log, hint):
    attrs = getattr(log, "attributes", None)
    if isinstance(attrs, dict):
        log.attributes = _scrub_event_data(attrs)

    body = getattr(log, "body", None)
    if isinstance(body, str) and JWT_LIKE_RE.search(body):
        log.body = "[REDACTED]"

    return log


def init_observability() -> None:
    global _OBSERVABILITY_INITIALIZED

    if _OBSERVABILITY_INITIALIZED:
        return

    _configure_app_logging()

    dsn = os.getenv("SENTRY_DSN")
    if dsn:
        sentry_logging = LoggingIntegration(
            sentry_logs_level=logging.INFO,
            level=logging.INFO,
            event_level=logging.ERROR,
        )

        sentry_sdk.init(
            dsn=dsn,
            environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
            release=os.getenv("SENTRY_RELEASE"),
            integrations=[sentry_logging],
            enable_logs=True,
            send_default_pii=False,
            include_local_variables=False,
            traces_sample_rate=1.0,
            event_scrubber=EventScrubber(
                denylist=[
                    "password",
                    "plain_password",
                    "password_hash",
                    "access_token",
                    "refresh_token",
                    "authorization",
                    "cookie",
                    "set-cookie",
                    "token",
                    "jwt",
                    "secret",
                    "api_key",
                ]
            ),
            before_send=_before_send,
            before_send_log=_before_send_log,
        )

    _configure_audit_logger()

    _OBSERVABILITY_INITIALIZED = True


def flush_observability(timeout: float = 2.0) -> None:
    if sentry_sdk.is_initialized():
        sentry_sdk.flush(timeout=timeout)


def get_application_logger() -> logging.Logger:
    return logging.getLogger(APP_LOGGER_NAME)


def get_audit_logger() -> AuditLoggerAdapter:
    return AuditLoggerAdapter(logging.getLogger(AUDIT_LOGGER_NAME), extra={})


def _configure_app_logging() -> None:
    logger = get_application_logger()
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.addFilter(ExcludeAuditLogsFilter())
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )
        )
        logger.addHandler(handler)


def _configure_audit_logger() -> None:
    logger = logging.getLogger(AUDIT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = True


def _build_actor_extra(actor) -> dict:
    if actor is None:
        return {}

    return {
        "actor_employee_id": getattr(actor, "employee_id", None),
        "actor_role": getattr(getattr(actor, "role", None), "name", None),
    }


def log_employee_created(actor, employee) -> None:
    audit_logger = get_audit_logger()
    audit_logger.info(
        "employee_created",
        extra={
            **_build_actor_extra(actor),
            "event_kind": "audit",
            "event_category": "employee",
            "event_action": "created",
            "entity_id": str(employee.employee_id),
            "employee_id": employee.employee_id,
            "employee_full_name": employee.full_name,
            "employee_role": employee.role.name if employee.role else None,
            "employee_is_active": employee.is_active,
        },
    )


def log_employee_updated(actor, employee) -> None:
    audit_logger = get_audit_logger()
    audit_logger.info(
        "employee_updated",
        extra={
            **_build_actor_extra(actor),
            "event_kind": "audit",
            "event_category": "employee",
            "event_action": "updated",
            "entity_id": str(employee.employee_id),
            "employee_id": employee.employee_id,
            "employee_full_name": employee.full_name,
            "employee_role": employee.role.name if employee.role else None,
            "employee_is_active": employee.is_active,
        },
    )


def log_contract_signed(actor, contract) -> None:
    customer = getattr(contract, "customer", None)

    audit_logger = get_audit_logger()
    audit_logger.info(
        "contract_signed",
        extra={
            **_build_actor_extra(actor),
            "event_kind": "audit",
            "event_category": "contract",
            "event_action": "signed",
            "entity_id": str(contract.contract_id),
            "contract_id": contract.contract_id,
            "contract_total_amount": str(contract.total_amount),
            "contract_remaining_amount": str(contract.remaining_amount),
            "customer_id": getattr(customer, "customer_id", None),
            "customer_name": getattr(customer, "full_name", None),
        },
    )
