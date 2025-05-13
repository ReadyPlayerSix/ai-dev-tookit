# Think Tool Guide

The Think Tool provides Claude with a structured way to reflect on complex problems, break down tasks, check requirements, and analyze results before taking action.

## Overview

Unlike other tools that perform actions on files or the system, the Think Tool is purely for reflection and reasoning. It's like a scratchpad where Claude can work through problems methodically without affecting anything. The output is formatted to clearly separate thought processes from regular conversation with the user.

## When to Use the Think Tool

Use the Think Tool when you need to:

1. **Break down complex tasks** into manageable steps
2. **Verify all required information** is collected before proceeding 
3. **Check if planned actions comply** with policies or constraints
4. **Analyze the results** of other tools to verify correctness
5. **Explore multiple approaches** to solving a problem

## How to Use the Think Tool

```python
think("Your thought or reflection here")
```

The input can be any text content that represents your thought process. The tool will format it and return it as a reflection.

## Example Usage Patterns

### Requirements Verification

```python
think("""
User wants to cancel flight ABC123
- Need to verify: user ID, reservation ID, reason
- Check cancellation rules:
  * Is it within 24h of booking?
  * If not, check ticket class and insurance
- Verify no segments flown or are in the past
- Plan: collect missing info, verify rules, get confirmation
""")
```

### Breaking Down Complex Tasks

```python
think("""
User wants to book 3 tickets to NYC with 2 checked bags each
- Need user ID to check:
  * Membership tier for baggage allowance
  * Which payments methods exist in profile
- Baggage calculation:
  * Economy class × 3 passengers
  * If regular member: 1 free bag each → 3 extra bags = $150
  * If silver member: 2 free bags each → 0 extra bags = $0
  * If gold member: 3 free bags each → 0 extra bags = $0
- Payment rules to verify:
  * Max 1 travel certificate, 1 credit card, 3 gift cards
  * All payment methods must be in profile
  * Travel certificate remainder goes to waste
""")
```

### Code Analysis

```python
think("""
Analyzing the bug in the authentication system:
1. The issue appears in auth_controller.js when validating tokens
2. The JWT verification isn't checking expiration correctly
3. Need to modify the verification to use the exp claim
4. Also need to add proper error handling for expired tokens
5. This will resolve the intermittent authentication failures
""")
```

### Decision Making

```python
think("""
Comparing approaches for implementing the search feature:
Option 1: Server-side search with SQL LIKE
- Pros: Simple implementation, works with existing DB
- Cons: Limited fuzzy matching, performance issues on large tables

Option 2: Elasticsearch integration
- Pros: Powerful search capabilities, scales well
- Cons: Additional infrastructure, more complex setup

Option 3: Client-side filtering with preloaded data
- Pros: Fast user experience, no additional API calls
- Cons: Limited to small datasets, initial load time increase

Decision: Option 2 is best for this project given the size of the dataset and search requirements
""")
```

## What Happens Behind the Scenes

When you use the Think Tool:

1. Your thought text is received by the tool
2. It's formatted with appropriate markers (like `<reflection>` tags)
3. The formatted text is returned to Claude
4. Claude reads the reflection but does not display it directly to the user
5. Claude uses these insights to inform its response to the user

## Important Distinctions

- **Think Tool vs. Deep Analysis**: The Think Tool provides immediate reflection, while the Deep Analysis task in the TaskBoard system processes complex queries asynchronously and returns results later.

- **Reflection vs. Action**: Use the Think Tool for reasoning and planning, then use other tools for actually taking actions based on your reasoning.

## Best Practices

1. **Be explicit about your reasoning** - Include your thought process, not just conclusions
2. **Structure complex thoughts** - Use lists, sections, or tables to organize complex ideas
3. **Consider edge cases** - Use the Think Tool to identify potential issues before they occur
4. **Verify requirements** - Ensure you have all needed information before proceeding
5. **Check your assumptions** - Use the tool to make your assumptions explicit and verify them

## Advanced Features

In addition to the basic `think()` function, there are specialized thinking templates available:

- `think_with_template("requirements", requirements=["a", "b"], provided=["a"])` - For checking required information
- `think_with_template("rule_check", rules=["rule1", "rule2"], action="action", analysis="...")` - For verifying rule compliance
- `think_with_template("action_plan", goal="goal", steps=["step1", "step2"])` - For planning complex actions
- `think_about_code(code="...", objective="find bugs")` - For analyzing code snippets

These templates provide structure for common reflection patterns.