"""Interface de configuration pour l'intégration Sarool."""
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SaroolApiClient, SaroolApiError
from .const import (
    CONF_DEVICE_NAME,
    CONF_PK,
    CONF_UK,
    DEFAULT_DEVICE_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class SaroolConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gère le flux de configuration pour Sarool."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Gère l'étape de saisie des identifiants par l'utilisateur.
        
        Args:
            user_input: Données saisies par l'utilisateur
            
        Returns:
            Résultat du flux de configuration
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            # L'utilisateur a soumis le formulaire
            try:
                # Créer le client API
                session = async_get_clientsession(self.hass)
                api_client = SaroolApiClient(session)

                # Tenter l'authentification
                credentials = await api_client.authenticate(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME),
                )

                # Créer un ID unique basé sur l'identifiant
                await self.async_set_unique_id(user_input[CONF_USERNAME])
                self._abort_if_unique_id_configured()

                # Stocker les credentials dans la config
                config_data = {
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PK: credentials["pk"],
                    CONF_UK: credentials["uk"],
                    CONF_DEVICE_NAME: user_input.get(
                        CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME
                    ),
                }

                # Créer l'entrée de configuration
                return self.async_create_entry(
                    title=f"Sarool - {user_input[CONF_USERNAME]}",
                    data=config_data,
                )

            except SaroolApiError as err:
                _LOGGER.error("Erreur d'authentification Sarool: %s", err)
                errors["base"] = "invalid_auth"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Erreur inattendue lors de la configuration: %s", err)
                errors["base"] = "unknown"

        # Afficher le formulaire de saisie
        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(CONF_DEVICE_NAME, default=DEFAULT_DEVICE_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "username": "Votre identifiant Sarool",
                "password": "Votre mot de passe Sarool",
                "device_name": "Nom du périphérique (optionnel)",
            },
        )
