OUTPUT:

Sequential Fetch Time: 670 ms
Parallel Fetch Time: 310 ms
Speed Improvement: 2.16x

# Task 3: Parallel Fetcher

This task demonstrates the performance difference between fetching customer data sequentially versus in parallel using `asyncio.gather`.

## How to do the task as per the code

1. **Requirements**: No external dependencies are required as all components are built-in Python modules. Ensure you have Python 3.10+ (for `dict | None` type hints and `dataclasses`).
2. **Execution**: Run the Python script directly from your terminal.
   ```bash
   python parallel_fetcher.py
   ```
3. **Observation**: The script performs data fetching simulations with intentional delays. It will first run a sequential fetch, print the resulting data and time taken. Next, it will perform a parallel fetch, catching any exceptions (like intentional billing timeouts) and print the improved fetch time.
