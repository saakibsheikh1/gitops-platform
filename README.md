# GitOps Platform

A production-oriented GitOps deployment platform using **Kubernetes, Argo CD, GitHub Actions, AWS ECR, and Trivy**.

This project demonstrates automated application synchronization, immutable container image promotion, security scanning, controlled staging promotion, rollback/recovery, configuration drift detection, drift remediation, and operational reporting across **Dev, Staging, and Production** environments.

---

## Architecture

```text
                    ┌──────────────────────┐
                    │      Developer       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       GitHub         │
                    │   gitops-platform    │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
       GitHub Actions                    Argo CD
       CI/CD Pipeline                GitOps Controller
                │                             │
                ▼                             │
          AWS ECR Images                      │
                │                             │
                └──────────────┬──────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Kubernetes      │
                    │                      │
                    │  ┌──────┐ ┌───────┐ │
                    │  │ Dev  │ │Staging│ │
                    │  └──────┘ └───────┘ │
                    │                      │
                    │     Production       │
                    └──────────────────────┘
Technology Stack
Technology	Purpose
GitHub	Git repository and GitOps source of truth
GitHub Actions	CI/CD and image promotion automation
AWS ECR	Container image registry
Kubernetes	Container orchestration
Argo CD	GitOps continuous delivery and reconciliation
Trivy	Container image vulnerability scanning
Python	Drift detection and report generation
YAML	Kubernetes and Argo CD configuration
Environments

The platform manages three Kubernetes environments:

Dev
 ↓
Staging
 ↓
Production

Each environment has its own Argo CD Application and Kubernetes manifests.

Dev
Argo CD Application: dev-app
Namespace: dev
Manifest path: manifests/dev
Staging
Argo CD Application: staging-app
Namespace: staging
Manifest path: manifests/staging
Production
Argo CD Application: production-app
Namespace: production
Manifest path: manifests/production
Repository Structure
gitops-platform/
│
├── .github/
│   └── workflows/
│       └── promote-image.yml
│
├── manifests/
│   ├── dev/
│   │   ├── configmap.yaml
│   │   ├── deployment.yaml
│   │   ├── secret.yaml
│   │   └── service.yaml
│   │
│   ├── staging/
│   │   ├── configmap.yaml
│   │   ├── deployment.yaml
│   │   ├── secret.yaml
│   │   └── service.yaml
│   │
│   └── production/
│       ├── deployment.yaml
│       └── service.yaml
│
├── drift/
│   ├── drift-report.py
│   └── drift-report.json
│
├── reports/
│   ├── gitops-compliance-report.md
│   └── delivery-metrics.md
│
└── README.md
GitOps Workflow

The repository acts as the desired state for the Kubernetes environments.

The workflow is:

Container Image
      │
      ▼
    AWS ECR
      │
      ▼
GitHub Actions
      │
      ├── Resolve immutable image digest
      │
      ├── Run Trivy security scan
      │
      ├── Update GitOps manifest
      │
      └── Create promotion PR
              │
              ▼
          GitHub
              │
              ▼
           Argo CD
              │
              ▼
        Kubernetes
              │
       ┌──────┼──────┐
       ▼      ▼      ▼
      Dev  Staging Production

Argo CD continuously reconciles Kubernetes with the desired state stored in Git.

Image Promotion

The image promotion workflow is implemented in:

.github/workflows/promote-image.yml

The workflow performs the following operations:

Checks out the repository.
Configures AWS credentials.
Determines the image tag.
Logs in to Amazon ECR.
Resolves the image SHA256 digest.
Runs a Trivy security scan.
Updates the appropriate GitOps manifest.
Commits the promotion.
Creates a staging promotion pull request.
Completes the workflow after successful execution.

Images are referenced using immutable SHA256 digests rather than relying only on mutable tags.

Example:

image: 495278513365.dkr.ecr.ap-south-1.amazonaws.com/cicd-rollback-pipeline@sha256:<digest>
Security Scanning

Trivy is integrated into the image promotion workflow.

The security stage prevents an image from progressing when the configured vulnerability policy fails.

The project intentionally tested a bad image:

1.2.0-bad

This provided evidence that the security gate can fail a promotion instead of allowing an unapproved image to continue through the deployment process.

Staging Promotion

Staging promotion is performed through Git.

The workflow creates a promotion branch and pull request rather than directly modifying the main branch.

Example promotion branch:

promotion/staging-1.1.0-33068402507

Example pull request:

Promote 1.1.0 to staging

The promotion PR is used as a controlled GitOps change before the staging environment is updated.

Rollback Demonstration

Rollback behavior was intentionally tested.

A staging deployment was modified to intentionally fail:

echo 'Intentional rollback test failure'
exit 1

The resulting Kubernetes pods entered:

CrashLoopBackOff

Argo CD reported the application as:

Synced / Progressing

The Git change was then reverted.

After Argo CD reconciliation, the staging application returned to:

Synced / Healthy

and the staging pods returned to:

Running

This demonstrated a Git-driven rollback and recovery process.

Drift Detection

The project includes a Python-based drift reporting tool:

drift/drift-report.py

The generated report is:

drift/drift-report.json

The tool reports Argo CD application state including:

Application name
Namespace
Sync status
Health status
Git revision
Target revision
Repository
Manifest path
Kubernetes resources

Example report summary:

{
  "total_applications": 3,
  "healthy": 2,
  "degraded": 1,
  "progressing": 0,
  "unknown": 0
}

The degraded state observed during testing was caused by an intentionally introduced Dev image configuration problem and was subsequently recovered.

Configuration Drift Test

Configuration drift was intentionally introduced into Kubernetes resources.

For example, the desired Git configuration contained:

data:
  application: gitops-platform
  environment: staging
  version: "1.0"

A live Kubernetes ConfigMap was intentionally modified to:

environment: DRIFTED

Argo CD detected the difference and reported:

OutOfSync

The Git-defined configuration was then restored through Argo CD synchronization.

The same workflow was used to test Secret drift.

This demonstrates the GitOps reconciliation principle:

Git desired state
       │
       ▼
   Argo CD
       │
       ▼
Kubernetes actual state
       │
       ├── Match → Synced
       │
       └── Difference → OutOfSync
                         │
                         ▼
                    Reconciliation
Argo CD

The following Applications were created:

dev-app
staging-app
production-app

Final validation showed:

NAME             SYNC STATUS   HEALTH STATUS
dev-app          Synced        Healthy
production-app   Synced        Healthy
staging-app      Synced        Healthy

Argo CD provides:

Git synchronization
Health monitoring
Resource visualization
Application history
Rollback capability
Drift detection
Automatic reconciliation
Final Kubernetes Validation
Dev
3/3 pods Running
Staging
2/2 pods Running

The staging pods had one historical restart each because of the intentional rollback/failure test, but both were Running and Ready during final validation.

Production
2/2 pods Running

Final application state:

Dev         → Synced / Healthy
Staging     → Synced / Healthy
Production  → Synced / Healthy
Argo CD Notifications

Argo CD Notifications was configured with notification templates/triggers for application events such as:

Sync success
Sync failure
Degraded health

The Notifications controller was running during final setup.

External Slack/email delivery was not claimed as validated because no external notification destination credential was configured and tested.

Operational Reports

The project includes:

reports/gitops-compliance-report.md
reports/delivery-metrics.md

These documents provide project-level compliance and delivery information.

The drift tooling also produces:

drift/drift-report.json
Verification Commands

Check all Argo CD applications:

kubectl get applications -n argocd

Check Dev:

kubectl get pods -n dev

Check Staging:

kubectl get pods -n staging

Check Production:

kubectl get pods -n production

Check deployment status:

kubectl get deployments -A

Check Git status:

git status

Check recent commits:

git log -5 --oneline

Check drift and report files:

git ls-files drift reports
Accessing the Application

The deployed application is an NGINX workload.

The Kubernetes services can be accessed locally using port forwarding.

Dev
kubectl port-forward svc/dev-nginx-service -n dev 8081:80

Open:

http://localhost:8081
Staging
kubectl port-forward svc/staging-nginx-service -n staging 8082:80

Open:

http://localhost:8082
Production
kubectl port-forward svc/production-nginx-service -n production 8083:80

Open:

http://localhost:8083
Key GitOps Principles Demonstrated
1. Git as the Source of Truth

Kubernetes desired state is stored and versioned in Git.

2. Immutable Deployments

Container images are promoted using SHA256 image digests.

3. Automated Reconciliation

Argo CD continuously compares Git state with Kubernetes state.

4. Controlled Promotion

Staging promotion is performed through a GitHub pull request.

5. Security Before Promotion

Trivy scanning occurs before an image is promoted.

6. Declarative Rollback

Rollback is performed by reverting the Git change and allowing Argo CD to reconcile the desired state.

7. Drift Detection

Unauthorized live changes are detected by Argo CD and can be corrected from Git.

Project Outcomes

The project successfully demonstrates:

GitOps-based Kubernetes deployment
Multi-environment application management
Argo CD synchronization
Automated container image promotion
AWS ECR integration
Immutable image digest deployment
Trivy security scanning
Controlled staging promotion
Intentional failure testing
Git-based rollback and recovery
Configuration drift detection
Drift remediation
Automated drift reporting
GitOps compliance reporting
Delivery metrics
Argo CD notification configuration
Evidence

The project was validated using:

Argo CD application dashboard
GitHub Actions promotion workflow
Successful ECR image digest resolution
Successful Trivy security scan
Staging promotion pull request
Intentional staging failure
CrashLoopBackOff failure state
Git-based rollback
Final Argo CD Healthy/Synced state
Kubernetes pod validation
Configuration drift detection
Drift remediation
Git repository status and commit history
Final Git Repository State

The final repository was verified with:

git status

On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean

Latest project completion commit:

41d37ca Complete GitOps compliance and delivery reports

Tracked reporting and drift files include:

drift/drift-report.json
drift/drift-report.py
reports/delivery-metrics.md
reports/gitops-compliance-report.md
Final Status
┌──────────────────────────────────────────┐
│          GITOPS PROJECT STATUS            │
├──────────────────────────────────────────┤
│ Dev                 Synced / Healthy      │
│ Staging             Synced / Healthy      │
│ Production          Synced / Healthy      │
│ Image Promotion     Completed             │
│ Trivy Security      Tested                │
│ Rollback            Tested                │
│ Drift Detection     Tested                │
│ Drift Remediation   Tested                │
│ Reporting           Completed             │
│ Git Repository      Clean / Pushed        │
└──────────────────────────────────────────┘
Conclusion

This project demonstrates an end-to-end GitOps delivery model where application configuration is maintained in Git, container images are securely promoted through CI/CD, Argo CD reconciles Kubernetes environments, failures can be recovered through Git-based rollback, and configuration drift can be detected and remediated.

The implementation provides a practical foundation for secure, auditable and repeatable Kubernetes application delivery.

Repository

GitHub:

https://github.com/saakibsheikh1/gitops-platform


**That's the complete file.** Save it as:

```text
README.md

Then run:

git add README.md
git commit -m "Add final project README"
git push
