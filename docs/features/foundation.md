# Feature: Foundation

## Traceability

| Feature ID | Original PRD ID | Description |
|-----------|----------------|-------------|
| FOUND-US-01 | US-01 | Provide source repo path and analyze its structure |
| FOUND-US-02 | US-02 | Have a mapping of each Copilot component to its Claude Code equivalent |
| FOUND-US-06 | US-06 | Reuse the porting process across multiple repos |
| FOUND-FR-01 | PF-01 | Accept source directory via interactive prompt |
| FOUND-FR-02 | PF-02 | Analyze source directory and produce component inventory |
| FOUND-FR-03 | PF-03 | Classify each component by type |
| FOUND-FR-04 | PF-04 | Apply Copilot-to-Claude Code mapping reference |
| FOUND-FR-05 | PF-05 | Produce a porting plan |
| FOUND-FR-10 | PF-10 | Validate ported components by running the original test suite |
| FOUND-FR-11 | PF-11 | Document all porting decisions and gaps/limitations |

**Product Vision:** [docs/product-vision.md](../product-vision.md)
**Original PRD:** [docs/copilot-to-claude-code-porting-framework.md](../copilot-to-claude-code-porting-framework.md)

---

## 1. Feature Overview

**Feature Name:** Foundation
**ID Prefix:** FOUND
**Summary:** The reusable core of the porting framework — the process definitions, templates, and mapping reference that are used regardless of which Copilot repository is being ported. This feature is what makes the framework a "framework" rather than a one-off porting effort.
**Dependencies:** None
**Priority:** Must

---

## 2. User Stories

| ID | As a... | I want to... | So that... | Priority |
|----|---------|-------------|-----------|----------|
| FOUND-US-01 | Framework User | To provide a source repo path and have the framework analyze its structure | I understand what components exist and what needs porting | Must |
| FOUND-US-02 | Framework User | To have a mapping of each Copilot component to its Claude Code equivalent | I know exactly what to create for each source artifact | Must |
| FOUND-US-06 | Framework Maintainer | To reuse the porting process across multiple repos | I don't reinvent the mapping each time | Must |

---

## 3. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FOUND-FR-01 | Framework shall accept a source directory path via interactive prompt at project start | Must |
| FOUND-FR-02 | Framework shall analyze the source directory structure and produce a component inventory | Must |
| FOUND-FR-03 | Framework shall classify each component by type (agent prompt, workflow, config, CLI tool, test, docs, bootstrap) | Must |
| FOUND-FR-04 | Framework shall apply the Copilot-to-Claude Code mapping reference to each component | Must |
| FOUND-FR-05 | Framework shall produce a porting plan listing all artifacts to create or modify | Must |
| FOUND-FR-10 | Framework shall validate ported components by running the original test suite | Must |
| FOUND-FR-11 | Framework shall document all porting decisions and any gaps/limitations | Should |

---

## 4. UI / Interaction Design

The foundation is a **process**, not a UI. The interaction is:

1. Claude Code agent prompts the user for the source directory path
2. Agent analyzes the directory and reports the component inventory as a structured table
3. Agent presents the mapping and porting plan for user confirmation
4. Agent executes the porting phases, reporting progress at each step

All interaction through the Claude Code chat interface.

---

## 5. Implementation Tasks

### Phase 1: Framework Definition
- [x] Draft and finalize the PRD
- [x] Decompose into Product Vision + Features (this document)
- [ ] Define the component inventory template (what to capture for each source repo)
- [ ] Define the porting plan template (ordered checklist of artifacts to create)
- [ ] Document the Copilot-to-Claude Code mapping reference (see product-vision.md §5.4)
- [ ] Generate the framework agents (Analyzer, Mapper, Generator, Validator) via Agent Forge

---

## 6. Testing Strategy

| Level | Scope | Approach |
|-------|-------|----------|
| Process validation | Framework usability | Run through the framework with a test repo; verify all phases are clear and actionable |
| Template verification | Component inventory | Fill in template for Dirk repo; verify no fields are ambiguous |

Key test scenarios:
1. Source directory is readable and contains the expected structure
2. Component inventory accurately identifies all component types
3. Porting plan correctly maps all components to Claude Code equivalents

---

## 7. Acceptance Criteria

1. Component inventory template exists, is documented, and can be filled in for any Copilot repo
2. Porting plan template exists and produces an ordered checklist of artifacts to create
3. Copilot-to-Claude Code mapping reference is documented in the product vision
4. Framework agents (Analyzer, Mapper, Generator, Validator) are generated via Agent Forge
5. A dry-run walkthrough of the framework using a test repo succeeds

---

## 8. Open Questions

| # | Question | Default Assumption |
|---|----------|--------------------|
| 1 | Should the framework agents be defined as individual agents or as a single orchestrator? | Start with a single orchestrator agent that runs all phases; split if complexity grows |
