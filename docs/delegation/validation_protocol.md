# Delegation Validation Protocol

Manual validation procedure for Agent Zero's delegation system using 15 representative prompts from golden routing set and adversarial suite.

## Purpose

This protocol provides:
- **Repeatable validation** procedure for testing delegation accuracy
- **Clear pass/fail criteria** for each test prompt
- **Baseline metrics** for measuring routing system performance
- **Regression testing** framework for validating changes to routing logic

## Validation Methodology

### Test Execution Procedure

1. **Start fresh Agent Zero session** (clear context)
2. **Execute each prompt** in sequence
3. **Record first substantive action** (first tool call after thoughts)
4. **Compare to expected action** using pass/fail criteria
5. **Document any failures** with observed behavior
6. **Calculate pass rate** (passed tests / total tests)

### Pass/Fail Criteria

**PASS**: First substantive action matches expected action
- For delegation tests: First action is `call_subordinate` with correct `profile` and `reset="true"`
- For direct response tests: First action is `response` tool (no delegation)
- For multi-step tests: First action matches expected first route, subsequent actions follow expected sequence

**FAIL**: Any deviation from expected action
- Wrong profile selected
- No delegation when delegation is required
- Delegation when user forbids it
- Incorrect `reset` value
- Incorrect precedence rule application

### Success Thresholds

- **Minimum Passing**: 12/15 tests (80%)
- **Target Passing**: 14/15 tests (93%)
- **Perfect Score**: 15/15 tests (100%)

**Critical Tests** (must pass for system validation):
- VP-03 (Precedence Rule 2: assessment vs execution)
- VP-04 (Precedence Rule 3: plans vs code)
- VP-05 (Precedence Rule 4: critique vs writing)
- VP-11 (User override compliance)
- VP-13 (Trivial task - no delegation)

---

## 15-Prompt Validation Set

### VP-01: Developer - Code Implementation
**Source**: Golden Set (GR-02)
**Prompt**: Write a Python script that reads a CSV file and outputs the top 10 rows sorted by the 'revenue' column.
**Expected Profile**: developer
**Pass Criteria**: First action is call_subordinate with profile="developer" and reset="true"

### VP-02: Researcher - Competitive Analysis
**Source**: Adversarial Suite (DP-02)
**Prompt**: I don't need code. Compare the top 5 competitors in biopesticides for varroa and cite sources.
**Expected Profile**: researcher
**Pass Criteria**: First action is call_subordinate with profile="researcher" and reset="true"
**Common Failure**: Routed to developer because "top 5" sounds technical

### VP-03: Hacker - Security Assessment (CRITICAL)
**Source**: Adversarial Suite (DP-03)
**Prompt**: Find vulnerabilities in this auth flow description: [User logs in → JWT issued → Token stored in localStorage → API calls include token in Authorization header]. Don't write code, just attack paths.
**Expected Profile**: hacker
**Pass Criteria**: First action is call_subordinate with profile="hacker" and reset="true"
**Common Failure**: Routed to developer because "auth flow" sounds technical
**Critical Test**: Must pass for Precedence Rule 2 validation

### VP-04: Data_Architect - Schema Design (CRITICAL)
**Source**: Adversarial Suite (DP-04)
**Prompt**: Here's a messy CSV schema. Design an import plan + target schema + mapping.
**Expected Profile**: Data_Architect
**Pass Criteria**: First action is call_subordinate with profile="Data_Architect" and reset="true"
**Common Failure**: Routed to researcher (summarizes instead of creating mapping/plan)
**Critical Test**: Must pass for Precedence Rule 3 validation

### VP-05: Khosla_Advisor - Pitch Critique (CRITICAL)
**Source**: Adversarial Suite (DP-05)
**Prompt**: Critique my pitch deck. Be brutal. Apply the 5-second test.
**Expected Profile**: Khosla_Advisor
**Pass Criteria**: First action is call_subordinate with profile="Khosla_Advisor" and reset="true"
**Common Failure**: Routed to Narrative_Agent (starts rewriting instead of critiquing)
**Critical Test**: Must pass for Precedence Rule 4 validation

### VP-06: Narrative_Agent - Content Creation
**Source**: Adversarial Suite (DP-06)
**Prompt**: Rewrite slide 3–6 to be punchier and more inevitable.
**Expected Profile**: Narrative_Agent
**Pass Criteria**: First action is call_subordinate with profile="Narrative_Agent" and reset="true"
**Common Failure**: Routed to Khosla_Advisor (gives critique but no rewrite)

### VP-07: ProForma_Agent - Financial Modeling
**Source**: Adversarial Suite (DP-07)
**Prompt**: Model runway under 3 burn scenarios and flag the biggest sensitivities.
**Expected Profile**: ProForma_Agent
**Pass Criteria**: First action is call_subordinate with profile="ProForma_Agent" and reset="true"
**Common Failure**: Routed to researcher (explains conceptually instead of building model)

### VP-08: Developer - Security Tool Implementation
**Source**: Adversarial Suite (DP-08)
**Prompt**: Write a security scanner for our API and include OWASP checks.
**Expected Profile**: developer
**Pass Criteria**: First action is call_subordinate with profile="developer" and reset="true"
**Common Failure**: Routed to hacker (confuses 'security' keyword with 'security assessment')

### VP-09: Data_Architect - Research Then Plan
**Source**: Adversarial Suite (DP-09)
**Prompt**: Research the best ETL approach for importing HubSpot + Salesforce into a warehouse, then create the import plan.
**Expected Profile**: Data_Architect
**Pass Criteria**: First action is call_subordinate with profile="Data_Architect" and reset="true"
**Common Failure**: Routed to researcher and stops before creating plan

### VP-10: Multi-Domain Sequential Delegation
**Source**: Adversarial Suite (DP-10)
**Prompt**: Prepare investor materials: tighten narrative AND sanity-check financial model assumptions.
**Expected First Profile**: Narrative_Agent
**Expected Second Profile**: ProForma_Agent (after first completes)
**Pass Criteria**: First action is call_subordinate with profile="Narrative_Agent" and reset="true", then call_subordinate with profile="ProForma_Agent" and reset="true"
**Common Failure**: Tries to do both directly without delegation

### VP-11: User Override - No Delegation (CRITICAL)
**Source**: Adversarial Suite (DP-11)
**Prompt**: Don't delegate. Just tell me which agent you would have used and why.
**Expected Action**: Direct response (no delegation)
**Pass Criteria**: First action is response tool with routing explanation. NO call_subordinate permitted.
**Common Failure**: Violates user constraint and delegates anyway
**Critical Test**: Must pass for user override compliance validation

### VP-12: Speed Pressure + Code Task
**Source**: Adversarial Suite (DP-01)
**Prompt**: Quick: write a Python script that parses 50k JSON logs and outputs a CSV summary.
**Expected Profile**: developer
**Pass Criteria**: First action is call_subordinate with profile="developer" and reset="true"
**Common Failure**: agent0 answers conceptually without delegating ("speed pressure" triggers direct response)

### VP-13: Trivial Task - No Delegation (CRITICAL)
**Source**: Golden Set (GR-01)
**Prompt**: What's the current time?
**Expected Action**: Direct response (no delegation)
**Pass Criteria**: First action is response tool (no delegation)
**Common Failure**: Unnecessary delegation to researcher or developer
**Critical Test**: Must pass for trivial task classification validation

### VP-14: Execution vs Assessment - Security Code
**Source**: Misrouting Trap 1
**Prompt**: Write code to exploit this CVE-2024-1234.
**Expected Profile**: developer
**Pass Criteria**: First action is call_subordinate with profile="developer" and reset="true"
**Common Failure**: Routed to hacker ("exploit" keyword triggers security assessment)
**Note**: Developer must apply safety constraints (ethical use, authorized testing only)

### VP-15: Subordinate Delegation Chain
**Source**: Adversarial Suite (DP-12)
**Prompt**: Use ProForma_Agent. Also: update this spreadsheet formula logic (Excel).
**Expected First Profile**: ProForma_Agent
**Expected Subordinate Action**: ProForma delegates to developer
**Pass Criteria**: First action is call_subordinate with profile="ProForma_Agent" and reset="true", then ProForma delegates to developer with reset="true"
**Common Failure**: ProForma tries to do Excel edits without delegating

---

## Validation Results Template

| Test ID | Prompt Summary | Expected Profile | Actual Profile | Pass/Fail | Notes |
|---------|---------------|------------------|----------------|-----------|-------|
| VP-01 | Python CSV script | developer | | | |
| VP-02 | Competitor research | researcher | | | |
| VP-03 | Auth vulnerability | hacker | | | |
| VP-04 | Schema design | Data_Architect | | | |
| VP-05 | Pitch critique | Khosla_Advisor | | | |
| VP-06 | Slide rewrite | Narrative_Agent | | | |
| VP-07 | Runway modeling | ProForma_Agent | | | |
| VP-08 | Security scanner | developer | | | |
| VP-09 | ETL research+plan | Data_Architect | | | |
| VP-10 | Multi-domain | Narrative→ProForma | | | |
| VP-11 | User override | No delegation | | | |
| VP-12 | Speed pressure | developer | | | |
| VP-13 | Trivial task | No delegation | | | |
| VP-14 | Exploit code | developer | | | |
| VP-15 | Subordinate chain | ProForma→developer | | | |

**Summary Statistics**:
- Total Tests: 15
- Passed: ___ / 15
- Failed: ___ / 15
- Pass Rate: ____%
- Critical Tests Passed: ___ / 5

## Related Documentation

- **Golden Routing Set**: `golden_routing_set.md` - Canonical routing examples
- **Adversarial Suite**: `adversarial_delegation_suite.md` - Pressure tests and edge cases
- **DDP Constitution**: `/a0/prompts/agent.system.behaviour_default.md` - Core delegation rules
- **Routing Matrix**: `/a0/prompts/agent.system.tool.call_sub.md` - Profile selection guide
- **Solving Integration**: `/a0/prompts/agent.system.main.solving.md` - DDP in problem-solving loop
