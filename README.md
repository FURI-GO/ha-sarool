# Intégration Sarool pour Home Assistant ( En Constrution )

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Intégration Home Assistant pour suivre vos heures de conduite et votre planning avec l'application Sarool.

## 📋 Fonctionnalités

Cette intégration vous permet de :

- 📅 **Afficher votre prochaine leçon** avec les détails (moniteur, lieu, horaire)
- 💰 **Suivre votre solde** et vos informations financières
- 🔔 **Recevoir des notifications** pour les contrats à signer et dossiers incomplets
- 📆 **Visualiser tout votre planning** dans le calendrier Home Assistant

## 📦 Installation

### Via HACS (recommandé)

1. Ouvrez HACS dans Home Assistant
2. Cliquez sur "Intégrations"
3. Cliquez sur le menu (3 points) en haut à droite
4. Sélectionnez "Dépôts personnalisés"
5. Ajoutez l'URL : `https://github.com/FURI-GO/ha-sarool`
6. Catégorie : `Integration`
7. Cliquez sur "Télécharger"
8. Redémarrez Home Assistant

### Installation manuelle

1. Téléchargez ce dépôt
2. Copiez le dossier `custom_components/sarool` dans votre dossier `config/custom_components/`
3. Redémarrez Home Assistant

## ⚙️ Configuration

1. Allez dans **Paramètres** → **Appareils et services**
2. Cliquez sur **Ajouter une intégration**
3. Recherchez **Sarool**
4. Entrez vos identifiants Sarool :
   - Identifiant
   - Mot de passe
   - Nom du périphérique (optionnel, par défaut "Home Assistant")

## 📊 Capteurs disponibles

### Prochaine leçon
- **État** : Date et heure de la prochaine leçon
- **Attributs** :
  - Moniteur
  - Lieu de rendez-vous
  - Commentaire
  - Libellé

### Solde
- **État** : Solde global en euros
- **Attributs** :
  - Solde global
  - Solde réel
  - NEPH
  - Formule
  - Moniteur référent
  - Date d'inscription

### Notifications
- **État** : Nombre total de notifications
- **Attributs** :
  - Nombre de contrats à signer
  - Nombre d'éléments manquants au dossier
  - Fiche d'évaluation signée
  - Mémo

### Calendrier
- Affiche tout votre planning de leçons
- Intégré au calendrier Home Assistant
- Synchronisable avec Google Calendar, etc.

## 🔄 Mise à jour des données

Les données sont mises à jour automatiquement toutes les **5 minutes**.

Vous pouvez forcer une mise à jour en rechargeant l'intégration dans **Appareils et services**.

## 🎯 Exemples d'automatisations

### Notification 1h avant la leçon

```yaml
automation:
  - alias: "Rappel leçon de conduite"
    trigger:
      - platform: time
        at: sensor.prochaine_lecon
        offset: "-01:00:00"
    action:
      - service: notify.mobile_app
        data:
          title: "Leçon de conduite dans 1h"
          message: "Rendez-vous avec {{ state_attr('sensor.prochaine_lecon', 'moniteur') }} à {{ state_attr('sensor.prochaine_lecon', 'lieu_rdv') }}"
```

### Alerte contrat à signer

```yaml
automation:
  - alias: "Alerte contrat à signer"
    trigger:
      - platform: state
        entity_id: sensor.notifications
    condition:
      - condition: template
        value_template: "{{ state_attr('sensor.notifications', 'nb_contrats_a_signer') > 0 }}"
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Action requise"
          message: "Vous avez {{ state_attr('sensor.notifications', 'nb_contrats_a_signer') }} contrat(s) à signer sur Sarool"
```

## 🐛 Problèmes connus

- L'API Sarool peut avoir des limites de taux. Si vous rencontrez des erreurs, augmentez l'intervalle de mise à jour dans `const.py`

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ouvrir une issue pour signaler un bug
- Proposer une pull request pour ajouter des fonctionnalités

## 📝 Licence

Ce projet est sous licence MIT.

## ⚠️ Avertissement

Cette intégration n'est pas officielle et n'est pas affiliée à Sarool.
Utilisez-la à vos propres risques.

## 👨‍💻 Auteur

Créé par [@FURI-GO](https://github.com/FURI-GO)

---

Si cette intégration vous est utile, n'hésitez pas à mettre une ⭐ sur le dépôt !
