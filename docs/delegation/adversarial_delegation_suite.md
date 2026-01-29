# Adversarial Delegation Suite

Pressure tests designed to validate Agent Zero's delegation system under adversarial conditions, edge cases, and ambiguous phrasing.

## Purpose

This suite tests routing robustness beyond golden examples by:
- Testing common failure modes (wrong profile selection, no delegation when required)
- Validating precedence rule application under ambiguous conditions
- Testing user override compliance
- Testing multi-domain sequential delegation
- Testing subordinate delegation chains
- Testing resistance to "sneaky phrasing" that might confuse routing

## Pass/Fail Rule

**PASS** = The first substantive action is routing to the expected profile via `call_subordinate` (unless prompt explicitly forbids delegation).

**FAIL** = Any deviation from expected first action:
- Wrong profile selected
- No delegation when delegation is required
- Delegation when user forbids it
- Incorrect precedence rule application

---

## Core Adversarial Tests

### DP-01: Speed Pressure + Code Task

**Prompt**: "Quick: write a Python script that parses 50k JSON logs and outputs a CSV summary."

**Expected First Route**: `developer`

**Common Failure Mode**: agent0 answers conceptually without delegating ("speed pressure" triggers direct response)

**Why This Tests Routing**: Tests whether urgency language ("Quick:") overrides correct specialist routing. The task clearly requires code implementation (developer domain) regardless of urgency.

**Validation**: First action must be `call_subordinate` with `profile="developer"` and `reset="true"`.

---

### DP-02: Anti-Code Instruction + Research Task

**Prompt**: "I don't need code. Compare the top 5 competitors in biopesticides for varroa and cite sources."

**Expected First Route**: `researcher`

**Common Failure Mode**: Routed to developer because "top 5" or structured output sounds technical

**Why This Tests Routing**: Tests whether explicit anti-code instruction ("I don't need code") correctly routes to researcher despite structured output requirements. Primary intent is competitive research, not code.

**Validation**: First action must be `call_subordinate` with `profile="researcher"` and `reset="true"`.

---

### DP-03: Assessment vs Execution (Precedence Rule 2)

**Prompt**: "Find vulnerabilities in this auth flow description: [paste]. Don't write code, just attack paths."

**Expected First Route**: `hacker`

**Common Failure Mode**: Routed to developer because "auth flow" sounds technical

**Why This Tests Routing**: Tests Precedence Rule 2 (assessment vs execution). Primary intent is security assessment ("find vulnerabilities", "attack paths"), not code implementation. Explicit anti-code instruction reinforces assessment intent.

**Validation**: First action must be `call_subordinate` with `profile="hacker"` and `reset="true"`.

---

### DP-04: Plan vs Execution (Precedence Rule 3)

**Prompt**: "Here's a messy CSV schema. Design an import plan + target schema + mapping."

**Expected First Route**: `Data_Architect`

**Common Failure Mode**: Routed to researcher (summarizes instead of creating mapping/plan)

**Why This Tests Routing**: Tests Precedence Rule 3 (plans vs code). Primary intent is data planning ("design an import plan", "target schema", "mapping"), not research or implementation. Data_Architect specializes in schema design and ETL planning.

**Validation**: First action must be `call_subordinate` with `profile="Data_Architect"` and `reset="true"`.

---

### DP-05: Critique vs Writing (Precedence Rule 4)

**Prompt**: "Critique my pitch deck. Be brutal. Apply the 5-second test."

**Expected First Route**: `Khosla_Advisor`

**Common Failure Mode**: Routed to Narrative_Agent (starts rewriting instead of critiquing)

**Why This Tests Routing**: Tests Precedence Rule 4 (critique vs writing). Primary intent is assessment ("critique", "be brutal"), not content creation. Khosla_Advisor specializes in pitch deck critique using Vinod Khosla methodology.

**Validation**: First action must be `call_subordinate` with `profile="Khosla_Advisor"` and `reset="true"`.

---

### DP-06: Writing vs Critique (Precedence Rule 4 Inverse)

**Prompt**: "Rewrite slide 3–6 to be punchier and more inevitable."

**Expected First Route**: `Narrative_Agent`

**Common Failure Mode**: Routed to Khosla_Advisor (gives critique but no rewrite)

**Why This Tests Routing**: Tests Precedence Rule 4 inverse. Primary intent is content creation ("rewrite"), not critique. Narrative_Agent specializes in pitch narrative and slide copy.

**Validation**: First action must be `call_subordinate` with `profile="Narrative_Agent"` and `reset="true"`.

---

### DP-07: Financial Modeling (Specialist Domain)

**Prompt**: "Model runway under 3 burn scenarios and flag the biggest sensitivities."

**Expected First Route**: `ProForma_Agent`

**Common Failure Mode**: Routed to researcher (explains conceptually instead of building model)

**Why This Tests Routing**: Tests specialist domain recognition for financial modeling. Primary intent is quantitative financial analysis ("model runway", "burn scenarios", "sensitivities"), not research. ProForma_Agent specializes in financial modeling and scenario planning.

**Validation**: First action must be `call_subordinate` with `profile="ProForma_Agent"` and `reset="true"`.

---

### DP-08: Security Code vs Security Assessment

**Prompt**: "Write a security scanner for our API and include OWASP checks."

**Expected First Route**: `developer`

**Common Failure Mode**: Routed to hacker (confuses 'security' keyword with 'security assessment')

**Why This Tests Routing**: Tests Precedence Rule 2 (execution vs assessment) with security context. Primary intent is code implementation ("write a security scanner"), not vulnerability assessment. Developer profile handles security tool implementation; hacker profile handles security assessments.

**Validation**: First action must be `call_subordinate` with `profile="developer"` and `reset="true"`.

---

### DP-09: Research Then Plan (Multi-Domain Sequential)

**Prompt**: "Research the best ETL approach for importing HubSpot + Salesforce into a warehouse, then create the import plan."

**Expected First Route**: `Data_Architect`

**Common Failure Mode**: Routed to researcher and stops before creating plan

**Why This Tests Routing**: Tests Precedence Rule 1 (primary intent wins) with multi-domain task. Primary intent is data planning ("create the import plan"), not research. Research is contextual input for the plan. Data_Architect can conduct research as part of planning process.

**Validation**: First action must be `call_subordinate` with `profile="Data_Architect"` and `reset="true"`.

---

### DP-10: Multi-Domain Sequential Delegation

**Prompt**: "Prepare investor materials: tighten narrative AND sanity-check financial model assumptions."

**Expected First Route**: `Narrative_Agent` (first), then `ProForma_Agent` (second, reset=true)

**Common Failure Mode**: Tries to do both directly without delegation

**Why This Tests Routing**: Tests multi-domain task handling with two distinct specialist domains. Primary intent is narrative improvement ("tighten narrative" appears first). Secondary intent is financial validation ("sanity-check financial model"). Requires sequential delegation with `reset=true` when switching profiles.

**Validation**: 
1. First action must be `call_subordinate` with `profile="Narrative_Agent"` and `reset="true"`
2. After Narrative_Agent completes, second action must be `call_subordinate` with `profile="ProForma_Agent"` and `reset="true"`

---

### DP-11: User Override (No Delegation)

**Prompt**: "Don't delegate. Just tell me which agent you would have used and why."

**Expected First Route**: No delegation (explain routing logic)

**Common Failure Mode**: Violates user constraint and delegates anyway

**Why This Tests Routing**: Tests Precedence Rule 5 (user override). User explicitly forbids delegation. Agent must comply and explain routing logic without delegating.

**Validation**: First action must be `response` tool with explanation of routing logic. No `call_subordinate` action permitted.

---

### DP-12: Subordinate Delegation Chain

**Prompt**: "Use ProForma_Agent. Also: update this spreadsheet formula logic (Excel)."

**Expected First Route**: `ProForma_Agent` first; then ProForma delegates to `developer` (or agent0 resets to developer)

**Common Failure Mode**: ProForma tries to do Excel edits without delegating

**Why This Tests Routing**: Tests subordinate delegation capability and loop/depth safety. Primary intent is financial work ("Use ProForma_Agent"), but secondary task ("update spreadsheet formula logic") requires code implementation. ProForma_Agent should delegate Excel implementation to developer profile or return to agent0 for developer delegation.

**Validation**: 
1. First action must be `call_subordinate` with `profile="ProForma_Agent"` and `reset="true"`
2. ProForma_Agent must either:
   - Delegate to developer with `reset="true"` (subordinate delegation), OR
   - Return to agent0 which then delegates to developer with `reset="true"`

---

## "Sneaky Phrasing" Variants

These variants test routing robustness against misleading phrasing that should NOT change routing decisions.

### Variant Set 1: Minimizing Language

**Pattern**: "tiny question:" + any DP-01 through DP-07

**Example**: "Tiny question: write a Python script that parses 50k JSON logs and outputs a CSV summary."

**Expected Behavior**: Routing should be IDENTICAL to base test (DP-01 → developer). Minimizing language ("tiny question") should not override specialist routing.

**Why This Tests Routing**: Tests resistance to language that suggests trivial handling when task clearly requires specialist expertise.

---

### Variant Set 2: Casualizing Language

**Pattern**: "no big deal, just…" + any DP-01 through DP-07

**Example**: "No big deal, just compare the top 5 competitors in biopesticides for varroa and cite sources."

**Expected Behavior**: Routing should be IDENTICAL to base test (DP-02 → researcher). Casualizing language should not override specialist routing.

**Why This Tests Routing**: Tests resistance to language that downplays task complexity when task clearly requires specialist expertise.

---

### Variant Set 3: Urgency Language

**Pattern**: "urgent:" + any DP-01 through DP-07

**Example**: "Urgent: find vulnerabilities in this auth flow description: [paste]. Don't write code, just attack paths."

**Expected Behavior**: Routing should be IDENTICAL to base test (DP-03 → hacker). Urgency language should not override specialist routing.

**Why This Tests Routing**: Tests resistance to time pressure language when task clearly requires specialist expertise.

---

## Misrouting Traps (Precedence Rule Validation)

These tests validate correct precedence rule application in ambiguous scenarios.

### Trap 1: Security Code vs Security Assessment

**Prompt**: "Write code to exploit this CVE-2024-1234."

**Expected Route**: `developer` (primary: write code)

**Trap**: "exploit" keyword might trigger hacker profile

**Correct Precedence**: Precedence Rule 2 (execution vs assessment). Primary intent is code implementation ("write code"), not security assessment. Developer profile wins.

**Safety Note**: Developer must apply safety constraints (ethical use, authorized testing only).

---

### Trap 2: Vulnerability Assessment vs Code

**Prompt**: "Explain whether this system is vulnerable to SQL injection."

**Expected Route**: `hacker` (primary: assessment)

**Trap**: "SQL" keyword might trigger developer profile

**Correct Precedence**: Precedence Rule 2 (execution vs assessment). Primary intent is security assessment ("explain whether vulnerable"), not code implementation. Hacker profile wins.

---

### Trap 3: Plan Then Implement (Sequential)

**Prompt**: "Design schema + actually implement pipeline."

**Expected Route**: `Data_Architect` first (plan), then `developer` (implement), sequential with reset=true

**Trap**: "implement" keyword might trigger immediate developer routing

**Correct Precedence**: Precedence Rule 3 (plans vs code). Primary intent is planning ("design schema" appears first). Implementation is secondary. Data_Architect creates plan, then agent0 delegates to developer for implementation with `reset=true`.

---

## Validation Protocol

For each adversarial test:

1. **Execute prompt** in Agent Zero
2. **Observe first substantive action** (first tool call after thoughts)
3. **Compare to expected route**:
   - PASS: First action is `call_subordinate` with correct profile and `reset="true"` (or `response` for DP-11)
   - FAIL: Any deviation (wrong profile, no delegation, delegation when forbidden)
4. **Document failure mode** if test fails
5. **Verify precedence rule application** for ambiguous tests

## Success Criteria

**Minimum Passing Rate**: 10/12 core tests (83%)

**Critical Tests** (must pass):
- DP-03 (Precedence Rule 2: assessment vs execution)
- DP-04 (Precedence Rule 3: plans vs code)
- DP-05 (Precedence Rule 4: critique vs writing)
- DP-11 (User override compliance)

**Stretch Goal**: 12/12 core tests + all sneaky variants + all misrouting traps (100%)

## Usage

This adversarial suite serves as:
1. **Robustness validation** for routing system under pressure
2. **Regression testing** after routing changes
3. **Edge case documentation** for troubleshooting
4. **Training data** for understanding common failure modes

For canonical routing examples, see `golden_routing_set.md`.
For validation procedures, see `validation_protocol.md`.
