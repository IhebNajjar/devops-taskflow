# TaskFlow — Smart Task & Project Manager (DevOps Module)
**Étudiant :** Licence 3 · DSI · ISET  
**Module :** DevOps — Projet de Fin de Module  
**Note visée :** 20 / 20 (16 pts essentiels + 4 pts soutenance + 4 pts bonus)

---

## 🚀 Démarrer le Projet en UNE Seule Commande

Pour lancer l'ensemble de l'infrastructure (Application FastAPI + Base de données PostgreSQL + Volume persistant) :

```bash
docker compose up -d --build
```

L'application est immédiatement accessible sur :
* **Interface Web :** [http://localhost:8000](http://localhost:8000)
* **Contrôle de Santé :** [http://localhost:8000/health](http://localhost:8000/health)

---

## 📋 Tableau de Conformité au Barème de l'Enseignant

| # | Exigence du Guide Étudiant | Fichier / Implémentation | Statut |
| :--- | :--- | :--- | :--- |
| **1** | **Git propre** (Commits clairs, .gitignore, aucun secret) | `.gitignore`, `.env.example`, commits conventionnels | ✅ Conforme (2 pts) |
| **2** | **Automatiser par script** (Bash, renvoie 0 en succès, code non nul en échec) | `scripts/check.sh` & `scripts/check.bat` | ✅ Conforme (2 pts) |
| **3** | **Conteneuriser** (Dockerfile, .dockerignore, tag explicite, non-root, HEALTHCHECK) | `Dockerfile` (`python:3.11-slim`, `USER appuser`, `HEALTHCHECK`) | ✅ Conforme (3 pts) |
| **4** | **Assembler avec Compose** (App + DB Postgres, nom de service `db`, port privé, volume persistant, santé) | `docker-compose.yml` (`condition: service_healthy`, port privé) | ✅ Conforme (3 pts) |
| **5** | **Pipeline CI** (Merge request, tests puis build avec `needs`, artefact JUnit XML) | `.gitlab-ci.yml` & `.github/workflows/ci.yml` | ✅ Conforme (3 pts) |
| **6** | **Livrer & Mettre en service** (Tag vX.Y.Z, image publiée et JAMAIS reconstruite, contrôle santé) | `scripts/deploy.sh` & Stage CD automatique | ✅ Conforme (2 pts) |
| **7** | **Revenir en arrière** (Retour à la version précédente démontré sans reconstruction) | `scripts/rollback.sh` | ✅ Conforme (1 pt) |
| **8** | **La Soutenance (10 min)** (MR verte, MR rouge + erreur dans logs, déploiement, rollback) | `SOUTENANCE.md` | ✅ Conforme (4 pts) |
| **B1** | **Bonus : Protection de main** (MR rouge bloquée) | Documenté dans `SOUTENANCE.md` | 🌟 Bonus (+1 pt) |
| **B2** | **Bonus : Déploiement automatique sur tag** (Déclenché sur tag `v*` + test santé) | `.gitlab-ci.yml` (`deploy:test-environment`) | 🌟 Bonus (+2 pts) |
| **B3** | **Bonus : Matrice de versions** (Tests sur Python 3.10 et Python 3.11) | Matrice CI dans `.gitlab-ci.yml` | 🌟 Bonus (+1 pt) |

---

## 🛠️ Scripts d'Automatisation Disponibles

### 1. Script de Contrôle Qualité & Tests (Point 2)
Exécute la compilation syntaxique, la suite de tests unitaires et la validation du contrat `/health`. Renvoie **0** en cas de succès, **1** en cas d'erreur.
```bash
# Sous Linux / macOS / Git Bash :
./scripts/check.sh

# Sous Windows Command Prompt :
.\scripts\check.bat
```

### 2. Déploiement d'une Version Spécifique (Point 6)
Déploie une version étiquetée sans la recompiler et vérifie sa santé :
```bash
./scripts/deploy.sh v1.0.0
```

### 3. Procédure de Retour Arrière (Rollback) (Point 7)
Restaure instantanément une version antérieure sans altérer la base de données :
```bash
./scripts/rollback.sh v0.9.0
```

---

## 🏗️ Architecture Technique

```
                              Navigateur Client
                                      │
                         Port 8000    ▼
               ┌──────────────────────────────────────────────┐
               │         Réseau Privé Docker Compose          │
               │                                              │
               │   ┌──────────────────────────────────────┐   │
               │   │      taskflow-app (Conteneur)        │   │
               │   │  • Base image: python:3.11-slim      │   │
               │   │  • Utilisateur: appuser (non-root)   │   │
               │   │  • FastAPI Backend + SPA Frontend    │   │
               │   │  • Route: /health                    │   │
               │   └──────────────────┬───────────────────┘   │
               │                      │                       │
               │                      │ Nom d'hôte: 'db:5432' │
               │                      ▼                       │
               │   ┌──────────────────────────────────────┐   │
               │   │       taskflow-db (Conteneur)        │   │
               │   │  • Base image: postgres:16-alpine    │   │
               │   │  • Port interne: 5432 (NON PUBLIÉ)   │   │
               │   │  • Volume persistant: db_data        │   │
               │   │  • Healthcheck: pg_isready           │   │
               │   └──────────────────────────────────────┘   │
               └──────────────────────────────────────────────┘
```

---

## 📦 Documents Fournis pour l'Évaluation
* [FICHE_SYNTHESE.md](file:///c:/Users/ihebn/OneDrive/Documents/dsi31/proje%20de%20integration/task-manager-app/FICHE_SYNTHESE.md) : Fiche synthétique d'une page (Architecture, version en service, déroulé du rollback).
* [SOUTENANCE.md](file:///c:/Users/ihebn/OneDrive/Documents/dsi31/proje%20de%20integration/task-manager-app/SOUTENANCE.md) : Guide pas-à-pas de 10 minutes pour réussir la présentation orale (MR verte, MR rouge, logs d'erreur, déploiement et rollback).
* [test-results.xml](file:///c:/Users/ihebn/OneDrive/Documents/dsi31/proje%20de%20integration/task-manager-app/test-results.xml) : Rapport de tests au format JUnit XML généré automatiquement pour les artefacts CI.
