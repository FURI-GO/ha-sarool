"""Coordinateur de données pour l'intégration Sarool."""
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SaroolApiClient, SaroolApiError
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class SaroolDataCoordinator(DataUpdateCoordinator):
    """Classe pour gérer la récupération des données depuis l'API Sarool."""

    def __init__(self, hass: HomeAssistant, api_client: SaroolApiClient) -> None:
        """Initialise le coordinateur.
        
        Args:
            hass: Instance Home Assistant
            api_client: Client API Sarool
        """
        self.api_client = api_client
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self):
        """Récupère les données depuis l'API.
        
        Cette méthode est appelée automatiquement par Home Assistant
        selon l'intervalle défini (UPDATE_INTERVAL).
        
        Returns:
            Dictionnaire avec toutes les données de l'élève
            
        Raises:
            UpdateFailed: Si la mise à jour échoue
        """
        try:
            _LOGGER.debug("Récupération des données Sarool")
            data = await self.api_client.get_all_data()
            _LOGGER.debug("Données Sarool récupérées avec succès")
            return data
        except SaroolApiError as err:
            raise UpdateFailed(f"Erreur lors de la mise à jour des données: {err}") from err
