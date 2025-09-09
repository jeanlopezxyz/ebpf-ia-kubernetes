# Tekton RBAC - Additional Permissions

Additional RBAC configuration for Tekton Triggers webhook automation.

## 📁 Files

- **`webhook-rbac-additional.yaml`** - ServiceAccount and bindings for ebpf-security namespace

## 🎯 Purpose

This RBAC configuration ensures the EventListener has proper permissions in the `ebpf-security` namespace where webhooks are processed.

## 🔧 Components

### ServiceAccount
- **Name**: `tekton-triggers-example-sa`
- **Namespace**: `ebpf-security`
- **Purpose**: Used by EventListener pods

### RoleBinding  
- **Scope**: Namespace `ebpf-security`
- **ClusterRole**: `tekton-triggers-eventlistener-roles`
- **Purpose**: Namespace-level permissions for webhook processing

### ClusterRoleBinding
- **Scope**: Cluster-wide
- **ClusterRole**: `tekton-triggers-eventlistener-clusterroles`  
- **Purpose**: Cluster-level permissions for cross-namespace operations

## 🔄 Managed by ArgoCD

- **Application**: `tekton-rbac-additional`
- **Sync Wave**: `1` (after base Tekton installation)
- **Auto Sync**: Enabled with prune and self-heal