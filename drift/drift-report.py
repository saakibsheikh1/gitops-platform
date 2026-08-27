import json
import subprocess
from datetime import datetime


def run_kubectl(args):
    result = subprocess.run(
        ["kubectl"] + args,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None, result.stderr.strip()

    return result.stdout.strip(), None


def get_applications():
    output, error = run_kubectl(
        ["get", "applications", "-n", "argocd", "-o", "json"]
    )

    if error:
        print(f"ERROR: {error}")
        return []

    data = json.loads(output)
    return data.get("items", [])


def get_resources(namespace):
    output, error = run_kubectl(
        ["get", "all", "-n", namespace, "-o", "json"]
    )

    if error:
        return []

    data = json.loads(output)

    resources = []

    for item in data.get("items", []):
        resources.append({
            "kind": item.get("kind"),
            "name": item.get("metadata", {}).get("name"),
            "namespace": item.get("metadata", {}).get("namespace"),
        })

    return resources


def main():
    timestamp = datetime.now().astimezone().isoformat()

    applications = get_applications()

    report = {
        "generated_at": timestamp,
        "summary": {
            "total_applications": len(applications),
            "healthy": 0,
            "degraded": 0,
            "progressing": 0,
            "unknown": 0,
        },
        "applications": [],
    }

    for app in applications:
        name = app["metadata"]["name"]

        spec = app.get("spec", {})
        status = app.get("status", {})

        namespace = spec.get("destination", {}).get("namespace", "")
        repo = spec.get("source", {}).get("repoURL", "")
        path = spec.get("source", {}).get("path", "")
        target_revision = spec.get("source", {}).get("targetRevision", "")

        sync_status = status.get("sync", {}).get("status", "Unknown")
        health_status = status.get("health", {}).get("status", "Unknown")
        revision = status.get("sync", {}).get("revision", "")

        if health_status == "Healthy":
            report["summary"]["healthy"] += 1
        elif health_status == "Degraded":
            report["summary"]["degraded"] += 1
        elif health_status == "Progressing":
            report["summary"]["progressing"] += 1
        else:
            report["summary"]["unknown"] += 1

        resources = get_resources(namespace)

        report["applications"].append({
            "name": name,
            "namespace": namespace,
            "sync_status": sync_status,
            "health_status": health_status,
            "git_revision": revision,
            "target_revision": target_revision,
            "repository": repo,
            "manifest_path": path,
            "resources": resources,
        })

    with open("drift/drift-report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("=" * 70)
    print("GITOPS DRIFT REPORT")
    print("=" * 70)
    print(f"Generated: {timestamp}")
    print()
    print(f"Applications : {report['summary']['total_applications']}")
    print(f"Healthy      : {report['summary']['healthy']}")
    print(f"Degraded     : {report['summary']['degraded']}")
    print(f"Progressing  : {report['summary']['progressing']}")
    print(f"Unknown      : {report['summary']['unknown']}")
    print()

    for app in report["applications"]:
        print("-" * 70)
        print(f"Application : {app['name']}")
        print(f"Namespace   : {app['namespace']}")
        print(f"Sync        : {app['sync_status']}")
        print(f"Health      : {app['health_status']}")
        print(f"Revision    : {app['git_revision']}")
        print(f"Git target  : {app['target_revision']}")
        print(f"Manifest    : {app['manifest_path']}")

        print("Resources:")

        for resource in app["resources"]:
            print(
                f"  - {resource['kind']}/"
                f"{resource['name']}"
            )

    print("=" * 70)
    print("Report saved to drift/drift-report.json")
    print("=" * 70)


if __name__ == "__main__":
    main()