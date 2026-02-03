# 🚗 GUIDE COMPLET - Intégration Sarool pour Home Assistant

## 📁 Structure du projet

Voici l'arborescence complète de votre intégration :

```
sarool-integration/
├── .gitignore                                    # Fichiers à ignorer par Git
├── README.md                                     # Documentation principale
├── hacs.json                                     # Configuration HACS
├── info.md                                       # Description courte pour HACS
└── custom_components/
    └── sarool/
        ├── __init__.py                          # Point d'entrée de l'intégration
        ├── manifest.json                        # Métadonnées de l'intégration
        ├── const.py                             # Constantes (URLs API, noms, etc.)
        ├── api.py                               # Client API Sarool
        ├── coordinator.py                       # Gestion des mises à jour
        ├── config_flow.py                       # Interface de configuration
        ├── sensor.py                            # Les 3 capteurs
        ├── calendar.py                          # Calendrier du planning
        └── translations/
            ├── fr.json                          # Traductions françaises
            └── en.json                          # Traductions anglaises
```

## 🎯 Fonctionnalités implémentées

### ✅ Capteurs (3)
1. **Prochaine leçon** (`sensor.prochaine_lecon`)
   - État : Date/heure de la prochaine leçon
   - Attributs : Moniteur, lieu RDV, commentaire

2. **Solde** (`sensor.solde`)
   - État : Solde global en €
   - Attributs : Solde réel, NEPH, formule, moniteur référent

3. **Notifications** (`sensor.notifications`)
   - État : Nombre total de notifications
   - Attributs : Contrats à signer, dossiers incomplets

### ✅ Calendrier
- **Planning complet** (`calendar.planning_sarool`)
  - Affiche toutes vos leçons
  - Intégré au calendrier Home Assistant

## 🔧 Installation sur GitHub

### Étape 1 : Nettoyer votre dépôt actuel

```bash
# Depuis votre dépôt local ha-sarool
git pull origin main
rm -rf custom_components/
rm README.md hacs.jason info.md
```

### Étape 2 : Copier les nouveaux fichiers

1. Téléchargez tous les fichiers que je vous ai créés
2. Copiez-les dans votre dépôt `ha-sarool/`
3. Vérifiez que la structure est correcte

### Étape 3 : Commiter et pousser

```bash
git add .
git commit -m "Intégration Sarool complète v1.0.0"
git push origin main
```

## 📦 Installation dans Home Assistant

### Via HACS (après publication sur GitHub)

1. Ouvrez HACS
2. Cliquez sur "Intégrations"
3. Menu (⋮) → "Dépôts personnalisés"
4. URL : `https://github.com/FURI-GO/ha-sarool`
5. Catégorie : `Integration`
6. Télécharger et redémarrer HA

### Installation manuelle (pour tester)

1. Copiez le dossier `custom_components/sarool` dans votre `config/custom_components/`
2. Redémarrez Home Assistant
3. Allez dans Paramètres → Appareils et services → Ajouter
4. Cherchez "Sarool"

## 🔐 Configuration

Lors de la configuration, vous devrez fournir :
- **Identifiant** : Votre login Sarool
- **Mot de passe** : Votre mot de passe Sarool
- **Nom du périphérique** (optionnel) : Par défaut "Home Assistant"

⚠️ **Sécurité** : Ces informations sont stockées de manière sécurisée dans Home Assistant.

## 📊 Utilisation des capteurs

### Dans un dashboard Lovelace

```yaml
type: entities
title: Sarool Auto-école
entities:
  - entity: sensor.prochaine_lecon
    name: Prochaine leçon
  - entity: sensor.solde
    name: Solde restant
  - entity: sensor.notifications
    name: Actions à faire
```

### Dans le calendrier

Le calendrier `calendar.planning_sarool` s'affiche automatiquement dans l'onglet Calendrier de Home Assistant.

## 🤖 Exemples d'automatisations

### Rappel 1h avant la leçon

```yaml
automation:
  - alias: "Rappel leçon de conduite"
    trigger:
      - platform: state
        entity_id: sensor.prochaine_lecon
    action:
      - delay:
          hours: -1  # 1h avant
      - service: notify.mobile_app_votre_telephone
        data:
          title: "⏰ Leçon dans 1h"
          message: >
            Rendez-vous avec {{ state_attr('sensor.prochaine_lecon', 'moniteur') }}
            à {{ state_attr('sensor.prochaine_lecon', 'lieu_rdv') }}
```

### Alerte contrat à signer

```yaml
automation:
  - alias: "Alerte contrat Sarool"
    trigger:
      - platform: numeric_state
        entity_id: sensor.notifications
        attribute: nb_contrats_a_signer
        above: 0
    action:
      - service: notify.mobile_app_votre_telephone
        data:
          title: "📝 Sarool"
          message: "Vous avez un contrat à signer !"
```

## 🐛 Débogage

### Activer les logs

Ajoutez dans `configuration.yaml` :

```yaml
logger:
  default: info
  logs:
    custom_components.sarool: debug
```

### Vérifier les données

Dans les Outils de développement → États, cherchez :
- `sensor.prochaine_lecon`
- `sensor.solde`
- `sensor.notifications`
- `calendar.planning_sarool`

## 🔄 Mise à jour des données

- **Intervalle** : 5 minutes (configurable dans `const.py` → `UPDATE_INTERVAL`)
- **Manuel** : Rechargez l'intégration dans Appareils et services

## 📝 Explications du code (pour apprendre)

### Flux d'exécution

1. **Authentification** (`config_flow.py`)
   - L'utilisateur entre ses identifiants
   - Appel API → récupération PK et UK
   - Stockage sécurisé dans Home Assistant

2. **Initialisation** (`__init__.py`)
   - Création du client API avec PK/UK
   - Création du coordinateur
   - Configuration des plateformes (sensor, calendar)

3. **Mise à jour** (`coordinator.py`)
   - Toutes les 5 minutes
   - Appelle `api.get_all_data()`
   - Distribue les données aux capteurs

4. **Affichage** (`sensor.py`, `calendar.py`)
   - Les capteurs lisent les données du coordinateur
   - Calculent leur état et attributs
   - Home Assistant affiche le résultat

### Concepts Python importants

- **async/await** : Programmation asynchrone
- **Type hints** : `str | None`, `dict[str, Any]`
- **Classes** : Héritage de `SensorEntity`, `CalendarEntity`
- **Décorateurs** : `@property`
- **Gestion d'erreurs** : `try/except`

## 🎓 Prochaines étapes pour apprendre

1. **Modifier UPDATE_INTERVAL** dans `const.py`
2. **Ajouter un nouveau capteur** dans `sensor.py`
3. **Personnaliser les icônes** (voir `mdi:` icons)
4. **Créer vos propres automatisations**

## ✅ Checklist de déploiement

- [ ] Code copié dans le dépôt GitHub
- [ ] Commit et push effectués
- [ ] Testé en installation manuelle
- [ ] README à jour
- [ ] Version dans `manifest.json`
- [ ] Prêt pour HACS

## 🆘 Support

- **Issues GitHub** : https://github.com/FURI-GO/ha-sarool/issues
- **Documentation HA** : https://developers.home-assistant.io

---

**Bravo ! Vous avez créé votre première intégration Home Assistant ! 🎉**
