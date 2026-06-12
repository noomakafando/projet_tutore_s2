import json
import os
import glob
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, 'results', 'raw')
REPORTS_DIR = os.path.join(BASE_DIR, 'results', 'reports')

def get_latest_results():
    """Récupère uniquement le fichier le plus récent par projet."""
    files = glob.glob(os.path.join(RESULTS_DIR, '*_semgrep_*.json'))
    latest = {}
    for f in files:
        filename = os.path.basename(f)
        parts = filename.split('_semgrep_')
        if len(parts) == 2:
            project = parts[0]
            timestamp = parts[1].replace('.json', '')
            if project not in latest or timestamp > latest[project][1]:
                latest[project] = (f, timestamp)
    return {project: filepath for project, (filepath, _) in latest.items()}

def load_findings(filepath):
    """Charge les findings d'un fichier JSON Semgrep."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('results', [])

def display_project_findings(project, findings):
    """Affiche les findings d'un projet de façon lisible."""
    print(f"\n{'='*60}")
    print(f"  {project.upper()} — {len(findings)} finding(s)")
    print(f"{'='*60}")

    if not findings:
        print("  Aucun finding détecté.")
        return

    # Grouper par sévérité
    by_severity = defaultdict(list)
    for f in findings:
        severity = f.get('extra', {}).get('severity', 'UNKNOWN')
        by_severity[severity].append(f)

    # Afficher par sévérité
    order = ['ERROR', 'WARNING', 'INFO', 'UNKNOWN']
    counter = 1
    for severity in order:
        if severity not in by_severity:
            continue
        for finding in by_severity[severity]:
            path = finding.get('path', 'N/A')
            # Raccourcir le chemin
            path_short = path.replace(
                os.path.join(BASE_DIR, 'corpus') + os.sep, ''
            )
            line = finding.get('start', {}).get('line', '?')
            rule = finding.get('check_id', 'N/A').split('.')[-1]
            message = finding.get('extra', {}).get('message', 'N/A')
            # Raccourcir le message
            message_short = message[:100] + '...' if len(message) > 100 else message

            severity_icon = {'ERROR': '🔴', 'WARNING': '🟡', 'INFO': '🔵'}.get(severity, '⚪')

            print(f"\n  [{counter}] {severity_icon} {severity}")
            print(f"      Fichier  : {path_short}, ligne {line}")
            print(f"      Règle    : {rule}")
            print(f"      Message  : {message_short}")
            counter += 1

def generate_summary(all_results):
    """Génère un résumé global."""
    print(f"\n{'='*60}")
    print(f"  RÉSUMÉ GLOBAL")
    print(f"{'='*60}")
    print(f"\n  {'Projet':<25} {'Findings':>8}  {'ERROR':>6}  {'WARNING':>8}  {'INFO':>5}")
    print(f"  {'-'*55}")

    total = 0
    for project, findings in sorted(all_results.items()):
        errors = sum(1 for f in findings if f.get('extra', {}).get('severity') == 'ERROR')
        warnings = sum(1 for f in findings if f.get('extra', {}).get('severity') == 'WARNING')
        infos = sum(1 for f in findings if f.get('extra', {}).get('severity') == 'INFO')
        print(f"  {project:<25} {len(findings):>8}  {errors:>6}  {warnings:>8}  {infos:>5}")
        total += len(findings)

    print(f"  {'-'*55}")
    print(f"  {'TOTAL':<25} {total:>8}")

def save_report(all_results):
    """Sauvegarde un rapport JSON structuré."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report = {}
    for project, findings in all_results.items():
        report[project] = {
            'total': len(findings),
            'by_severity': defaultdict(list),
            'findings': []
        }
        for f in findings:
            severity = f.get('extra', {}).get('severity', 'UNKNOWN')
            path = f.get('path', 'N/A').replace(BASE_DIR + os.sep, '')
            line = f.get('start', {}).get('line', '?')
            rule = f.get('check_id', 'N/A')
            message = f.get('extra', {}).get('message', 'N/A')
            report[project]['findings'].append({
                'severity': severity,
                'file': path,
                'line': line,
                'rule': rule,
                'message': message
            })
            report[project]['by_severity'][severity].append(rule)

        # Convertir defaultdict en dict pour JSON
        report[project]['by_severity'] = dict(report[project]['by_severity'])

    report_file = os.path.join(REPORTS_DIR, 'semgrep_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n  Rapport sauvegardé : {report_file}")

def main():
    print("=== Analyse des résultats Semgrep ===\n")

    latest_files = get_latest_results()
    if not latest_files:
        print("Aucun fichier de résultats trouvé dans results/raw/")
        return

    print(f"  Projets trouvés : {', '.join(sorted(latest_files.keys()))}")

    all_results = {}
    for project, filepath in sorted(latest_files.items()):
        findings = load_findings(filepath)
        all_results[project] = findings

    # Afficher les findings projet par projet
    for project, findings in sorted(all_results.items()):
        display_project_findings(project, findings)

    # Résumé global
    generate_summary(all_results)

    # Sauvegarder le rapport
    save_report(all_results)

if __name__ == '__main__':
    main()