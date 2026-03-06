# Task 2: Call Record Repository

This task demonstrates how to use `asyncpg` to interact with a PostgreSQL database asynchronously. It includes functionality for saving call records, retrieving recent calls, and running analytics.

## How to do the task as per the code

1. **Setup the Database**: Use `database.sql` to create the necessary tables and indexes in a PostgreSQL database named `support_db`.
   ```bash
   psql -U postgres -d support_db -f database.sql
   ```

2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Configuration**: In `main.py`, ensure the PostgreSQL connection pool is configured correctly for your local environment:
   - `user="postgres"`
   - `password="password"`
   - `database="support_db"`
   - `host="localhost"`

4. **Running the code**: Execute the main asynchronous entry script.
   ```bash
   python main.py
   ```
   This script will insert a dummy call record using `CallRecordRepository` (from `repository.py`) and print recent customer calls. 

5. **Analytics**: The function `get_problem_intents` in `analytics.py` can be called to retrieve statistics about problem intents over the last 7 days.
