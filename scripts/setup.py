import csv
import os
import subprocess
import sys

CORPUS_DIR = os.path.join(os.path.dirname(__file__), '..', 'corpus')
DATASETS_FILE = os.path.join(CORPUS_DIR, 'datasets', 'projects.csv')

def clone_project(name, language, github_url):
    target_dir = os.path.join(CORPUS_DIR, language, name)

    if os.path.exists(target_dir):
        print(f"[SKIP] {name} déjà cloné dans {target_dir}")
        return

    print(f"[CLONE] {name} ({language}) depuis {github_url}...")
    result = subprocess.run(
        ['git', 'clone', '--depth=1', github_url, target_dir],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"[OK] {name} cloné avec succès")
    else:
        print(f"[ERREUR] {name} : {result.stderr.strip()}")

def main():
    if not os.path.exists(DATASETS_FILE):
        print(f"Fichier introuvable : {DATASETS_FILE}")
        sys.exit(1)

    with open(DATASETS_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        projects = list(reader)

    print(f"=== Clonage de {len(projects)} projets ===\n")
    for project in projects:
        clone_project(project['name'], project['language'], project['github_url'])

    print("\n=== Terminé ===")

if __name__ == '__main__':
    main()