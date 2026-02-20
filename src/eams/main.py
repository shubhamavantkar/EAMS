from __future__ import annotations

import logging

from eams.config import settings
from eams.service_runner.supervisor import ServiceSupervisor
from eams.utils.logging_setup import configure_logging

LOGGER = logging.getLogger("eams.main")


def main() -> None:
    configure_logging("INFO")
    LOGGER.info("Starting EAMS in %s mode", settings.mode)
    supervisor = ServiceSupervisor(settings)
    if settings.mode == "development":
        LOGGER.info("Development mode: report scheduler active, console logging enabled")
    supervisor.start()


if __name__ == "__main__":
    main()
