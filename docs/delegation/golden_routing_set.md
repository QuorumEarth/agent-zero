# Golden Routing Set

Canonical prompts demonstrating ideal Delegation Decision Protocol (DDP) application across all routing scenarios.

## Purpose

This document provides reference examples of correct routing behavior for Agent Zero's delegation system. Each example demonstrates:
- Clear task classification (Trivial, Specialist, Multi-domain, Ambiguous)
- Correct profile selection from the 7 available profiles
- Proper application of precedence rules when multiple profiles could match
- Expected first action (delegation or direct response)

## Profile Reference

| Profile | Domain |
|---------|--------|
| `developer` | Code, scripts, implementation, debugging, APIs, architecture |
| `researcher` | Research, analysis, fact-checking, literature review |
| `hacker` | Security, vulnerabilities, exploits, threat modeling |
| `Data_Architect` | Data plans, schemas, ETL/ELT, migration plans |
| `ProForma_Agent` | Financial modeling, runway/burn, unit economics |
| `Narrative_Agent` | Pitch content, slide copy, messaging, story arc |
| `Khosla_Advisor` | Pitch critique, deck review, 5-second test |

---

## Golden Examples

### GR-01: Trivial Task (No Delegation)

**Prompt**: "What's the current time?"

**Classification**: Trivial/direct answer

**Expected First Action**: Direct response using system datetime

**Rationale**: Simple factual query requiring no specialist expertise. Agent0 handles directly without delegation.

---

### GR-02: Specialist Task - Developer

**Prompt**: "Write a Python script that reads a CSV file and outputs the top 10 rows sorted by the 'revenue' column."

**Classification**: Specialist domain task

**Expected First Action**: Delegate to `developer` profile with reset=true

**Delegation Message Template**:
```json
{
  "profile": "developer",
  "message": "You are a Python developer. Write a script that reads a CSV file and outputs the top 10 rows sorted by the 'revenue' column. Success: script runs without errors and produces correct output. Constraints: use pandas library. Return: working Python code with usage example.",
  "reset": "true"
}
```

**Rationale**: Primary intent is code implementation. Developer profile is the clear specialist for this task.

---

### GR-03: Specialist Task - Researcher

**Prompt**: "Research the top 5 competitors in the biopesticide market for varroa mites and cite your sources."

**Classification**: Specialist domain task

**Expected First Action**: Delegate to `researcher` profile with reset=true

**Delegation Message Template**:
```json
{
  "profile": "researcher",
  "message": "You are a research analyst. Identify and analyze the top 5 competitors in the biopesticide market for varroa mites. Success: comprehensive competitive analysis with cited sources. Constraints: focus on commercial products, not academic research. Return: structured report with company names, products, and source citations.",
  "reset": "true"
}
```

**Rationale**: Primary intent is information gathering and competitive analysis. Researcher profile is the clear specialist.

---

### GR-04: Specialist Task - Hacker

**Prompt**: "Analyze this authentication flow for security vulnerabilities: [flow description]. Don't write code, just identify attack vectors."

**Classification**: Specialist domain task

**Expected First Action**: Delegate to `hacker` profile with reset=true

**Delegation Message Template**:
```json
{
  "profile": "hacker",
  "message": "You are a security analyst. Analyze this authentication flow for vulnerabilities: [flow description]. Success: comprehensive list of attack vectors with severity ratings. Constraints: assessment only, no exploit code. Return: structured vulnerability report with OWASP classifications.",
  "reset": "true"
}
```

**Rationale**: Primary intent is security assessment, not code implementation. Hacker profile is the clear specialist per Precedence Rule 2 (assessment vs execution).

---

### GR-05: Specialist Task - Data_Architect

**Prompt**: "Here's a messy CSV schema with 50 columns. Design an import plan with target schema and column mappings."

**Classification**: Specialist domain task

**Expected First Action**: Delegate to `Data_Architect` profile with reset=true

**Delegation Message Template**:
```json
{
  "profile": "Data_Architect",
  "message": "You are a data architect. Design an import plan for this CSV schema: [schema details]. Success: complete import plan with target schema, column mappings, and transformation rules. Constraints: optimize for query performance. Return: structured plan with DDL, mapping table, and transformation logic.",
  "reset": "true"
}
```

**Rationale**: Primary intent is data planning and schema design. Data_Architect profile is the clear specialist per Precedence Rule 3 (plans vs code).

---

### GR-06: Specialist Task - ProForma_Agent

**Prompt**: "Model our runway under 3 burn scenarios and flag the biggest sensitivities."

**Classification**: Specialist domain task

**Expected First Action**: Delegate to `ProForma_Agent` profile with reset=true

**Delegation Message Template**:
```json
{
  "profile": "ProForma_Agent",
  "message": "You are a financial analyst. Model runway under 3 burn scenarios (low/medium/high) and identify key sensitivities. Success: complete financial model with scenario analysis and sensitivity rankings. Constraints: use realistic assumptions. Return: Excel model with scenario comparison and sensitivity analysis.",
  "reset": "true"
}
```

**Rationale**: Primary intent is financial modeling and scenario planning. ProForma_Agent profile is the clear specialist.

---

### GR-07: Specialist Task - Narrative_Agent

**Prompt**: "Rewrite slides 3-6 of my pitch deck to be punchier and more inevitable."

**Classification**: Specialist domain task

**Expected First Action**: Delegate to `Narrative_Agent` profile with reset=true

**Delegation Message Template**:
```json
{
  "profile": "Narrative_Agent",
  "message": "You are a pitch narrative specialist. Rewrite slides 3-6 to be punchier and more inevitable. Success: rewritten slide content that passes the 5-second test. Constraints: maintain factual accuracy, use Sequoia Capital structure. Return: rewritten slide content with headlines and body copy.",
  "reset": "true"
}
```

**Rationale**: Primary intent is content creation and messaging. Narrative_Agent profile is the clear specialist per Precedence Rule 4 (writing vs critique).

---

### GR-08: Specialist Task - Khosla_Advisor

**Prompt**: "Critique my pitch deck. Be brutal. Apply the 5-second test to every slide."

**Classification**: Specialist domain task

**Expected First Action**: Delegate to `Khosla_Advisor` profile with reset=true

**Delegation Message Template**:
```json
{
  "profile": "Khosla_Advisor",
  "message": "You are a pitch deck critic using Vinod Khosla methodology. Critique this pitch deck brutally, applying the 5-second test to every slide. Success: comprehensive critique with specific improvement recommendations. Constraints: focus on investor psychology and emotional impact. Return: slide-by-slide critique with 5-second verdicts and recommended rewrites.",
  "reset": "true"
}
```

**Rationale**: Primary intent is critique and assessment. Khosla_Advisor profile is the clear specialist per Precedence Rule 4 (critique vs writing).

---

### GR-09: Multi-Domain Task (Sequential Delegation)

**Prompt**: "Prepare investor materials: tighten the narrative AND sanity-check the financial model assumptions."

**Classification**: Multi-domain task

**Expected First Action**: Delegate to `Narrative_Agent` profile with reset=true (primary intent: narrative)

**Expected Second Action**: After Narrative_Agent completes, delegate to `ProForma_Agent` with reset=true (secondary intent: financial validation)

**Rationale**: Two distinct specialist domains. Primary intent is narrative improvement (Precedence Rule 1). Sequential delegation with reset=true when switching profiles (Loop & Depth Safety).

---

### GR-10: Precedence Rule Application - Execution vs Assessment

**Prompt**: "Write code to exploit this CVE-2024-1234 vulnerability."

**Classification**: Specialist domain task with precedence conflict

**Expected First Action**: Delegate to `developer` profile with reset=true

**Rationale**: Primary intent is code implementation ("write code"), not security assessment. Developer profile wins per Precedence Rule 2 (execution vs assessment). Hacker profile would be correct for "Find vulnerabilities in this system" (assessment).

---

### GR-11: Precedence Rule Application - Plans vs Code

**Prompt**: "Design a data migration plan from MySQL to PostgreSQL, then implement the migration scripts."

**Classification**: Multi-domain task with precedence conflict

**Expected First Action**: Delegate to `Data_Architect` profile with reset=true (primary intent: plan)

**Expected Second Action**: After Data_Architect completes, delegate to `developer` with reset=true (secondary intent: implementation)

**Rationale**: Primary intent is planning ("design a plan"). Data_Architect profile wins per Precedence Rule 3 (plans vs code). Sequential delegation with reset=true when switching profiles.

---

### GR-12: Ambiguous Task (Clarification Required)

**Prompt**: "Help me with my pitch."

**Classification**: Ambiguous

**Expected First Action**: Ask ONE clarifying question to determine routing

**Clarification Question**: "I can help with your pitch. Do you need: (1) Critique of existing content (Khosla_Advisor), (2) Rewriting/tightening narrative (Narrative_Agent), or (3) Financial model review (ProForma_Agent)?"

**Rationale**: Insufficient information to determine primary intent. Clarification changes routing materially (3 different profiles possible). Ask ONE question per DDP guidance.

---

### GR-13: User Override (No Delegation)

**Prompt**: "Don't delegate. Just tell me which agent you would use for: 'Write a Python script to parse JSON logs'."

**Classification**: User override

**Expected First Action**: Direct response explaining routing logic without delegation

**Response Template**: "I would delegate this to the `developer` profile because the primary intent is code implementation. The developer profile specializes in writing/modifying/debugging code, scripts, and APIs. However, since you've asked me not to delegate, I'm explaining the routing logic instead."

**Rationale**: User explicitly forbids delegation. Comply with user override per Precedence Rule 5, but explain routing logic for transparency.

---

## Validation Criteria

For each golden example:
- **PASS**: First substantive action matches expected action (delegation to correct profile OR direct response for trivial/override cases)
- **FAIL**: Any deviation from expected action (wrong profile, no delegation when required, delegation when forbidden)

## Usage

These golden examples serve as:
1. **Training references** for understanding correct DDP application
2. **Validation baselines** for testing routing accuracy
3. **Documentation** for explaining routing decisions to users
4. **Debugging aids** for troubleshooting routing failures

For adversarial testing and edge cases, see `adversarial_delegation_suite.md`.
