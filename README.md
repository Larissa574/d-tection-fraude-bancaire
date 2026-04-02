# Detection de fraude bancaire - AfriBank

Application Streamlit de detection de transactions bancaires frauduleuses, avec:
- prediction en saisie manuelle ou par upload CSV,
- tableau de bord KPI,
- page de performance interactive (seuil ajustable),
- export PDF du resultat d'analyse.

## Objectif

Ce projet permet de:
- charger un modele de machine learning deja entraine,
- scorer des transactions,
- visualiser les indicateurs metier (fraudes detectees, montants bloques, taux de fraude),
- explorer l'impact du seuil de decision sur Precision, Recall, F1 et matrice de confusion.

## Contexte Data Science

Le projet combine deux volets:
- un volet experimentation dans le notebook [détection_fraude.ipynb](détection_fraude.ipynb),
- un volet produit avec l'app Streamlit dans [my_app/acceuil.py](my_app/acceuil.py).

Objectif metier:
- detecter un maximum de fraudes (recall eleve),
- tout en limitant les faux positifs (precision elevee),
- et en gardant un modele deployable facilement.

## Dataset

- Fichier principal: [creditcard.csv](creditcard.csv)
- Volume: 284 807 transactions
- Cible: `Class` (0 = legitime, 1 = fraude)
- Variables utilisees par le modele: `Time`, `V1` a `V28`, `Amount`

Remarques:
- Le dataset est fortement desequilibre (tres peu de fraudes).
- En production cloud, le fichier brut n'est pas necessaire pour la page Performance car elle lit [models/performance_summary.json](models/performance_summary.json).

## Modeles testes

Les experimentations (notebook) ont couvert principalement:
- Logistic Regression (baseline interpretable)
- XGBoost (plusieurs variantes et reglages, avec et sans SMOTE)
- tests de preprocessing (gestion outliers, ajustement de seuil)


## Resultats (Modele Actuel)

Resultats issus de [models/performance_summary.json](models/performance_summary.json):
- Seuil par defaut: 0.41
- AUC ROC: 0.9918
- Taille evaluee: 284 807 transactions

Au seuil 0.41:
- TN: 284311
- FP: 4
- FN: 15
- TP: 477
- Precision: 0.9917
- Recall: 0.9695
- F1-score: 0.9805

Important:
- Ces metriques correspondent au setup d'evaluation present dans le projet (resume pre-calcule utilise par l'app).
- Les comparaisons de modeles et iterations detaillees sont dans [détection_fraude.ipynb](détection_fraude.ipynb).

## Stack technique

- Python 3.13
- Streamlit
- scikit-learn
- pandas / numpy
- plotly
- reportlab
- joblib

Dependances exactes dans [requirements.txt](requirements.txt).

## Structure du projet

- Application Streamlit:
	- [my_app/acceuil.py](my_app/acceuil.py)
	- [my_app/pages/1_prediction.py](my_app/pages/1_prediction.py)
	- [my_app/pages/2_Dashboard_KPI.py](my_app/pages/2_Dashboard_KPI.py)
	- [my_app/pages/3_performance.py](my_app/pages/3_performance.py)
- Modeles et artefacts:
	- [models/model_sklearn.joblib](models/model_sklearn.joblib)
	- [models/model.joblib](models/model.joblib)
	- [models/performance_summary.json](models/performance_summary.json)

## Installation locale

1. Cloner le repository.
2. Creer un environnement virtuel.
3. Installer les dependances.

Exemple Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Lancer l'application

Depuis la racine du projet:

```powershell
streamlit run my_app/acceuil.py
```

L'application s'ouvre dans le navigateur avec un menu lateral pour naviguer entre les pages.

## Lancer Le Notebook (Experimentation)

1. Ouvrir [détection_fraude.ipynb](détection_fraude.ipynb) dans VS Code ou Jupyter.
2. Selectionner le meme environnement Python que l'app.
3. Executer les cellules dans l'ordre.

Le notebook sert a:
- reproduire la comparaison des modeles,
- ajuster les hyperparametres,
- regenerer les artefacts si besoin.

## Comment utiliser l'app

### 1) Onglet Prediction

Fichier: [my_app/pages/1_prediction.py](my_app/pages/1_prediction.py)

Deux modes sont disponibles:

1. Mode 1 - Saisie manuelle
- Renseigner les variables de transaction (Time, V1...V28, Amount).
- Cliquer sur Analyser la transaction.
- Lire le statut (LEGITIME/FRAUDE), la probabilite et les metriques.

2. Mode 2 - Upload CSV
- Importer un fichier CSV contenant les colonnes attendues par le modele.
- Cliquer sur Lancer l'analyse CSV.
- Consulter les resultats et telecharger le rapport PDF.

Notes:
- Le modele charge en priorite [models/model_sklearn.joblib](models/model_sklearn.joblib), puis [models/model.joblib](models/model.joblib) en secours.
- La prediction utilise un seuil enregistre dans l'artefact du modele.

### 2) Onglet Dashboard KPI

Fichier: [my_app/pages/2_Dashboard_KPI.py](my_app/pages/2_Dashboard_KPI.py)

Ce module affiche:
- nombre total d'analyses,
- transactions analysees,
- fraudes detectees,
- montant total bloque,
- taux de fraude,
- histogrammes (fraudes par jour, transactions par mode),
- details de la derniere analyse de la session.

### 3) Onglet Performance

Fichier: [my_app/pages/3_performance.py](my_app/pages/3_performance.py)

Ce module propose:
- un slider de seuil de decision (0.00 a 1.00),
- Precision / Recall / F1 / AUC ROC,
- matrice de confusion interactive,
- courbe ROC avec point de fonctionnement.

Important:
- La page utilise [models/performance_summary.json](models/performance_summary.json).
- Le CSV brut volumineux n'est pas requis en production.

## Historique utilisateur

L'historique n'est pas global:
- il est isole par scope utilisateur,
- gere dans [my_app/history_store.py](my_app/history_store.py),
- enregistre dans le dossier `my_app/analysis_history/` a l'execution.

Cela evite que les tests d'un utilisateur apparaissent dans le dashboard d'un autre.

## Format CSV attendu (Prediction)

Le CSV doit contenir les variables du modele:
- Time, V1 a V28, Amount

La colonne `Class` n'est pas obligatoire pour la prediction (elle sert surtout a l'evaluation offline).

## Deploiement (Streamlit Community Cloud)

1. Pousser le repo sur GitHub.
2. Creer une nouvelle app sur Streamlit Cloud.
3. Selectionner le repo et la branche.
4. Definir le fichier principal: `my_app/acceuil.py`.
5. Deployer.

Si vous mettez a jour des artefacts de modele, faire un redeploy propre et vider le cache Streamlit si necessaire.


## Ameliorations possibles

- Ajouter une authentification pour une isolation utilisateur forte.
- Ajouter des tests automatises (unitaires et integration Streamlit).
- Mettre en place une pipeline CI/CD pour verifier les artefacts avant deploiement.
