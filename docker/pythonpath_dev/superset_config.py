# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# This file is included in the final Docker image and SHOULD be overridden when
# deploying the image to prod. Settings configured here are intended for use in local
# development environments. Also note that superset_config_docker.py is imported
# as a final step as a means to override "defaults" configured here
#
import logging
import os
from smtplib import SMTP_SSL

from celery.schedules import crontab
from flask_caching.backends.filesystemcache import FileSystemCache
from flask_appbuilder.security.manager import AUTH_OAUTH
from custom_sso_security_manager import CustomSsoSecurityManager

CUSTOM_SECURITY_MANAGER = CustomSsoSecurityManager

import config_custom as cc

logger = logging.getLogger()

DATABASE_DIALECT = os.getenv("DATABASE_DIALECT")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_DB = os.getenv("DATABASE_DB")

EXAMPLES_USER = os.getenv("EXAMPLES_USER")
EXAMPLES_PASSWORD = os.getenv("EXAMPLES_PASSWORD")
EXAMPLES_HOST = os.getenv("EXAMPLES_HOST")
EXAMPLES_PORT = os.getenv("EXAMPLES_PORT")
EXAMPLES_DB = os.getenv("EXAMPLES_DB")

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = (
    f"{DATABASE_DIALECT}://"
    f"{DATABASE_USER}:{DATABASE_PASSWORD}@"
    f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"
)

SQLALCHEMY_EXAMPLES_URI = (
    f"{DATABASE_DIALECT}://"
    f"{EXAMPLES_USER}:{EXAMPLES_PASSWORD}@"
    f"{EXAMPLES_HOST}:{EXAMPLES_PORT}/{EXAMPLES_DB}"
)

REDIS_HOST = os.getenv("REDIS_HOST", cc.REDIS_HOST)
REDIS_PORT = os.getenv("REDIS_PORT", cc.REDIS_PORT)
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", cc.REDIS_CELERY_DB)
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", cc.REDIS_RESULTS_DB)

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": cc.CACHE_DEFAULT_TIMEOUT,
    "CACHE_KEY_PREFIX": cc.CACHE_KEY_PREFIX,
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
    "CACHE_REDIS_URL": cc.CACHE_REDIS_URL,
}
DATA_CACHE_CONFIG = CACHE_CONFIG


class CeleryConfig:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = ("superset.sql_lab",)
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    worker_prefetch_multiplier = 1
    task_acks_late = False
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

FEATURE_FLAGS = {
    "ALERT_REPORTS": cc.ALERT_REPORTS,
    "DASHBOARD_RBAC": cc.DASHBOARD_RBAC,
    # doesn't exist "DASHBOARD_NATIVE_FILTERS": cc.DASHBOARD_NATIVE_FILTERS,
    # doesn't exist "ALERTS_V2": cc.ALERTS_V2,
    # doesn't exist "VERSIONED_EXPORT": cc.VERSIONED_EXPORT,
    "EMBEDDED_SUPERSET": cc.EMBEDDED_SUPERSET,
    # doesn't exist "DASHBOARD_CROSS_FILTERS": cc.DASHBOARD_CROSS_FILTERS,
}
ALERT_REPORTS_NOTIFICATION_DRY_RUN = cc.ALERT_REPORTS_NOTIFICATION_DRY_RUN

SMTP_HOST = cc.SMTP_HOST
SMTP_HOST = cc.SMTP_PORT
SMTP_STARTTLS = cc.SMTP_STARTTLS
SMTP_SSL = cc.SMTP_SSL
SMTP_USER = cc.SMTP_USER
SMTP_PASSWORD = cc.SMTP_PASSWORD
SMTP_MAIL_FROM = cc.SMTP_MAIL_FROM


WEBDRIVER_BASEURL = "http://superset:8088/"  # When using docker compose baseurl should be http://superset_app:8088/
# The base URL for the email report hyperlinks.
WEBDRIVER_BASEURL_USER_FRIENDLY = WEBDRIVER_BASEURL

SQLLAB_CTAS_NO_LIMIT = True

SLACK_API_TOKEN = cc.SLACK_API_TOKEN


# Set the authentication type to OAuth
AUTH_TYPE = AUTH_OAUTH

OAUTH_PROVIDERS = [
    {
        'name': 'google',
        'whitelist': "gmail.com",
        'icon': 'fa-google',
        'token_key': 'access_token',
        'remote_app': {
            'base_url': 'https://www.googleapis.com/oauth2/v2/',
            'request_token_params': {
                'scope': 'https://www.googleapis.com/auth/userinfo.email'
            },
            'request_token_url': None,
            'access_token_url': 'https://accounts.google.com/o/oauth2/token',
            'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
            'consumer_key': cc.SUPERSET_AUTH_KEY,
            'consumer_secret': cc.SUPERSET_AUTH_SECRET
        }
    }
]

'''OAUTH_PROVIDERS = [
    {
        "name": "egaSSO",
        "token_key": "access_token",  # Name of the token in the response of access_token_url
        "icon": "fa-address-card",  # Icon for the provider
        "remote_app": {
            "client_id": "myClientId",  # Client Id (Identify Superset application)
            "client_secret": "MySecret",  # Secret for this Client Id (Identify Superset application)
            "client_kwargs": {"scope": "read"},  # Scope for the Authorization
            "access_token_method": "POST",  # HTTP Method to call access_token_url
            "access_token_params": {  # Additional parameters for calls to access_token_url
                "client_id": "myClientId"
            },
            "jwks_uri": "https://myAuthorizationServe/adfs/discovery/keys",  # may be required to generate token
            "access_token_headers": {  # Additional headers for calls to access_token_url
                "Authorization": "Basic Base64EncodedClientIdAndSecret"
            },
            "api_base_url": "https://myAuthorizationServer/oauth2AuthorizationServer/",
            "access_token_url": "https://myAuthorizationServer/oauth2AuthorizationServer/token",
            "authorize_url": "https://myAuthorizationServer/oauth2AuthorizationServer/authorize",
        },
    }
]'''

# Will allow user self registration, allowing to create Flask users from Authorized User
AUTH_USER_REGISTRATION = True

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Public"

#
# Optionally import superset_config_docker.py (which will have been included on
# the PYTHONPATH) in order to allow for local settings to be overridden
#
try:
    import superset_config_docker
    from superset_config_docker import *  # noqa

    logger.info(
        f"Loaded your Docker configuration at " f"[{superset_config_docker.__file__}]"
    )
except ImportError:
    logger.info("Using default Docker config...")
