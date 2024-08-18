import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from .env import Vars, getvar


def set_up_sentry(
    trace_sample_rate=1.0,
    breadcrumb_level=logging.INFO,
    event_level=logging.ERROR,
    logger=logging.getLogger(__name__),
):
    """
    Set up Sentry SDK with the given configuration.

    Parameters:
    - trace_sample_rate: float, optional. The rate at which traces should be sampled.
        Default is 1.0 (sample all traces).
    - breadcrumb_level: int, optional. The level at which breadcrumbs should be captured.
        Default is logging.INFO.
    - event_level: int, optional. The level at which events should be captured.
        Default is logging.ERROR.

    Returns: bool. True if Sentry was set up successfully, False otherwise.
    """
    SENTRY_DSN = getvar(Vars.SENTRY_DSN, logger=logger)
    if not SENTRY_DSN:
        logger.warning("SENTRY_DSN not found. Skipping Sentry setup.")
        return False

    BUILD_INFO = getvar(Vars.BUILD_INFO, logger=logger) or {}
    DEPLOYMENT_ENVIRONMENT = (
        getvar(Vars.DEPLOYMENT_ENVIRONMENT, logger=logger) or "unknown"
    )

    build_labels = BUILD_INFO.get("labels", {})
    image_title = build_labels.get("org.opencontainers.image.title", "unknown_image")
    image_version = build_labels.get(
        "org.opencontainers.image.version", "unknown_version"
    )
    image_rev = build_labels.get("org.opencontainers.image.revision", "unknown_rev")

    SENTRY_RELEASE = (
        getvar(Var.SENTRY_RELEASE, logger=logger)
        or f"{image_title}:{image_version}@{image_rev}"
    )

    sentry_config = {
        "dsn": SENTRY_DSN,
        "environment": DEPLOYMENT_ENVIRONMENT,
        "release": SENTRY_RELEASE,
    }

    logger.info(f"Setting up Sentry with config: {sentry_config}")
    logger.info(f"Sentry SDK version: {sentry_sdk.VERSION}")

    sentry_logging = LoggingIntegration(
        level=breadcrumb_level,
        event_level=event_level,
    )

    def sentry_traces_sampler(sampling_context):
        # Inherit parent sampling decision
        if sampling_context.get("parent_sampled") is not None:
            return sampling_context["parent_sampled"]

        # Don't need to sample health checks
        if sampling_context.get("asgi_scope", {}).get("path", "").startswith("/health"):
            return 0

        # Sample everything else
        return trace_sample_rate

    sentry_sdk.init(
        **sentry_config,
        integrations=[sentry_logging],
        traces_sampler=sentry_traces_sampler,
        enable_tracing=True,
    )

    return True
