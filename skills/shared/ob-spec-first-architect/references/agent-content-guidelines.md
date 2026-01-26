# Agent Spec Content Guidelines

Detailed instructions for creating LLM Agent specification documents.

## 1. Set Metadata (YAML Frontmatter)

```yaml
status: 🏗 Draft
created: YYYY-MM-DD
updated: YYYY-MM-DD
related_docs: []
tags: [spec, agent, llm]
```

## 2. Document Context

- **Agent's purpose and necessity**: Why is this agent needed?
- **Problems being solved**: What specific issues does it address?
- **Current architecture** (if refactoring): What's the existing implementation?

## 3. Define Requirements

### Functional Requirements
- What the agent must do
- Core capabilities and features
- Expected behaviors

### Non-functional Requirements
- Token usage limits and optimization
- Latency constraints
- Consistency and reliability expectations
- Cost considerations

### Out of Scope
- Explicitly state what this agent will NOT do
- Set clear boundaries

## 4. Design Agent Architecture

### Agent Roles and Responsibilities
- Define the agent's role in the system
- Clarify its scope and authority

### Prompt Design
- **Current prompt** (if refactoring)
- **Improved prompt** design
- Prompt engineering strategies

### Tools/Functions
- **LLM-based functions**: When to use AI decision-making
- **Rule-based functions**: When to use deterministic logic
- Tool classification and selection criteria

### Agent Interactions and Orchestration
- How does this agent communicate with other agents?
- Orchestration patterns
- Data flow between agents

### Input/Output Schemas
- Define expected input format
- Define output format
- Include examples

## 5. Specify Edge Cases

### LLM API Failures
- Retry strategies
- Fallback mechanisms
- Error handling

### Prompt Optimization Needs
- How to identify when prompts need improvement
- Metrics for prompt performance

### Cost Optimization Strategies
- Token usage reduction techniques
- Caching strategies
- When to use smaller models

## Optional Sections

### Expected Benefits
- Token reduction estimates
- Performance improvements
- Cost savings

### Open Questions
- Design decisions that need clarification
- Trade-offs to consider

### References
- Current code locations
- Related agents
- Prompt patterns used
