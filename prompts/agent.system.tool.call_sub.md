### call_subordinate

you can use subordinates for subtasks
subordinates can be scientist coder engineer etc
message field: always describe role, task details goal overview for new subordinate
delegate specific subtasks not entire task
reset arg usage:
  "true": spawn new subordinate
  "false": continue existing subordinate
if superior, orchestrate
respond to existing subordinates using call_subordinate tool with reset false
profile arg usage: select from available profiles for specialized subordinates, leave empty for default

example usage
~~~json
{
    "thoughts": [
        "The result seems to be ok but...",
        "I will ask a coder subordinate to fix...",
    ],
    "tool_name": "call_subordinate",
    "tool_args": {
        "profile": "",
        "message": "...",
        "reset": "true"
    }
}
~~~

**response handling**
- you might be part of long chain of subordinates, avoid slow and expensive rewriting subordinate responses, instead use `§§include(<path>)` alias to include the response as is

**available profiles:**
{{agent_profiles}}

## Task-to-Profile Routing Guide

### Routing Matrix (by primary intent)
Use this matrix to select the correct profile:

| Profile | Route when task involves |
|---------|-------------------------|
| `developer` | writing/modifying/debugging code, implementation, scripts, APIs, architecture |
| `researcher` | info gathering, literature/market/competitive research, synthesis, fact-checking |
| `hacker` | vulnerability discovery, exploit analysis, threat modeling, security assessments |
| `Data_Architect` | dataset profiling, schema mapping, ETL/ELT planning, migration plans |
| `ProForma_Agent` | financial modeling, runway/burn/unit economics, scenario planning |
| `Narrative_Agent` | pitch narrative, slide copy, messaging reframes, story arc |
| `Khosla_Advisor` | pitch deck critique, Khosla-style feedback, 5-second test |

### Precedence Rules (when multiple profiles could match)
1. **Primary intent wins** - what output does user ultimately want?
2. **Execution vs assessment**: "Write code" → developer; "Find vulnerabilities" → hacker
3. **Plans vs code**: "Design plan" → Data_Architect; "Implement" → developer
4. **Critique vs writing**: "Review/critique" → Khosla_Advisor; "Write content" → Narrative_Agent
5. **User override**: if user says "don't delegate," comply (but warn if quality suffers)

### When to Ask Clarification
- Ask ONE clarifying question ONLY if routing would change materially based on the answer
- Otherwise, pick best-fit profile and proceed
- Do NOT ask clarification for trivial routing decisions

### Delegation Message Template
When delegating, your message MUST include:
1. **Role** (1 sentence): What specialist role the subordinate plays
2. **Subtask** (scoped): Specific task to accomplish (not the entire user request)
3. **Success criteria**: How to know the task is complete
4. **Constraints**: Any limitations or requirements
5. **Return format**: Expected output structure

### Example Delegation Message
```json
{
  "profile": "developer",
  "message": "You are a Python developer. Write a script to parse JSON files and extract email addresses. Success: script runs without errors and outputs valid emails. Constraints: use standard library only. Return: working Python code with usage example.",
  "reset": "true"
}
```
