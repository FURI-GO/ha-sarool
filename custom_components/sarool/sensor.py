"""Capteurs pour l'intégration Sarool."""
from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_COMMENTAIRE,
    ATTR_DATE_INSCRIPTION,
    ATTR_FORMULE,
    ATTR_LIEU_RDV,
    ATTR_MONITEUR,
    ATTR_NB_CONTRATS_A_SIGNER,
    ATTR_NB_DOSSIER_INCOMPLET,
    ATTR_NEPH,
    ATTR_SOLDE_GLOBAL,
    ATTR_SOLDE_REEL,
    DOMAIN,
)
from .coordinator import SaroolDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configure les capteurs Sarool.
    
    Args:
        hass: Instance Home Assistant
        entry: Entrée de configuration
        async_add_entities: Fonction pour ajouter les entités
    """
    coordinator: SaroolDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Créer les 3 capteurs
    sensors = [
        SaroolNextLessonSensor(coordinator, entry),
        SaroolBalanceSensor(coordinator, entry),
        SaroolNotificationsSensor(coordinator, entry),
    ]

    async_add_entities(sensors)


class SaroolSensorBase(CoordinatorEntity, SensorEntity):
    """Classe de base pour les capteurs Sarool."""

    def __init__(
        self,
        coordinator: SaroolDataCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
    ) -> None:
        """Initialise le capteur.
        
        Args:
            coordinator: Coordinateur de données
            entry: Entrée de configuration
            sensor_type: Type de capteur (next_lesson, balance, notifications)
        """
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Sarool",
            "manufacturer": "Sarool",
            "model": "Auto-école",
        }


class SaroolNextLessonSensor(SaroolSensorBase):
    """Capteur pour la prochaine leçon de conduite."""

    def __init__(self, coordinator: SaroolDataCoordinator, entry: ConfigEntry) -> None:
        """Initialise le capteur de prochaine leçon."""
        super().__init__(coordinator, entry, "next_lesson")
        self._attr_name = "Prochaine leçon"
        self._attr_icon = "mdi:car"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        """Retourne la date/heure de la prochaine leçon.
        
        Returns:
            Datetime de la prochaine leçon ou None si aucune leçon
        """
        if not self.coordinator.data:
            return None

        planning = self.coordinator.data.get("planning", {})
        rdvs = planning.get("RendezVous", [])

        # Filtrer les rendez-vous futurs et trier par date
        now = datetime.now()
        future_rdvs = [
            rdv for rdv in rdvs
            if datetime.fromisoformat(rdv["DateDebut"].replace("Z", "+00:00")) > now
        ]

        if not future_rdvs:
            return None

        # Trier et prendre le premier
        future_rdvs.sort(key=lambda x: x["DateDebut"])
        next_rdv = future_rdvs[0]

        return datetime.fromisoformat(next_rdv["DateDebut"].replace("Z", "+00:00"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Retourne les attributs supplémentaires du capteur.
        
        Returns:
            Dictionnaire avec moniteur, lieu, commentaire, etc.
        """
        if not self.coordinator.data:
            return {}

        planning = self.coordinator.data.get("planning", {})
        rdvs = planning.get("RendezVous", [])

        now = datetime.now()
        future_rdvs = [
            rdv for rdv in rdvs
            if datetime.fromisoformat(rdv["DateDebut"].replace("Z", "+00:00")) > now
        ]

        if not future_rdvs:
            return {}

        future_rdvs.sort(key=lambda x: x["DateDebut"])
        next_rdv = future_rdvs[0]

        return {
            ATTR_MONITEUR: next_rdv.get("Moniteur", "Non défini"),
            ATTR_LIEU_RDV: next_rdv.get("LieuRdv", "Non défini"),
            ATTR_COMMENTAIRE: next_rdv.get("Commentaire", ""),
            "libelle": next_rdv.get("Libelle", ""),
            "date_fin": next_rdv.get("DateFin", ""),
        }


class SaroolBalanceSensor(SaroolSensorBase):
    """Capteur pour le solde de l'élève."""

    def __init__(self, coordinator: SaroolDataCoordinator, entry: ConfigEntry) -> None:
        """Initialise le capteur de solde."""
        super().__init__(coordinator, entry, "balance")
        self._attr_name = "Solde"
        self._attr_icon = "mdi:currency-eur"
        self._attr_native_unit_of_measurement = CURRENCY_EURO
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self) -> float | None:
        """Retourne le solde de l'élève.
        
        Returns:
            Solde en euros ou None
        """
        if not self.coordinator.data:
            return None

        recap = self.coordinator.data.get("recap", {})
        return recap.get("SoldeGlobal")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Retourne les attributs supplémentaires du capteur.
        
        Returns:
            Dictionnaire avec solde global et solde réel
        """
        if not self.coordinator.data:
            return {}

        recap = self.coordinator.data.get("recap", {})
        info = self.coordinator.data.get("info", {})

        return {
            ATTR_SOLDE_GLOBAL: recap.get("SoldeGlobal"),
            ATTR_SOLDE_REEL: recap.get("SoldeReel"),
            ATTR_NEPH: info.get("NEPH", ""),
            ATTR_FORMULE: info.get("Formule", ""),
            ATTR_MONITEUR: info.get("MoniteurReferent", ""),
            ATTR_DATE_INSCRIPTION: info.get("DateInscription", ""),
        }


class SaroolNotificationsSensor(SaroolSensorBase):
    """Capteur pour les notifications (contrats à signer, dossiers incomplets)."""

    def __init__(self, coordinator: SaroolDataCoordinator, entry: ConfigEntry) -> None:
        """Initialise le capteur de notifications."""
        super().__init__(coordinator, entry, "notifications")
        self._attr_name = "Notifications"
        self._attr_icon = "mdi:bell-alert"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        """Retourne le nombre total de notifications.
        
        Returns:
            Nombre de notifications
        """
        if not self.coordinator.data:
            return 0

        user_data = self.coordinator.data.get("user_data", {})
        nb_contrats = user_data.get("NbContratsASigner", 0) or 0
        nb_dossier = user_data.get("NbDossierIndispensable", 0) or 0

        return nb_contrats + nb_dossier

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Retourne les attributs supplémentaires du capteur.
        
        Returns:
            Dictionnaire avec détail des notifications
        """
        if not self.coordinator.data:
            return {}

        user_data = self.coordinator.data.get("user_data", {})

        return {
            ATTR_NB_CONTRATS_A_SIGNER: user_data.get("NbContratsASigner", 0) or 0,
            ATTR_NB_DOSSIER_INCOMPLET: user_data.get("NbDossierIndispensable", 0) or 0,
            "fiche_eval_signee": user_data.get("IsFicheEvalSigne", False),
            "memo": user_data.get("Memo", ""),
        }
