# Backend Spec Content Guidelines

Detailed instructions for creating API and Backend specification documents.

## 1. Set Metadata (YAML Frontmatter)

```yaml
status: 🏗 Draft
created: YYYY-MM-DD
updated: YYYY-MM-DD
related_docs: [[Related Spec 1]], [[Related Spec 2]]
tags: [spec, api, backend]
```

## 2. Document Context

- **Why this feature is needed**: Business justification and value
- **What problem it solves**: Specific pain points addressed
- **Background information**: Related features, dependencies, constraints

## 3. Define Requirements

### Functional Requirements (use checkboxes)
- [ ] Requirement 1: Description
- [ ] Requirement 2: Description
- [ ] Requirement 3: Description

### Non-functional Requirements
- Performance expectations (response time, throughput)
- Scalability requirements
- Security considerations
- Availability/reliability targets

### Out of Scope
- Features explicitly excluded
- Future enhancements not included in this spec

## 4. Design Technical Solution

### Data Models and Entities
- Database schema changes
- Entity relationships
- Data types and constraints

### API Endpoints and Schemas
- Endpoint paths and methods
- Request schemas (headers, body, query params)
- Response schemas (success and error cases)
- Status codes

**Example**:
```
POST /api/users
Request: { "name": "string", "email": "string" }
Response: { "id": "uuid", "name": "string", "email": "string" }
```

### Business Logic Flows
- Core business rules
- Processing steps
- Validation logic
- State management

### State Transitions
- Entity lifecycle
- Status changes and triggers
- State machine description (if applicable)

### Edge Cases and Error Handling
- Invalid input scenarios
- Concurrent access handling
- External service failures
- Rollback strategies

## 5. Specify Acceptance Criteria

### Success Metrics (checkboxes)
- [ ] Metric 1: Measurable goal
- [ ] Metric 2: Measurable goal

### Test Scenarios (Given/When/Then format)
- **Scenario 1**: Happy path
  - Given: Initial state
  - When: Action performed
  - Then: Expected outcome

- **Scenario 2**: Error case
  - Given: Error condition
  - When: Action attempted
  - Then: Error handled gracefully

## Optional Sections

### Implementation Notes
- Developer guidance
- Technical considerations
- Performance optimization tips

### Dependencies
- External services required
- Third-party libraries
- Infrastructure needs

### Migration Strategy
- For changes to existing systems
- Data migration plan
- Rollback procedures
- Backward compatibility

### Timeline & Milestones
- Phased rollout plan
- Key milestones
- Dependencies on other work

### Review History
- Approval tracking
- Change log
- Stakeholder sign-offs
