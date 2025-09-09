# Tekton Triggers - Base Installation

Official Tekton Triggers components managed declaratively by ArgoCD.

## 📁 Files

- **`release.yaml`** - Complete Tekton Triggers installation (controllers, CRDs, RBAC)
- **`interceptors.yaml`** - Core interceptors (github, cel, gitlab, bitbucket, slack)

## 🎯 Purpose

This directory contains the official Tekton Triggers installation files downloaded from:
- https://storage.googleapis.com/tekton-releases/triggers/latest/release.yaml
- https://storage.googleapis.com/tekton-releases/triggers/latest/interceptors.yaml

## 🔧 Components Installed

### Controllers
- **tekton-triggers-controller** - Manages EventListeners, TriggerBindings, TriggerTemplates
- **tekton-triggers-webhook** - Validates configurations and webhooks
- **tekton-triggers-core-interceptors** - Processes webhook events (github, cel, etc.)

### ClusterInterceptors
- **github** - GitHub webhook event processing
- **cel** - Common Expression Language filtering  
- **gitlab** - GitLab webhook events
- **bitbucket** - Bitbucket webhook events
- **slack** - Slack integration

### RBAC
- **ClusterRoles**: `tekton-triggers-eventlistener-roles`, `tekton-triggers-eventlistener-clusterroles`
- **ServiceAccounts**: Controllers and interceptors
- **ClusterRoleBindings**: Controller and webhook permissions

## 🔄 Managed by ArgoCD

- **Application**: `tekton-triggers`
- **Namespace**: `tekton-pipelines`
- **Sync Wave**: `0` (with base Tekton installation)
- **Auto Sync**: Enabled with prune and self-heal

## 🎯 Dependencies

Requires:
1. **Tekton Pipelines** (installed via separate ArgoCD app)
2. **Kubernetes** version 1.18 or later

## 🚀 Post-Installation

After installation, additional components are available:
- **EventListeners** can be created in any namespace
- **TriggerBindings** and **TriggerTemplates** for webhook automation
- **ClusterInterceptors** for event filtering and validation

## ⚠️ Version Note

These files are downloaded from the latest release. For cluster recreation, ArgoCD will reinstall these exact components ensuring consistent webhook automation functionality.