# TaskFlow — Smart Task & Project Management Platform

TaskFlow est une application web moderne de gestion de projets et de tâches structurées avec sous-tâches, décomposition assistée par IA et suivi de progression, conçue selon les standards DevOps (conteneurisation multi-niveaux, orchestration, intégration et déploiement continus).

---

## 🚀 Démarrage Rapide (En UNE Commande)

Pour compiler et démarrer l'ensemble de l'infrastructure (Application Web + Base de données PostgreSQL + Volume persistant) :

```bash
docker compose up -d --build
```

L'application est immédiatement accessible sur :
* **Interface Web :** [http://localhost:8000](http://localhost:8000)
* **Contrôle de Santé (Healthcheck) :** [http://localhost:8000/health](http://localhost:8000/health)

Pour arrêter les services :
```bash
docker compose down
```

---

## 🏗️ Architecture Technique

La solution repose sur une architecture conteneurisée isolée orchestrée par Docker Compose :

```
                        Machine Hôte (Navigateur Utilisateur)
                                       │
                                       │ Port publié: 8000:8000
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │                Réseau Privé Docker               │
             │             (taskflow_internal_net)              │
             │                                                  │
             │   ┌─────────────────────┐   pg_isready           │
             │   │    taskflow-db      │◄───────────────────┐   │
             │   │  (Postgres 16 Alpine)                    │   │
             │   │  Port 5432 PRIVÉ    │                    │   │
             │   │  Volume: db_data    │                    │   │
             │   └──────────┬──────────┘                    │   │
             │              │                               │   │
             │              │ Nom d'hôte 'db'               │   │
             │              │ (Condition: service_healthy)  │   │
             │              ▼                               │   │
             │   ┌─────────────────────┐                    │   │
             │   │    taskflow-app     │────────────────────┘   │
             │   │  (Python 3.11-slim) │                        │
             │   │  User: appuser (non-root)                    │
             │   │  Route: /health     │                        │
             │   └─────────────────────┘                        │
             └──────────────────────────────────────────────────┘
```

### Principes Clés d'Architecture :
* **Sécurité & Isolation :** Le port de la base de données (5432) est **strictement interne** au réseau Docker et n'est pas publié sur la machine hôte.
* **Persistance :** Les données PostgreSQL sont conservées dans le volume nommé persistant `taskflow_db_data`.
* **Ordonnancement par Santé :** L'application attend la disponibilité opérationnelle validée de la base de données (`depends_on: db: condition: service_healthy`).
* **Sécurité Conteneur :** Le conteneur s'exécute sous un utilisateur non-privilégié (`appuser`, UID 10001) et intègre une sonde de santé native (`HEALTHCHECK`) testant `/health`.

---

## 🛠️ Scripts d'Automatisation

Le dossier `scripts/` fournit les outils d'automatisation des opérations :

### 1. Contrôle Qualité & Tests Automatisés
Exécute la vérification syntaxique, lance la suite complète de tests unitaires via `pytest` avec génération du rapport JUnit XML, et valide la route `/health`.
```bash
# Sous Linux / macOS / Git Bash :
./scripts/check.sh

# Sous Windows :
.\scripts\check.bat
```
*Le script renvoie **0** en cas de succès et **1** en cas d'échec.*

### 2. Déploiement d'une Version Étiquetée
Déploie une version spécifique sans recompilation de l'image Docker (`--no-build`) et vérifie automatiquement la route de santé :
```bash
./scripts/deploy.sh v1.0.0
```

### 3. Procédure de Retour Arrière (Rollback)
Permet de revenir instantanément à une version antérieure sans altérer les données de la base :
```bash
./scripts/rollback.sh v0.9.0
```

---

## 🔄 Pipeline CI/CD

Le pipeline d'intégration et de livraison continues est configuré dans `.gitlab-ci.yml` (et `.github/workflows/ci.yml`) et comprend 3 étapes :

1. **Stage `test` :**
   * Exécution automatique sur chaque Merge Request et commit sur `main`.
   * Matrice de versions parallèle testant sur **Python 3.10** et **Python 3.11**.
   * Publication du rapport de tests JUnit XML en artefact (`test-results.xml`).
2. **Stage `build` :**
   * Conditionné par la réussite des tests (`needs: [test:unit]`).
   * Construction de l'image Docker avec tag explicite et publication sur le registre.
3. **Stage `deploy` :**
   * Déclenché automatiquement sur création d'un tag Git `vX.Y.Z`.
   * Déploiement en environnement de test sans reconstruction de l'image.
   * Contrôle de santé systématique via appel HTTP sur `/health`.

---

## ⚙️ Configuration & Variables d'Environnement

Un fichier modèle [.env.example](.env.example) est fourni. Pour personnaliser l'environnement :
```bash
cp .env.example .env
```

| Variable | Description | Valeur par défaut |
| :--- | :--- | :--- |
| `PORT` | Port d'écoute HTTP | `8000` |
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql://taskflow_user:taskflow_pass@db:5432/taskflow_db` |
| `IMAGE_TAG` | Tag de l'image pour déploiement/rollback | `v1.0.0` |
| `GROQ_API_KEY` | Clé d'API Groq (Optionnel pour IA 120B) | *(Optionnel)* |

---

## 📋 Liens des Livrables Officiels (Partie 4 du Sujet)

* **Dépôt Git :** [https://github.com/IhebNajjar/devops-taskflow](https://github.com/IhebNajjar/devops-taskflow)
* **Pipeline Réussi (Green) :** [Action Run #44918320736](https://github.com/IhebNajjar/devops-taskflow/actions/runs/44918320736) | [Pull Request #2](https://github.com/IhebNajjar/devops-taskflow/pull/2)
* **Pipeline en Échec (Red) :** [Action Run #44918222101](https://github.com/IhebNajjar/devops-taskflow/actions/runs/44918222101) | [Pull Request #1](https://github.com/IhebNajjar/devops-taskflow/pull/1)
* **Fiche Synthèse 1 Page :** [FICHE_SYNTHESE.md](FICHE_SYNTHESE.md) (Disponible également au format Word pour impression)
