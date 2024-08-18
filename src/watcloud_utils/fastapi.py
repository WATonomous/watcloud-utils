import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .env import Vars, getvar
from .sentry import sentry_sdk, set_up_sentry


class WATcloudFastAPI(FastAPI):
    def __init__(
        self,
        *args,
        cors_allow_origins=None,
        logger=logging.getLogger(__name__),
        expose_metrics=True,
        expose_build_info=True,
        expose_health=True,
        health_fns=[],
        expose_runtime_info=True,
        initial_runtime_info={},
        enable_sentry=True,
        **kwargs,
    ):
        """
        A FastAPI wrapper that adds various convenience features.

        Args:
            cors_allow_origins (List[str], optional): A list of origins to allow CORS requests from. Defaults to ['*'] if the DEPLOYMENT_ENVIRONMENT environment variable is nonempty, otherwise []. This parameter is useful for local development. In production, CORS should be handled by the reverse proxy.
        """
        super().__init__(*args, **kwargs)

        if cors_allow_origins is None:
            cors_allow_origins = (
                ["*"] if getvar(Vars.DEPLOYMENT_ENVIRONMENT, logger=logger) else []
            )

        if cors_allow_origins:
            logger.info(
                f"Adding CORS middleware with allow_origins={cors_allow_origins}. This should only be used for local development. Please handle CORS at the reverse proxy in production."
            )
            self.add_middleware(
                CORSMiddleware,
                allow_origins=cors_allow_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        self.logger = logger

        if expose_metrics:
            Instrumentator().instrument(self).expose(self)

        if expose_build_info:
            self.add_api_route("/build-info", self.read_build_info, methods=["GET"])

        if expose_health:
            self.health_fns = health_fns
            self.add_api_route("/health", self.read_health, methods=["GET"])

        if expose_runtime_info:
            self.runtime_info = initial_runtime_info
            self.add_api_route("/runtime-info", self.read_runtime_info, methods=["GET"])

        if enable_sentry:
            sentry_has_dsn = set_up_sentry(logger=self.logger)
            if self.runtime_info is not None:
                self.runtime_info["sentry_has_dsn"] = sentry_has_dsn
                self.runtime_info["sentry_sdk_version"] = sentry_sdk.VERSION

    def read_build_info(self):
        return getvar(Vars.BUILD_INFO, logger=self.logger) or {}

    def read_health(self):
        for fn in self.health_fns:
            fn(self)
        return {"status": "ok"}

    def read_runtime_info(self):
        return self.runtime_info
