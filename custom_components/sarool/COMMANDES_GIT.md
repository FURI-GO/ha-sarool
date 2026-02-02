# 📋 COMMANDES GIT - Mise à jour de votre dépôt ha-sarool

## 🎯 Objectif
Remplacer les fichiers actuels de votre dépôt par la nouvelle intégration complète.

## 📍 Prérequis
- Git installé sur votre machine
- Accès à votre dépôt GitHub FURI-GO/ha-sarool
- Tous les fichiers téléchargés depuis Claude

## 🔧 Étapes à suivre

### 1. Cloner votre dépôt (si pas déjà fait)

```bash
# Ouvrir un terminal
cd ~/Documents  # ou le dossier de votre choix

# Cloner le dépôt
git clone https://github.com/FURI-GO/ha-sarool.git
cd ha-sarool
```

### 2. Sauvegarder l'ancien code (optionnel mais recommandé)

```bash
# Créer une branche de sauvegarde
git checkout -b backup-old-version
git push origin backup-old-version

# Retourner sur main
git checkout main
```

### 3. Supprimer les anciens fichiers

```bash
# Supprimer les fichiers existants
rm -rf custom_components/
rm README.md
rm hacs.jason  # Notez le typo dans le nom original
rm info.md
```

### 4. Copier les nouveaux fichiers

```bash
# Copier tous les fichiers téléchargés depuis Claude
# Remplacez /chemin/vers/telechargements par le vrai chemin

cp -r /chemin/vers/telechargements/custom_components/ .
cp /chemin/vers/telechargements/README.md .
cp /chemin/vers/telechargements/hacs.json .  # Nom corrigé
cp /chemin/vers/telechargements/info.md .
cp /chemin/vers/telechargements/.gitignore .
```

**Alternative Windows (PowerShell)** :
```powershell
# Copier les dossiers
Copy-Item -Path "C:\Users\VotreNom\Downloads\custom_components" -Destination . -Recurse

# Copier les fichiers
Copy-Item -Path "C:\Users\VotreNom\Downloads\README.md" -Destination .
Copy-Item -Path "C:\Users\VotreNom\Downloads\hacs.json" -Destination .
Copy-Item -Path "C:\Users\VotreNom\Downloads\info.md" -Destination .
Copy-Item -Path "C:\Users\VotreNom\Downloads\.gitignore" -Destination .
```

### 5. Vérifier que tout est correct

```bash
# Lister les fichiers
ls -la

# Vous devriez voir :
# .gitignore
# README.md
# hacs.json
# info.md
# custom_components/
```

```bash
# Vérifier la structure complète
find . -type f -not -path "./.git/*"

# Vous devriez avoir tous les fichiers Python, JSON, MD
```

### 6. Commiter les changements

```bash
# Voir les modifications
git status

# Ajouter tous les fichiers
git add .

# Créer le commit
git commit -m "✨ Intégration Sarool v1.0.0 complète

- Ajout de 3 capteurs (prochaine leçon, solde, notifications)
- Ajout du calendrier planning
- Interface de configuration
- Documentation complète
- Support HACS
- Traductions FR/EN"

# Pousser sur GitHub
git push origin main
```

### 7. Créer un tag de version (optionnel mais recommandé)

```bash
# Créer un tag pour la version 1.0.0
git tag -a v1.0.0 -m "Version 1.0.0 - Première version stable"

# Pousser le tag
git push origin v1.0.0
```

## 🎉 Vérification

1. Allez sur https://github.com/FURI-GO/ha-sarool
2. Vérifiez que tous les fichiers sont présents
3. Le README devrait s'afficher automatiquement

## 🔍 Commandes de vérification

```bash
# Voir l'historique des commits
git log --oneline

# Voir les fichiers trackés
git ls-files

# Voir les tags
git tag -l
```

## ⚠️ En cas de problème

### Annuler le dernier commit (avant push)
```bash
git reset --soft HEAD~1
```

### Annuler le dernier commit (après push)
```bash
git revert HEAD
git push origin main
```

### Revenir à la version précédente
```bash
git checkout backup-old-version
git checkout -b main-new
git branch -D main
git branch -m main
git push -f origin main
```

## 📱 Test de l'intégration

### Installation manuelle pour tester

1. Dans Home Assistant, allez dans `config/custom_components/`
2. Copiez le dossier `sarool/` depuis votre dépôt
3. Redémarrez Home Assistant
4. Allez dans Paramètres → Appareils et services
5. Cliquez sur "Ajouter une intégration"
6. Cherchez "Sarool"
7. Entrez vos identifiants

### Vérification des logs

1. Allez dans Paramètres → Système → Journaux
2. Cherchez "sarool" ou "custom_components.sarool"
3. Vérifiez qu'il n'y a pas d'erreurs

## 🚀 Publication sur HACS

Une fois que tout fonctionne :

1. Rendez le dépôt public (si privé)
2. Ajoutez un fichier LICENSE (MIT recommandé)
3. Créez une release sur GitHub
4. Les utilisateurs pourront l'installer via HACS

---

**Bon courage ! N'hésitez pas si vous avez des questions ! 🚗💨**
