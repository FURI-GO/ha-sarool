"""Constantes pour l'intégration Sarool."""

# Domaine de l'intégration
DOMAIN = "sarool"

# URLs de l'API Sarool
API_BASE_URL = "https://api.sarool.fr"
API_PERIPHERIQUE = f"{API_BASE_URL}/Peripherique"
API_F1 = f"{API_BASE_URL}/F1"
API_F2 = f"{API_BASE_URL}/F2"
API_F3 = f"{API_BASE_URL}/F3"
API_UTILISATEUR = f"{API_BASE_URL}/Utilisateur"

# Clés de configuration
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_DEVICE_NAME = "device_name"

# Clés pour stocker les tokens
CONF_PK = "pk"  # Clé périphérique
CONF_UK = "uk"  # Clé utilisateur

# Intervalle de mise à jour (en secondes)
# 5 minutes par défaut pour ne pas surcharger l'API
UPDATE_INTERVAL = 300

# Attributs des capteurs
ATTR_NEPH = "neph"
ATTR_FORMULE = "formule"
ATTR_MONITEUR = "moniteur"
ATTR_DATE_INSCRIPTION = "date_inscription"
ATTR_LIEU_RDV = "lieu_rdv"
ATTR_COMMENTAIRE = "commentaire"
ATTR_SOLDE_GLOBAL = "solde_global"
ATTR_SOLDE_REEL = "solde_reel"
ATTR_NB_CONTRATS_A_SIGNER = "nb_contrats_a_signer"
ATTR_NB_DOSSIER_INCOMPLET = "nb_dossier_incomplet"

# Noms par défaut
DEFAULT_DEVICE_NAME = "Home Assistant"
DEFAULT_NAME = "Sarool"
