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
        """Retourne le prochain événement du calendrier."""
        if not self.coordinator.data:
            return None

        lessons_data = self.coordinator.data.get("lessons", {})
        lecons = lessons_data.get("Lecons", [])

        if not lecons:
            return None

        from zoneinfo import ZoneInfo
        paris_tz = ZoneInfo("Europe/Paris")
        now = datetime.now(paris_tz)

        # Filtrer les leçons futures non annulées
        future_lessons = []
        for lecon in lecons:
            try:
                if lecon.get("IsAnnule", 0) == 1:
                    continue
                    
                date_str = lecon["Date"]
                lesson_date_naive = datetime.fromisoformat(date_str)
                lesson_date = lesson_date_naive.replace(tzinfo=paris_tz)
                
                if lesson_date > now:
                    future_lessons.append((lecon, lesson_date))
            except (ValueError, KeyError):
                continue

        if not future_lessons:
            return None

        # Trier et prendre la première
        future_lessons.sort(key=lambda x: x[1])
        next_lesson = future_lessons[0][0]

        return self._convert_lesson_to_event(next_lesson)

async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Retourne les événements entre deux dates."""
        if not self.coordinator.data:
            return []

        lessons_data = self.coordinator.data.get("lessons", {})
        lecons = lessons_data.get("Lecons", [])

        from zoneinfo import ZoneInfo
        paris_tz = ZoneInfo("Europe/Paris")

        # Filtrer les leçons dans la période demandée
        events = []
        for lecon in lecons:
            try:
                # Ignorer les leçons annulées
                if lecon.get("IsAnnule", 0) == 1:
                    continue
                
                date_str = lecon["Date"]
                duree = lecon.get("Duree", 60)  # Durée en minutes
                
                lesson_start_naive = datetime.fromisoformat(date_str)
                lesson_start = lesson_start_naive.replace(tzinfo=paris_tz)
                lesson_end = lesson_start + timedelta(minutes=duree)

                # Vérifier si la leçon est dans la période
                if lesson_start <= end_date and lesson_end >= start_date:
                    events.append(self._convert_lesson_to_event(lecon))
            except (ValueError, KeyError) as e:
                _LOGGER.debug(f"Erreur parsing leçon pour calendrier: {e}")
                continue

        return events
   
def _convert_lesson_to_event(self, lecon: dict[str, Any]) -> CalendarEvent:
        """Convertit une leçon Sarool en événement de calendrier.
        
        Args:
            lecon: Dictionnaire représentant une leçon Sarool
            
        Returns:
            CalendarEvent pour Home Assistant
        """
        from zoneinfo import ZoneInfo
        
        paris_tz = ZoneInfo("Europe/Paris")
        
        # Parser la date
        date_str = lecon["Date"]
        duree = lecon.get("Duree", 60)  # Durée en minutes
        
        start_naive = datetime.fromisoformat(date_str)
        start = start_naive.replace(tzinfo=paris_tz)
        end = start + timedelta(minutes=duree)

        # Construire le titre
        libelle = lecon.get("Libelle", "Leçon de conduite")
        formateur = lecon.get("Formateur", "")
        numero = lecon.get("Numero", "")
        
        if formateur:
            title = f"{libelle} #{numero} - {formateur}"
        else:
            title = f"{libelle} #{numero}"

        # Construire la description
        description_parts = []
        if lecon.get("LieuRdv"):
            description_parts.append(f"Lieu: {lecon['LieuRdv']}")
        if lecon.get("Commentaire"):
            description_parts.append(f"Commentaire: {lecon['Commentaire']}")
        if lecon.get("SuiviPedago"):
            description_parts.append(f"Suivi: {lecon['SuiviPedago']}")

        description = "\n".join(description_parts) if description_parts else None

        return CalendarEvent(
            start=start,
            end=end,
            summary=title,
            description=description,
            location=lecon.get("LieuRdv"),
        )