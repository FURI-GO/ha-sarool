"""Intégration Sarool pour Home Assistant."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SaroolApiClient
from .const import CONF_PK, CONF_UK, DOMAIN
from .coordinator import SaroolDataCoordinator

_LOGGER = logging.getLogger(__name__)

# Liste des plateformes supportées par l'intégration
PLATFORMS: list[Platform] = [
    Platform.SENSOR,      # Les capteurs (solde, prochaine leçon, notifications)
    Platform.CALENDAR,    # Le calendrier du planning
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configure l'intégration Sarool à partir d'une entrée de configuration.
    
    Cette fonction est appelée par Home Assistant lors de l'ajout de l'intégration.
    
    Args:
        hass: Instance Home Assistant
        entry: Entrée de configuration contenant les credentials
        
    Returns:
        True si la configuration a réussi, False sinon
    """
    _LOGGER.info("Configuration de l'intégration Sarool")

    # Récupérer les credentials depuis la configuration
    pk = entry.data[CONF_PK]
    uk = entry.data[CONF_UK]

    # Créer le client API
    session = async_get_clientsession(hass)
    api_client = SaroolApiClient(session)
    api_client.set_credentials(pk, uk)

    # Créer le coordinateur de données
    coordinator = SaroolDataCoordinator(hass, api_client)

    # Faire une première récupération des données
    await coordinator.async_config_entry_first_refresh()

    # Stocker le coordinateur dans hass.data pour que les plateformes puissent y accéder
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Configurer les plateformes (sensors, calendar)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info("Intégration Sarool configurée avec succès")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Décharge l'intégration Sarool.
    
    Cette fonction est appelée lors de la suppression de l'intégration.
    
    Args:
        hass: Instance Home Assistant
        entry: Entrée de configuration
        
    Returns:
        True si le déchargement a réussi
    """
    _LOGGER.info("Déchargement de l'intégration Sarool")

    # Décharger les plateformes
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Supprimer les données stockées
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
