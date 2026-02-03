"""Calendrier pour l'intégration Sarool."""
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SaroolDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configure le calendrier Sarool.
    
    Args:
        hass: Instance Home Assistant
        entry: Entrée de configuration
        async_add_entities: Fonction pour ajouter les entités
    """
    coordinator: SaroolDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    calendar = SaroolCalendar(coordinator, entry)
    async_add_entities([calendar])


class SaroolCalendar(CoordinatorEntity, CalendarEntity):
    """Calendrier affichant le planning des leçons Sarool."""

    def __init__(self, coordinator: SaroolDataCoordinator, entry: ConfigEntry) -> None:
        """Initialise le calendrier.
        
        Args:
            coordinator: Coordinateur de données
            entry: Entrée de configuration
        """
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_calendar"
        self._attr_name = "Planning Sarool"
        self._attr_icon = "mdi:calendar-clock"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Sarool",
            "manufacturer": "Sarool",
            "model": "Auto-école",
        }

    @property
    def event(self) -> CalendarEvent | None:
        """Retourne le prochain événement du calendrier.
        
        Cette propriété est utilisée par Home Assistant pour afficher
        le prochain événement dans l'interface.
        
        Returns:
            Le prochain événement ou None
        """
        if not self.coordinator.data:
            return None

        planning = self.coordinator.data.get("planning", {})
        rdvs = planning.get("RendezVous", [])

        if not rdvs:
            return None

        from zoneinfo import ZoneInfo
        paris_tz = ZoneInfo("Europe/Paris")
        now = datetime.now(paris_tz)

        # Filtrer les rendez-vous futurs
        future_rdvs = []
        for rdv in rdvs:
            try:
                date_str = rdv["DateDebut"].replace("Z", "")
                rdv_date_naive = datetime.fromisoformat(date_str)
                rdv_date = rdv_date_naive.replace(tzinfo=paris_tz)
                
                if rdv_date > now:
                    future_rdvs.append((rdv, rdv_date))
            except (ValueError, KeyError):
                continue

        if not future_rdvs:
            return None

        # Trier et prendre le premier
        future_rdvs.sort(key=lambda x: x[1])
        next_rdv = future_rdvs[0][0]

        return self._convert_rdv_to_event(next_rdv)

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Retourne les événements entre deux dates.
        
        Cette méthode est appelée par Home Assistant pour afficher
        les événements dans le calendrier.
        
        Args:
            hass: Instance Home Assistant
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des événements dans la période demandée
        """
        if not self.coordinator.data:
            return []

        planning = self.coordinator.data.get("planning", {})
        rdvs = planning.get("RendezVous", [])

        from zoneinfo import ZoneInfo
        paris_tz = ZoneInfo("Europe/Paris")

        # Filtrer les rendez-vous dans la période demandée
        events = []
        for rdv in rdvs:
            try:
                start_str = rdv["DateDebut"].replace("Z", "")
                end_str = rdv["DateFin"].replace("Z", "")
                
                rdv_start_naive = datetime.fromisoformat(start_str)
                rdv_end_naive = datetime.fromisoformat(end_str)
                
                rdv_start = rdv_start_naive.replace(tzinfo=paris_tz)
                rdv_end = rdv_end_naive.replace(tzinfo=paris_tz)

                # Vérifier si le rendez-vous est dans la période
                if rdv_start <= end_date and rdv_end >= start_date:
                    events.append(self._convert_rdv_to_event(rdv))
            except (ValueError, KeyError) as e:
                _LOGGER.debug(f"Erreur parsing rdv pour calendrier: {e}")
                continue

        return events

    def _convert_rdv_to_event(self, rdv: dict[str, Any]) -> CalendarEvent:
        """Convertit un rendez-vous Sarool en événement de calendrier.
        
        Args:
            rdv: Dictionnaire représentant un rendez-vous Sarool
            
        Returns:
            CalendarEvent pour Home Assistant
        """
        from zoneinfo import ZoneInfo
        
        # Timezone française (l'API retourne des dates locales françaises)
        paris_tz = ZoneInfo("Europe/Paris")
        
        # Parser les dates (sans timezone dans l'API)
        start_str = rdv["DateDebut"].replace("Z", "")
        end_str = rdv["DateFin"].replace("Z", "")
        
        start_naive = datetime.fromisoformat(start_str)
        end_naive = datetime.fromisoformat(end_str)
        
        # Ajouter la timezone
        start = start_naive.replace(tzinfo=paris_tz)
        end = end_naive.replace(tzinfo=paris_tz)

        # Construire le titre
        libelle = rdv.get("Libelle", "Leçon de conduite")
        moniteur = rdv.get("Moniteur", "")
        if moniteur:
            title = f"{libelle} - {moniteur}"
        else:
            title = libelle

        # Construire la description
        description_parts = []
        if rdv.get("LieuRdv"):
            description_parts.append(f"Lieu: {rdv['LieuRdv']}")
        if rdv.get("Commentaire"):
            description_parts.append(f"Commentaire: {rdv['Commentaire']}")

        description = "\n".join(description_parts) if description_parts else None

        # Construire le lieu
        location = rdv.get("LieuRdv")

        return CalendarEvent(
            start=start,
            end=end,
            summary=title,
            description=description,
            location=location,
        )
