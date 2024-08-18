import json
import logging
import os

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


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
    """
    if not os.getenv("SENTRY_DSN"):
        logger.info("No Sentry DSN found. Skipping Sentry setup.")
        return

    # BUILD_INFO is generated by the build pipeline (e.g. docker/metadata-action).
    # Example:
    # {
    #     "tags": ["ghcr.io/watonomous/repo-ingestion:main"],
    #     "labels": {
    #         "org.opencontainers.image.title": "repo-ingestion",
    #         "org.opencontainers.image.description": "Simple server to receive file changes and open GitHub pull requests",
    #         "org.opencontainers.image.url": "https://github.com/WATonomous/repo-ingestion",
    #         "org.opencontainers.image.source": "https://github.com/WATonomous/repo-ingestion",
    #         "org.opencontainers.image.version": "main",
    #         "org.opencontainers.image.created": "2024-01-20T16:10:39.421Z",
    #         "org.opencontainers.image.revision": "1d55b62b15c78251e0560af9e97927591e260a98",
    #         "org.opencontainers.image.licenses": "",
    #     },
    # }
    try:
        BUILD_INFO = json.loads(os.getenv("DOCKER_METADATA_OUTPUT_JSON", "{}"))
    except json.JSONDecodeError:
        logger.warning("Failed to parse DOCKER_METADATA_OUTPUT_JSON. Not using build info.")
        BUILD_INFO = {}

    build_labels = BUILD_INFO.get("labels", {})
    image_title = build_labels.get("org.opencontainers.image.title", "unknown_image")
    image_version = build_labels.get("org.opencontainers.image.version", "unknown_version")
    image_rev = build_labels.get("org.opencontainers.image.revision", "unknown_rev")

    sentry_config = {
        "dsn": os.environ["SENTRY_DSN"],
        "environment": os.getenv("DEPLOYMENT_ENVIRONMENT", "unknown"),
        "release": os.getenv(
            "SENTRY_RELEASE", f"{image_title}:{image_version}@{image_rev}"
        ),
    }

    logger.info(f"Sentry DSN found. Setting up Sentry with config: {sentry_config}")
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
