import csv
import os
import subprocess
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS_DIR = os.path.join(BASE_DIR, 'corpus')
DATASETS_FILE = os.path.join(CORPUS_DIR, 'datasets', 'projects.csv')
DBS_DIR = os.path.join(BASE_DIR, 'results', 'codeql-dbs')
RESULTS_DIR = os.path.join(BASE_DIR, 'results', 'codeql-dbs')

LANGUAGE_MAP = {
    'python': 'python',
    'java': 'java',
    'javascript': 'javascript'
}

SUITE_MAP = {
    'python': 'python-security-extended.qls',
    'java': 'java-security-extended.qls',
    'javascript': 'javascript-security-extended.qls'
}

def create_database(name, language, project_path, db_path):
    """Crée la base de données CodeQL pour un projet."""
    if os.path.exists(db_path):
        print(f"  [SKIP] Base de données déjà existante")
        return True

    print(f"  [DB] Création de la base de données...")
    cmd = [
        'codeql', 'database', 'create', db_path,
        f'--language={language}',
        f'--source-root={project_path}',
        '--overwrite'
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode == 0:
        print(f"  [OK] Base de données créée")
        return True
    else:
        print(f"  [ERREUR] Création échouée")
        print(f"  {result.stderr.strip()[:300]}")
        return False

def analyze_database(name, language, db_path, output_file):
    """Lance l'analyse de sécurité CodeQL."""
    suite = SUITE_MAP.get(language)
    if not suite:
        print(f"  [SKIP] Langage non supporté : {language}")
        return 0

    print(f"  [ANALYSE] Lancement des requêtes {suite}...")
    cmd = [
        'codeql', 'database', 'analyze', db_path,
        '--format=sarif-latest',
        f'--output={output_file}',
        '--ram=2048',
        suite
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode == 0 and os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        nb = len(data.get('runs', [{}])[0].get('results', []))
        print(f"  [OK] {nb} finding(s) détecté(s)")
        return nb
    else:
        print(f"  [ERREUR] Analyse échouée")
        print(f"  {result.stderr.strip()[:300]}")
        return 0

def main():
    os.makedirs(DBS_DIR, exist_ok=True)

    if not os.path.exists(DATASETS_FILE):
        print(f"Fichier introuvable : {DATASETS_FILE}")
        return

    with open(DATASETS_FILE, newline='', encoding='utf-8') as f:
        projects = list(csv.DictReader(f))

    print(f"=== Analyse CodeQL — {len(projects)} projets ===\n")

    summary = []
    for project in projects:
        name = project['name']
        language = project['language']
        codeql_lang = LANGUAGE_MAP.get(language)
        project_path = os.path.join(CORPUS_DIR, language, name)

        print(f"\n[PROJET] {name} ({language})")

        if not os.path.exists(project_path):
            print(f"  [SKIP] Dossier introuvable")
            continue

        if not codeql_lang:
            print(f"  [SKIP] Langage non supporté")
            continue

        db_path = os.path.join(DBS_DIR, f"{name}-db")
        output_file = os.path.join(RESULTS_DIR, f"{name}-results.sarif")

        # Étape 1 — Créer la base de données
        ok = create_database(name, codeql_lang, project_path, db_path)
        if not ok:
            summary.append({'project': name, 'language': language, 'findings': 'ERREUR'})
            continue

        # Étape 2 — Analyser
        nb = analyze_database(name, language, db_path, output_file)
        summary.append({'project': name, 'language': language, 'findings': nb})

    print(f"\n=== Résumé ===")
    print(f"{'Projet':<30} {'Langage':<12} {'Findings'}")
    print("-" * 55)
    for s in summary:
        print(f"{s['project']:<30} {s['language']:<12} {s['findings']}")

if __name__ == '__main__':
    main()