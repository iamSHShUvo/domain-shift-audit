# Agent Team

The project uses a small team of AI agent roles. In practice one coding agent
(VS Code agent mode) plays each role in turn, started with a role-specific
prompt. A human (the project owner) approves every handoff and every merge.

## Roles

| Role | Responsibility | Inputs | Outputs |
|---|---|---|---|
| Planner | Turns the spec into GitHub Issues with acceptance criteria. Keeps SPEC.md and the issues consistent. | SPEC.md, README.md | Issues, updated spec |
| Builder | Implements one issue at a time, following AGENTS.md. | One issue, SPEC.md | Code and a commit that references the issue |
| Tester | Writes unit and integration tests for the issue's acceptance criteria and runs `make test`. | The issue, the Builder's code | Passing tests, bug reports back to the Builder |
| Reviewer | Checks the change against the acceptance criteria and AGENTS.md rules (no real data, no scope creep). | The diff, the issue | Approve, or a list of required changes |

## Handoffs

1. Planner creates the issue, then the Builder implements it.
2. The Builder hands off to the Tester, who writes and runs the tests.
3. If tests fail, the Tester reports the failure and the Builder fixes it. This repeats until tests pass.
4. The Reviewer checks the final diff. The human approves and merges.

## Boundaries

- Agents never merge on their own.
- Agents never touch real data or secrets.
- If the spec is unclear or two requirements conflict, the agent stops and asks the human.