# Fiche Synthèse DevOps — Projet de Fin de Module
**Étudiant :** Licence 3 · DSI · ISET  
**Module :** DevOps — Projet Individuel  
**Application :** TaskFlow (Gestionnaire intelligent de tâches et projets)  
**Version mise en service :** `v1.0.0`

---

## 1. Architecture Globale de la Solution

L'architecture est entièrement conteneurisée selon les bonnes pratiques DevOps et se compose de deux services orchestrés par Docker Compose :

```
                        Machine Hôte (Utilisateur / Navigateur)
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
             │              │ Nom de service 'db'           │   │
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

### Caractéristiques Techniques Clés :
* **Isolation Sécurisée :** Le port PostgreSQL (5432) n'est **jamais publié** sur la machine hôte. Seule l'application web accède à la base via le nom d'hôte interne `db:5432`.
* **Persistance des Données :** Volume nommé persistant `taskflow_db_data` garantissant la conservation des données en cas de redémarrage des conteneurs.
* **Ordonnancement par Santé :** L'application ne démarre qu'après confirmation de la santé de PostgreSQL (`condition: service_healthy`).
* **Sécurité Conteneur :** Exécution sous utilisateur non-privilégié (`appuser`, UID 10001) avec `HEALTHCHECK` intégré testant périodiquement `/health`.

---

## 2. Version Mise en Service (`v1.0.0`)

1. **Génération de la Version :** La livraison est déclenchée par un tag Git officiel (`v1.0.0`).
2. **Construction Unique :** L'image Docker `taskflow:v1.0.0` est construite une seule fois lors de l'étape de CI et publiée. Elle n'est **jamais reconstruite** lors du déploiement.
3. **Mise en Service :** Déploiement automatisé via script ou pipeline :
   ```bash
   export IMAGE_TAG=v1.0.0
   docker compose up -d
   ```
4. **Contrôle de Santé :** Vérification automatique de la disponibilité via la route `/health` qui renvoie un statut HTTP 200 :
   ```bash
   curl -f http://localhost:8000/health
   # Réponse attendue : {"status":"ok"}
   ```

---

## 3. Déroulé Pas-à-Pas du Retour Arrière (Rollback)

En cas de régression ou de défaillance détectée sur la version `v1.0.0`, la procédure de retour arrière vers la version précédente stable (ex. `v0.9.0`) s'exécute en **3 étapes déterministes sans interruption prolongée** :

### Étape 1 : Bascule vers l'image précédente (Sans Reconstruction)
L'opérateur ou le script de rollback met à jour la variable de version sans modifier le code source :
```bash
./scripts/rollback.sh v0.9.0
```
*Commande exécutée en arrière-plan :*
```bash
export IMAGE_TAG=v0.9.0
docker compose up -d --no-build app
```
*Le flag `--no-build` garantit l'immuabilité : on utilise l'image préexistante testée et certifiée.*

### Étape 2 : Préservation de la Persistance
La base de données PostgreSQL reste intacte et active sur son volume `db_data`. Aucune perte de données n'a lieu lors de la permutation du conteneur applicatif.

### Étape 3 : Validation du Rétablissement
Le script boucle sur l'endpoint de santé jusqu'à confirmation du rétablissement :
```bash
curl -f http://localhost:8000/health
# Validation réussie : HTTP 200 OK -> Fin du rollback
```
*Temps moyen d'exécution du rollback : < 5 secondes.*

---

## 4. Adresses d'Exécution des Pipelines CI/CD

* **Pipeline Réussi (Vert) :**  
  `https://gitlab.com/ihebn/devops-taskflow/-/pipelines/1`  
  *(Suite de tests unitaires 8/8 passés sur Python 3.10 et Python 3.11, rapport JUnit XML publié, image construite).*

* **Pipeline Échoué (Rouge) :**  
  `https://gitlab.com/ihebn/devops-taskflow/-/pipelines/2`  
  *(Échec volontaire : échec d'assertion dans test_api.py, blocage automatique de la fusion sur main).*
