# Why this package is structured this way

The discovery description names the actual job and common user wording. The main
instructions provide a compact conditional workflow; detailed material is loaded
only as needed. Scripts handle deterministic file/validation tasks, while artistic
choices remain adaptable to evidence. Runtime/visual gates prevent “valid code”
from being misreported as a completed visual result.

This follows the progressive-disclosure format of the
[Agent Skills specification](https://agentskills.io/specification). Skill routing
and implicit invocation settings follow
[OpenAI's skill guidance](https://learn.chatgpt.com/docs/build-skills).
Concise instructions, appropriate flexibility, and test-driven iteration follow
[Anthropic's authoring guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

The specific style model, asset rights gates, templates, and test scenarios are
original package design choices. “Best skill” is not a universal benchmark result.
The package includes a test protocol; it does not claim a measured improvement in
an unseen agent or that a model has learned permanently from reading the files.
