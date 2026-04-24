# Feature: Dirk Agent Port

## Traceability

| Feature ID | Original PRD ID | Description |
|-----------|----------------|-------------|
| DIRK-US-01 | US-03 | Generate Claude Code agent files from Copilot agent prompts |
| DIRK-US-02 | US-04 | Run `dirk run --all` and get the same results as in Copilot |
| DIRK-US-03 | US-08 | Configure Dirk via `dirk.config.yml` the same way as before |
| DIRK-FR-01 | DK-01 | Port agent prompt to `.claude/agents/dirk.md` with YAML frontmatter |
| DIRK-FR-02 | DK-02 | Ported Dirk agent includes `bash` and `read` tools |
| DIRK-FR-03 | DK-03 | Ported agent references original `dirk.config.yml` and `repos.yml` |
| DIRK-FR-04 | DK-04 | Ported agent invokes `dirk run --all` via bash tool |
| DIRK-FR-08 | DK-08 | CLI verb examples remain accessible |

**Product Vision:** [docs/product-vision.md](../product-vision.md)
**Original PRD:** [docs/copilot-to-claude-code-porting-framework.md](../copilot-to-claude-code-porting-framework.md)

---

## 1. Feature Overview

**Feature Name:** Dirk Agent Port
**ID Prefix:** DIRK
**Summary:** Port the Dirk agent prompt from `.github/agents/dirk.md` (Copilot format) to `.claude/agents/dirk.md` (Claude Code format). This is the primary artifact of the porting process — a Claude Code agent that can orchestrate the full Dirk pipeline.
**Dependencies:** Foundation (needs the mapping reference for conversion rules)
**Priority:** Must

---

## 2. User Stories

| ID | As a... | I want to... | So that... | Priority |
|----|---------|-------------|-----------|----------|
| DIRK-US-01 | Framework User | To generate Claude Code agent files from Copilot agent prompts | The ported agents work natively in Claude Code | Must |
| DIRK-US-02 | End User | To run `dirk run --all` and get the same results as in Copilot | The ported functionality is correct | Must |
| DIRK-US-03 | End User | To configure Dirk via `dirk.config.yml` the same way as before | My existing config works unchanged | Must |

---

## 3. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| DIRK-FR-01 | Dirk agent prompt from `.github/agents/dirk.md` shall be ported to `.claude/agents/dirk.md` with YAML frontmatter | Must |
| DIRK-FR-02 | Ported Dirk agent shall include `bash` and `read` tools in its frontmatter to invoke the Python CLI and read files | Must |
| DIRK-FR-03 | Ported Dirk agent shall reference the original `dirk.config.yml` and `repos.yml` for configuration | Must |
| DIRK-FR-04 | Ported Dirk agent shall invoke `dirk run --all` via bash tool to execute the pipeline | Must |
| DIRK-FR-08 | CLI verb examples from the original agent prompt (`dirk concept add`, `dirk link add`) shall remain accessible | Should |

---

## 4. UI / Interaction Design

The Dirk agent is invoked from the Claude Code CLI. The user runs an agent that loads the Dirk prompt and executes the pipeline:

1. User invokes Claude Code with the Dirk agent: `claude` (agent loaded via configuration)
2. Agent reads `dirk.config.yml` and `repos.yml` from the source repo
3. Agent runs `dirk run --all` via bash
4. Agent inspects the findings output and reports results back to the user
5. Agent follows the operating loop defined in the prompt

Agent YAML frontmatter structure:

```yaml
---
name: dirk
description: Holistic research agent that surfaces the fundamental interconnectedness of repositories
tools:
  - bash
  - read
  - grep
  - glob
---
```

---

## 5. Implementation Tasks

### Phase 1: Port the Agent Prompt
- [ ] Read the original `.github/agents/dirk.md` from the source repo
- [ ] Create `.claude/agents/dirk.md` with YAML frontmatter
- [ ] Adapt tool references (replace Copilot-specific verbs with Claude Code equivalents)
- [ ] Update the operating loop to reference the correct paths for config files
- [ ] Update the output contract to reflect Claude Code interaction patterns

### Phase 2: Verify Agent Load
- [ ] Verify YAML frontmatter is valid
- [ ] Verify agent file loads without Markdown parsing errors
- [ ] Verify all referenced paths exist in the project structure

---

## 6. Testing Strategy

| Level | Scope | Approach |
|-------|-------|----------|
| Syntax validation | Agent file | Verify YAML frontmatter parses correctly |
| Path validation | File references | Verify all referenced paths (config, repos, output dirs) exist |
| Load test | Agent invocation | Attempt to load agent; catch any errors |

Key test scenarios:
1. YAML frontmatter has valid `name`, `description`, `tools` fields
2. YAML frontmatter has no unknown fields that cause parse errors
3. All file paths in the agent prompt resolve to actual files

---

## 7. Acceptance Criteria

1. `.claude/agents/dirk.md` exists with valid YAML frontmatter
2. YAML frontmatter includes `tools: [bash, read, grep, glob]`
3. Agent prompt references `dirk.config.yml` and `repos.yml` from the source repo
4. Agent operating loop calls `dirk run --all` via bash
5. Agent loads without syntax errors when invoked

---

## 8. Open Questions

| # | Question | Default Assumption |
|---|----------|--------------------|
| 1 | Should the agent include `edit` and `create` tools (as the original Copilot agent had)? | Include only `bash`, `read`, `grep`, `glob` for phase 1; add `edit`/`create` only if needed for findings generation |
| 2 | How should the agent reference config files from the source repo? | Use relative path `repos/ai-etcetera/dirk.config.yml` |
