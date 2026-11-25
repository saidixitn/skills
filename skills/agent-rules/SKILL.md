---
name: agent-rules
description: >-
  Use when defining operational rules for autonomous AI coding agents, enforcing
  read-before-write protocols, standardizing multi-stage database cookbooks,
  eliminating AI boilerplate/slop, or validating memory schema compliance.
---

# Autonomous Agent Operational Rules & Anti-Slop Standards Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Defining system prompts and operational guardrails for autonomous coding agents (Claude, Gemini, Antigravity).
- Enforcing the **Read-Before-Write Protocol** (inspecting existing solutions before generating code).
- Eliminating AI-generated boilerplate, puffery, and non-functional commentary.
- Formatting durable engineering knowledge into standardized guides, cookbooks, and solution records.
- Enforcing strict type hints, exception boundaries, and schema compliance across projects.

---

## 2. Hard Architectural Rules

1. **The Read-Before-Write Mandate**:
   Agents must never generate a script or database query from scratch without first checking the local repository for existing implementations. If an existing pipeline solves 80% of the task, reuse its structure rather than writing an incompatible variant.

2. **Zero AI Boilerplate & Puffery**:
   Eliminate conversational filler ("I hope this helps!", "Certainly!", "As an AI..."), generic fluff, rule-of-three marketing bullet points, and em-dash puffery. Speak directly in terse, accurate engineering facts.

3. **Deterministic Verification Over Guessing**:
   Never claim a task is completed without providing a concrete verification command (`npm test`, `python3 script.py --check`, or curl command). Evidence is required before claiming success.

4. **Zero Unhandled Exceptions**:
   All networking, database, and file I/O operations must handle failure modes explicitly with meaningful logs and exit codes.

---

## 3. The 5 Standard Content Types (Dixit Archives Standard)

Whenever documenting a new pattern, tool, or fix, format it strictly into one of 5 types:

| Content Type | Purpose | Required Structure |
| :--- | :--- | :--- |
| **Guide** | Architectural deep dive | Context, Architecture diagram, Hard rules, Step-by-step workflow |
| **Snippet** | Atomic, reusable query or function | Exact inputs, Exact outputs, Execution constraints |
| **Cookbook** | Multi-stage pipeline | Stage breakdown, Memory guards, Index prerequisites |
| **Tutorial** | Step-by-step implementation | Numbered sequence, CLI commands, End-state verification |
| **Solution** | Root cause bug resolution | Symptom, Root cause, Verified fix, Regression test |

---

## 4. Verification Checklist
- [ ] Code inspected before writing new variants.
- [ ] Zero AI pleasantries or filler words in documentation.
- [ ] All database queries include index and memory considerations.
- [ ] Executable CLI test command provided.
