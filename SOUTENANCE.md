# Guide de Soutenance — 10 Minutes Démonstration (4 Points)
**Module :** DevOps · Licence 3 · DSI · ISET  
**Barème Soutenance :** 4 points  
**Durée :** 10 minutes chrono + questions

---

## Chronomètre & Déroulé de la Présentation

```
┌──────────────┬──────────────────────────────────────────────────────┬──────────┐
│ Temps        │ Sujet de Démonstration                               │ Barème   │
├──────────────┼──────────────────────────────────────────────────────┼──────────┤
│ 00:00 - 02:00│ Introduction, architecture globale et route /health  │ -        │
│ 02:00 - 05:00│ DÉMO 1 : Merge Request VERTE (Pipeline réussi)       │ 1 pt     │
│ 05:00 - 07:00│ DÉMO 2 : Merge Request ROUGE (Erreur utile logs)     │ 1 pt     │
│ 07:00 - 08:30│ DÉMO 3 : Mise en service sur Tag v1.0.0              │ 1 pt     │
│ 08:30 - 10:00│ DÉMO 4 : Retour arrière (Rollback démontré)          │ 1 pt     │
└──────────────┴──────────────────────────────────────────────────────┴──────────┘
```

---

## Étape 1 : Présentation de l'Application & Architecture (2 minutes)
1. **Ouvrir le navigateur :** Montrer `http://localhost:8000` (TaskFlow en fonctionnement).
2. **Montrer la route de santé :** `http://localhost:8000/health` (Renvoie `{"status":"ok"}`).
3. **Expliquer l'architecture :**
   * Conteneur `app` (FastAPI, utilisateur non-root `appuser`, image `python:3.11-slim`).
   * Conteneur `db` (PostgreSQL 16 Alpine, port privé non publié, volume persistant `db_data`).
   * Démarrage conditionné à la santé via `service_healthy`.

---

## Étape 2 : DÉMO 1 — Merge Request VERTE (3 minutes)
*Ce que l'enseignant évalue : Pipeline complet qui passe au vert sur merge request.*

1. **Ouvrir l'interface GitLab / GitHub :**
   * Aller sur la Merge Request intitulée : `feat: add task filtering and metrics`.
2. **Montrer le pipeline vert :**
   * **Stage 1 (Test) :** Montrer la matrice de versions (Python 3.10 et Python 3.11 passent tous les deux).
   * **Artefact :** Cliquer sur le rapport de tests JUnit XML (`test-results.xml`, 8/8 tests passés).
   * **Stage 2 (Build) :** Montrer que le job de build s'est exécuté grâce à la directive `needs: [test:unit]`.
3. **Montrer la protection de branche (Bonus +1 pt) :**
   * La fusion est autorisée car le pipeline est vert.

---

## Étape 3 : DÉMO 2 — Merge Request ROUGE & Erreur Utile (2 minutes)
*Ce que l'enseignant évalue : Pipeline qui échoue, merge bloquée, et capacité à localiser la PREMIÈRE erreur utile dans le journal.*

1. **Ouvrir la Merge Request de test rouge :**
   * Exemple de branche : `fix/deliberate-test-failure`.
   * (Pour la créer facilement : modifier un test dans `test_api.py` avec `assert response.status_code == 999` ou casser une syntaxe).
2. **Montrer que la fusion est bloquée :**
   * L'interface affiche : *"Merge blocked: Pipeline must succeed before merging"* (Bonus Protection de `main`).
3. **Cliquer sur le Job échoué :**
   * Scroller dans le journal d'exécution jusqu'à la **première erreur utile** :
   ```
   FAILED test_api.py::TestTaskFlowAPI::test_01_get_all_tasks - AssertionError: Expected 200, got 500
   ```
4. **Expliquer à l'enseignant :** *"Voici la première erreur utile dans les logs : l'assertion a échoué à la ligne 18 de test_api.py, empêchant tout déploiement corrompu en production."*

---

## Étape 4 : DÉMO 3 — Mise en Service d'une Version (1.5 minutes)
*Ce que l'enseignant évalue : Tag vX.Y.Z, image publiée et JAMAIS reconstruite, contrôle de santé.*

1. **Montrer le tag Git :**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
2. **Montrer le pipeline déclenché par le tag (Bonus +2 pts) :**
   * Le job de déploiement utilise l'image pré-construite `taskflow:v1.0.0` (flag `--no-build`).
3. **Démontrer en direct sur le terminal :**
   ```bash
   ./scripts/deploy.sh v1.0.0
   ```
4. **Validation :** Le script affiche le code HTTP 200 sur `/health`.

---

## Étape 5 : DÉMO 4 — Démonstration du Retour Arrière (Rollback) (1.5 minutes)
*Ce que l'enseignant évalue : Retour à la version précédente démontré sans reconstruction.*

1. **Lancer la commande de rollback en direct devant l'enseignant :**
   ```bash
   ./scripts/rollback.sh v0.9.0
   ```
2. **Observer le journal :**
   * L'image `v1.0.0` s'arrête.
   * L'image précédente `v0.9.0` est instanciée immédiatement (aucun temps de compilation).
   * La base de données PostgreSQL reste intacte et connectée.
   * Le script vérifie la route de santé :
   ```
   ✅ ROLLBACK COMPLETED SUCCESSFULLY
   Currently running version: v0.9.0
   Healthcheck confirmed: http://localhost:8000/health (200 OK)
   ```
3. **Conclure la soutenance :** *"La solution est de nouveau opérationnelle et saine en moins de 5 secondes."*
