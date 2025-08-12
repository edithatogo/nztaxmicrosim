# Proposal: Data-Driven Rules Engine

## 1. Summary

This document proposes a potential architectural enhancement to the NZ Tax Microsimulation Model: migrating from a code-based rules implementation to a data-driven rules engine. This would involve representing the logic of tax and benefit rules in a data format (like JSON) instead of hard-coding it in Python.

This proposal captures the strategic suggestion raised during our discussion. It outlines the current state, a possible future state, the associated trade-offs, and a potential path forward.

## 2. Current Architecture

The current system implements a hybrid approach that separates numerical **parameters** from logical **rules**.

*   **Parameters** (e.g., tax rates, income thresholds, benefit amounts) are stored in `parameters_YYYY-ZZZZ.json` files. This is highly flexible and allows for easy updates as policy numbers change year to year.
*   **Rules and Formulae** (e.g., the logic of how to apply a tax bracket, how to calculate an abatement) are implemented as Python functions and classes in the `src/` directory. For example, the `JSSRule` class in `src/benefit_rules.py` calls the `calculate_jss` function in `src/benefits.py`, which contains the specific logic for that benefit.

To add a completely new rule to the simulation (e.g., a new type of tax credit), a developer must write new Python code.

## 3. Proposed Architecture

The proposed architecture would abstract the rule logic itself into a data format, likely JSON. A new, generic "Rules Engine" component would be created in Python. This engine's job would be to read a rule definition from a JSON file and execute it.

### Example: Hypothetical JSON Rule

Here is a simplified, hypothetical example of how a rule like the Independent Earner Tax Credit (IETC) could be represented in JSON.

```json
{
  "rule_name": "IETC",
  "description": "Calculates the Independent Earner Tax Credit.",
  "conditions": [
    { "variable": "taxable_income", "operator": ">=", "value_from_param": "ietc.thrin" },
    { "variable": "taxable_income", "operator": "<", "value_from_param": "ietc.thrab" },
    { "variable": "is_wff_recipient", "operator": "is", "value": false },
    { "variable": "is_super_recipient", "operator": "is", "value": false }
  ],
  "actions": [
    {
      "type": "calculation",
      "output_variable": "ietc_entitlement",
      "formula": "min(ietc.ent, ietc.ent - ((taxable_income - ietc.thrab) * ietc.abrate))"
    }
  ]
}
```

In this model, the Python rules engine would be responsible for:
1.  Parsing the `conditions` and evaluating them against the input data.
2.  If all conditions are met, parsing and executing the `actions`. This might involve using a safe expression evaluation library to compute the `formula`.

## 4. Pros & Cons

Moving to a data-driven architecture is a significant decision with major trade-offs.

**Pros:**

*   **Flexibility:** As you identified, rules could be added or changed without deploying new Python code. This is the primary advantage.
*   **Accessibility:** With a well-defined schema and good tooling, it's possible that non-programmers (e.g., policy analysts) could read, understand, and perhaps even modify rules.
*   **Auditability & Transparency:** The complete logic of a rule is explicitly defined in a single data structure, which can be easier to audit than Python code spread across multiple files.

**Cons:**

*   **Engine Complexity:** The rules engine itself is a complex piece of software. It needs to be robust, secure, and handle all the logical cases required by the domain. This is a very significant engineering effort.
*   **Performance:** A generic engine that interprets rules from data will almost certainly be slower than the current system of specialized, compiled Python functions. For a large-scale simulation, this could be a major issue.
*   **Expressiveness Limitations:** It is very difficult to design a JSON schema that can elegantly handle all possible computational logic. The engine might not be able to express a particularly complex new rule, forcing a "leaky abstraction" where some rules remain in Python anyway.
*   **Debugging & Tooling:** Debugging becomes much harder. Instead of placing a breakpoint in a Python function, a developer has to debug the engine itself as it processes the rule data. Standard development tools (linters, static analyzers) would not understand the JSON rules.

## 5. High-Level Roadmap

If this architectural change were to be pursued, it should be done carefully and incrementally. A possible high-level roadmap would be:

1.  **Phase 1: Proof of Concept & Engine Design.**
    *   Design a comprehensive JSON schema for the rules.
    *   Build a minimal Python rules engine that can only execute one or two of the simplest existing rules (e.g., a basic tax credit).
    *   Benchmark the performance of this approach against the hard-coded version.

2.  **Phase 2: Engine Expansion.**
    *   Based on the findings from Phase 1, expand the engine's capabilities to handle all the logical constructs found in the existing rules (e.g., different abatement types, complex eligibility criteria).

3.  **Phase 3: Rule Migration.**
    *   One by one, migrate the existing, hard-coded Python rules into the new JSON format, verifying the output of the new rule matches the old one perfectly.

4.  **Phase 4: Full Deprecation & Refinement.**
    *   Once all rules are migrated, the old Python code can be removed.
    *   Develop tooling to help create, validate, and debug the JSON rules.
