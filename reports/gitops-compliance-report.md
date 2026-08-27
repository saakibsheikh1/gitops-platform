\# GitOps Compliance Report



\## Environment Status



| Environment | ArgoCD Sync | Health | Automated Sync | Self-Heal |

|-------------|-------------|--------|----------------|-----------|

| Dev | Synced | Healthy | Enabled | Enabled |

| Staging | Synced | Healthy | Enabled | Disabled |

| Production | Synced | Healthy | Disabled | Disabled |



\## GitOps Controls



\- Git is the source of truth for Kubernetes manifests.

\- ArgoCD continuously monitors application state.

\- Dev uses automated synchronization and self-healing.

\- Staging uses automated synchronization without self-healing.

\- Production uses manual synchronization.

\- Image promotion uses immutable ECR image digests.

\- Trivy security scanning blocks images with HIGH/CRITICAL vulnerabilities.

\- Staging rollback was demonstrated using Git-based recovery.

\- ConfigMap and Secret drift were manually introduced and detected by ArgoCD.

\- Drift was subsequently repaired through ArgoCD synchronization.



\## Drift Detection



A Python-based drift reporting tool was implemented at:



`drift/drift-report.py`



The tool reports:



\- Application sync status

\- Application health status

\- Git revision

\- Target revision

\- Kubernetes resources associated with each application



\## Security



Container images are stored in Amazon ECR.



Promotion workflow performs a Trivy security scan before modifying the GitOps deployment manifests.



HIGH and CRITICAL vulnerabilities cause the promotion workflow to fail.



\## Rollback



A staging failure was intentionally introduced using the bad image.



Observed failure:



`CrashLoopBackOff`



Git was reverted to the known-good state and ArgoCD restored staging to:



`Synced / Healthy`



\## Compliance Conclusion



The platform demonstrates GitOps-based deployment, controlled promotion, automated security gating, drift detection, health monitoring, and Git-based rollback.

