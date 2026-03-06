When multiple escalation rules apply, the engine evaluates them in priority order. Critical business rules override others. For example, even if the AI confidence is high (0.90), a request with intent"service_cancellation" will always escalate because it involves account termination and requires human verification. This design prioritizes business risk and customer protection over AI confidence.

# Task 4: Escalation Engine

This task implements a set of rules to determine whether a customer interaction should be escalated to a human agent, based on confidence, sentiment, intent, and customer context.

## How to do the task as per the code

1. **Requirements**: In order to test the escalation engine, you need to install the testing framework `pytest` (listed in `requirements.txt`).
   ```bash
   pip install -r requirements.txt
   ```
2. **Execution**: Run the provided unit tests to verify that all escalation rules function correctly according to the strict business logic.
   ```bash
   pytest test_escalation.py -v
   ```
3. **Logic Overview**: The `should_escalate` function in `escalation.py` demonstrates evaluating multiple strict rules iteratively (e.g., assessing sentiment, previous ticket history, VIP status, and data completeness).