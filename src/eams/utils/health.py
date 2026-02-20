from eams.models.results import HealthStatus


def healthy(module: str, details: str = "ok") -> HealthStatus:
    return HealthStatus(module=module, is_healthy=True, details=details)
