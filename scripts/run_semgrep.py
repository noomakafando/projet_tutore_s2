import csv
import os
import subprocess
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS_DIR = os.path.join(BASE_DIR, 'corpus')
DATASETS_FILE = os.path.join(CORPUS_DIR, 'datasets', 'projects.csv')
RESULTS_DIR = os.path.join(BASE_DIR, 'results', 'raw')

RULESETS = ["p/owasp-top-ten", "p/cwe-top-25"]

def run_semgrep(project_name, project_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(RESULTS_DIR, f"{project_name}_semgrep_{timestamp}.json")

    print(f"\n[ANALYSE] {project_name}")
    print(f"  Dossier  : {project_path}")
    print(f"  Résultat : {output_file}")

    cmd = [
        "semgrep",
        "--config", "p/owasp-top-ten",
        "--config", "p/cwe-top-25",
        "--json",
        project_path
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    # Sauvegarder stdout directement dans le fichier
    stdout = result.stdout.strip()
    if not stdout:
        print(f"  [ERREUR] Aucune sortie de Semgrep")
        print(f"  stderr: {result.stderr.strip()[:300]}")
        return 0

    try:
        data = json.loads(stdout)
        # Sauvegarder proprement dans le fichier JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        nb_findings = len(data.get('results', []))
        print(f"  [OK] {nb_findings} finding(s) détecté(s)")
        return nb_findings
    except json.JSONDecodeError as e:
        print(f"  [ERREUR] JSON invalide : {e}")
        return 0

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    if not os.path.exists(DATASETS_FILE):
        print(f"Fichier introuvable : {DATASETS_FILE}")
        return

    with open(DATASETS_FILE, newline='', encoding='utf-8') as f:
        projects = list(csv.DictReader(f))

    print(f"=== Analyse Semgrep — {len(projects)} projets ===")
    print(f"Rulesets : {', '.join(RULESETS)}\n")

    summary = []
    for project in projects:
        name = project['name']
        language = project['language']
        project_path = os.path.join(CORPUS_DIR, language, name)

        if not os.path.exists(project_path):
            print(f"[SKIP] {name} — dossier introuvable ({project_path})")
            continue

        nb = run_semgrep(name, project_path)
        summary.append({'project': name, 'language': language, 'findings': nb})

    print("\n=== Résumé ===")
    print(f"{'Projet':<30} {'Langage':<12} {'Findings'}")
    print("-" * 55)
    for s in summary:
        print(f"{s['project']:<30} {s['language']:<12} {s['findings']}")

    total = sum(s['findings'] for s in summary)
    print("-" * 55)
    print(f"{'TOTAL':<42} {total}")

if __name__ == '__main__':
    main()