"""Client API pour Sarool."""
import asyncio
import logging
from datetime import datetime
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientSession

from .const import (
    API_F1,
    API_F2,
    API_F3,
    API_PERIPHERIQUE,
    API_UTILISATEUR,
)

_LOGGER = logging.getLogger(__name__)


class SaroolApiError(Exception):
    """Exception levée lors d'erreurs API."""


class SaroolApiClient:
    """Client pour l'API Sarool."""

    def __init__(self, session: ClientSession) -> None:
        """Initialise le client API.
        
        Args:
            session: Session aiohttp pour les requêtes HTTP
        """
        self._session = session
        self._pk: str | None = None  # Clé périphérique
        self._uk: str | None = None  # Clé utilisateur

    async def authenticate(
        self, username: str, password: str, device_name: str = "Home Assistant"
    ) -> dict[str, str]:
        """Authentifie l'utilisateur et récupère les clés PK et UK.
        
        Args:
            username: Identifiant Sarool
            password: Mot de passe
            device_name: Nom du périphérique
            
        Returns:
            Dictionnaire contenant PK et UK
            
        Raises:
            SaroolApiError: En cas d'erreur d'authentification
        """
        payload = {
            "Identifiant": username,
            "MotDePasse": password,
            "Descriptif": device_name,
            "PushToken": None,  # Pas de notifications push pour Home Assistant
        }

        try:
            async with self._session.post(
                API_PERIPHERIQUE,
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    self._pk = data.get("PK")
                    self._uk = data.get("UK")
                    _LOGGER.info("Authentification Sarool réussie")
                    return {"pk": self._pk, "uk": self._uk}
                elif response.status == 404:
                    raise SaroolApiError("Identifiant ou mot de passe incorrect")
                elif response.status == 401:
                    raise SaroolApiError("Compte bloqué suite à trop d'échecs")
                else:
                    raise SaroolApiError(f"Erreur d'authentification: {response.status}")
        except ClientError as err:
            raise SaroolApiError(f"Erreur de connexion: {err}") from err

    def set_credentials(self, pk: str, uk: str) -> None:
        """Définit les credentials pour les requêtes API.
        
        Args:
            pk: Clé périphérique
            uk: Clé utilisateur
        """
        self._pk = pk
        self._uk = uk

    def _get_headers(self) -> dict[str, str]:
        """Retourne les headers pour les requêtes authentifiées.
        
        Returns:
            Headers avec les clés d'authentification
        """
        if not self._pk or not self._uk:
            raise SaroolApiError("Pas de credentials disponibles")
        
        return {
            "PK": self._pk,
            "UK": self._uk,
            "Content-Type": "application/json",
        }

    async def get_student_info(self) -> dict[str, Any]:
        """Récupère les informations de l'élève (F1).
        
        Returns:
            Dictionnaire avec les infos de l'élève
        """
        try:
            async with self._session.get(
                API_F1, headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    raise SaroolApiError("Échec d'authentification")
                else:
                    raise SaroolApiError(f"Erreur API: {response.status}")
        except ClientError as err:
            raise SaroolApiError(f"Erreur de connexion: {err}") from err

    async def get_student_recap(self) -> dict[str, Any]:
        """Récupère le récapitulatif financier de l'élève (F2).
        
        Returns:
            Dictionnaire avec solde, leçons, prestations, etc.
        """
        try:
            async with self._session.get(
                API_F2, headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    raise SaroolApiError("Échec d'authentification")
                else:
                    raise SaroolApiError(f"Erreur API: {response.status}")
        except ClientError as err:
            raise SaroolApiError(f"Erreur de connexion: {err}") from err

    async def get_student_planning(
        self, date_debut: datetime, date_fin: datetime
    ) -> dict[str, Any]:
        """Récupère le planning de l'élève (F3).
        
        Args:
            date_debut: Date de début de recherche
            date_fin: Date de fin de recherche
            
        Returns:
            Dictionnaire avec la liste des rendez-vous
        """
        try:
            params = {
                "du": date_debut.isoformat(),
                "au": date_fin.isoformat(),
            }
            async with self._session.get(
                API_F3, headers=self._get_headers(), params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    raise SaroolApiError("Échec d'authentification")
                elif response.status == 404:
                    raise SaroolApiError("Fiche élève introuvable")
                elif response.status == 412:
                    raise SaroolApiError("Période de recherche érronée")
                else:
                    raise SaroolApiError(f"Erreur API: {response.status}")
        except ClientError as err:
            raise SaroolApiError(f"Erreur de connexion: {err}") from err

    async def get_user_data(
        self,
        with_persistent: bool = True,
        with_info: bool = True,
        with_recap: bool = True,
        with_files: bool = False,
    ) -> dict[str, Any]:
        """Récupère les données utilisateur (notifications, infos persistantes).
        
        Args:
            with_persistent: Retourner les données persistantes
            with_info: Récupérer les infos de l'élève
            with_recap: Récupérer le récap de l'élève
            with_files: Récupérer les infos sur les fichiers
            
        Returns:
            Dictionnaire avec les données de l'utilisateur
        """
        try:
            params = {
                "avecPersistant": str(with_persistent).lower(),
                "avecInfoEleve": str(with_info).lower(),
                "avecRecapEleve": str(with_recap).lower(),
                "avecFichierEleve": str(with_files).lower(),
            }
            async with self._session.get(
                f"{API_UTILISATEUR}/Donnees",
                headers=self._get_headers(),
                params=params,
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    raise SaroolApiError("Échec d'authentification")
                else:
                    raise SaroolApiError(f"Erreur API: {response.status}")
        except ClientError as err:
            raise SaroolApiError(f"Erreur de connexion: {err}") from err

    async def get_all_data(self) -> dict[str, Any]:
        """Récupère toutes les données de l'élève en parallèle.
        
        Returns:
            Dictionnaire avec toutes les données combinées
        """
        # Calculer les dates pour le planning (7 prochains jours)
        from datetime import timedelta
        now = datetime.now()
        date_fin = now + timedelta(days=7)

        try:
            # Récupérer toutes les données en parallèle
            info, recap, planning, user_data = await asyncio.gather(
                self.get_student_info(),
                self.get_student_recap(),
                self.get_student_planning(now, date_fin),
                self.get_user_data(),
                return_exceptions=True,
            )

            # Vérifier les erreurs
            for data in [info, recap, planning, user_data]:
                if isinstance(data, Exception):
                    raise data

            return {
                "info": info,
                "recap": recap,
                "planning": planning,
                "user_data": user_data,
            }
        except Exception as err:
            raise SaroolApiError(f"Erreur lors de la récupération des données: {err}") from err
