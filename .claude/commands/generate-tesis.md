# Generate Tesis Command

Invoca el agente especializado en generación de tesis profesionales.

## Usage

```bash
/generate-tesis
```

## Agent Invocation

This command executes the `thesis_generator` agent:

- **Agent**: `thesis_generator`
- **Location**: `.claude/agents/thesis_generator.md`
- **Task**: Complete eBPF-IA project analysis and thesis plan generation

## Command Flow

```
/generate-tesis → thesis_generator agent → output/ directory
```

The agent handles all functionality including project analysis, content generation, and document creation with full APA compliance.