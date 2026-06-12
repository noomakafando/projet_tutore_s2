# Projet Tutoré S2 — Détection Automatisée de Vulnérabilités

## Description du projet

Ce projet tutoré porte sur l’analyse statique de sécurité appliquée à des projets open source.

L’objectif est de détecter automatiquement des vulnérabilités logicielles à l’aide d’outils modernes d’analyse statique comme Semgrep et CodeQL.

Le projet est réalisé dans le cadre du Master 1 Cybersécurité à l’Université Joseph Ki-Zerbo.

---

# Pourquoi ce projet existe ?

Les vulnérabilités logicielles représentent aujourd’hui l’une des principales causes de cyberattaques.

L’analyse statique permet d’identifier ces vulnérabilités directement dans le code source avant la mise en production.

Ce projet vise donc à :
- analyser des projets open source réels,
- détecter des failles de sécurité,
- comparer plusieurs outils SAST,
- comprendre les limites de ces outils,
- proposer des règles personnalisées.

---

# Objectifs

- Déployer Semgrep et CodeQL
- Scanner des projets open source
- Détecter des vulnérabilités de type :
  - SQL Injection
  - XSS
  - Hardcoded Secrets
  - Command Injection
- Comparer les résultats des outils
- Produire un rapport scientifique et technique

---

# Technologies utilisées

- Python
- Git / GitHub
- Semgrep
- CodeQL
- JSON
- YAML
- Markdown

---

# Installation

## 1. Cloner le projet

```bash
git clone https://github.com/noomakafando/projet_tutore_s2.git

## 2. Installé semgrep
dans .../projet_tutore
pip install semgrep
semgrep --version

---

### Structure du projet 

.
├── corpus/
│   ├── datasets/
│   ├── java/
│   ├── javascript/
│   └── python/
│
├── docs/
│   ├── articles/
│   └── soutenance/
│
├── scripts/
│
└── .gitignore

##Télécharger les corpus(differents projets git à analysé)
##les différents projet seront classés automatiquement dans corpus, respectivement, python, django, ....
cd scripts
python run_semgrep.py

## lancer l'analyseur semgrep

cd scripts
python run_semgrep.py

##Analyser les resultat obtenu par semgrep

cd scripts
python analyze.py