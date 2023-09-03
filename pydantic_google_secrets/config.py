import logging
from typing import Any, Dict, Optional, Tuple, Type

import google.auth as gc_auth
from google.api_core.exceptions import NotFound, PermissionDenied
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import secretmanager
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

logger = logging.getLogger(__name__)


class GoogleSecretManagerConfigSettingsSource(PydanticBaseSettingsSource):
    """
    A settings class that loads settings from Google Secret Manager.

    The account under which the application is executed should have the
    required access to Google Secret Manager.
    """

    def __init__(self, settings_cls: Type[BaseSettings]):
        super().__init__(settings_cls)

        self._client = None
        self._project_id = None

    def _get_gsm_value(self, field_name: str) -> Optional[str]:
        """
        Make the call to the Google Secret Manager API to get the value of the
        secret.
        """
        secret_name = self._client.secret_version_path(
            project=self._project_id, secret=field_name, secret_version="latest"
        )

        response = self._client.access_secret_version(name=secret_name)
        return response.payload.data.decode("UTF-8")

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        """
        Get the value of a field from Google Secret Manager.
        """
        try:
            field_name = field.alias or field_name
            field_value = self._get_gsm_value(field_name)
        except (NotFound, PermissionDenied) as e:
            logger.debug(e)
            field_value = None

        return field_value, field_name, False

    def __call__(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}

        try:
            # Set the credentials and project ID from the application default
            # credentials
            _credentials, project_id = gc_auth.default()
            self._project_id = project_id
            self._client = secretmanager.SecretManagerServiceClient(
                credentials=_credentials
            )

            for field_name, field in self.settings_cls.model_fields.items():
                field_value, field_key, value_is_complex = self.get_field_value(
                    field, field_name
                )
                field_value = self.prepare_field_value(
                    field_name, field, field_value, value_is_complex
                )
                if field_value is not None:
                    d[field_key] = field_value

        except DefaultCredentialsError as e:
            logger.debug(e)

        return d


class Settings(BaseSettings):
    my_secret_value: str

    model_config = SettingsConfigDict(
        case_sensitive=False, env_file=".env", env_file_encoding="utf-8"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            GoogleSecretManagerConfigSettingsSource(settings_cls),
        )
