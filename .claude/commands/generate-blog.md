# Generate Blog Command

Invoca el orquestador de blogs para crear contenido técnico completo sobre el proyecto eBPF-IA.

## Usage

```bash
/generate-blog
```

## Agent Invocation

This command executes the `blog_orchestrator` agent which coordinates all specialized blog agents:

- **Primary Agent**: `blog_orchestrator`
- **Location**: `.claude/agents/blogs/blog_orchestrator.md`
- **Task**: Coordinate specialized agents to create comprehensive blog series

## Orchestrated Agents

The blog orchestrator manages these specialist agents:

- **kubernetes_ansible_specialist**: Infrastructure and automation content
- **machine_learning_specialist**: AI/ML algorithms and cybersecurity applications  
- **devops_gitops_specialist**: CI/CD, deployment, and operational practices
- **monitoring_observability_specialist**: Metrics, logging, and system reliability

## Command Flow

```
/generate-blog → blog_orchestrator → coordinates specialist agents → comprehensive blog series
```

The orchestrator handles all coordination, content integration, and quality assurance to produce unified technical blog content covering the entire eBPF-IA platform.