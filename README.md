# GitOps Platform

GitOps-based Kubernetes application delivery using ArgoCD.

## Project Overview

This project implements declarative application delivery on Kubernetes using Git as the source of truth and ArgoCD for continuous reconciliation.

## Objectives

- Deploy ArgoCD on Kubernetes
- Implement declarative application delivery
- Configure dev, staging, and production applications
- Demonstrate different ArgoCD sync policies
- Implement GitOps promotion from dev to staging
- Detect and respond to Kubernetes drift
- Configure deployment notifications
- Generate GitOps compliance and delivery metrics

## Repository Structure

```text
gitops-platform/
├── argocd/
├── manifests/
├── promotion/
├── drift/
├── docs/
└── README.md