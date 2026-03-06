# Task 1: AI Message Handler

This task implements an asynchronous AI support agent for NexusAI Telecom using the Groq API (`llama-3.3-70b-versatile`).

## How to do the task as per the code

1. **Install dependencies**: Use the provided `requirements.txt` to install required packages (`aiohttp`, `python-dotenv`).
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**: Create a `.env` file in the `task_1` directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_key_here
   ```

3. **Running the script**: Execute the Python script to start the interactive CLI agent.
   ```bash
   python ai_message_handler_2.py
   ```

4. **Interacting**: 
   - Enter a valid Customer ID (or press Enter for GUEST).
   - Enter your message.
   - Choose a channel (`voice`, `chat`, or `whatsapp`) to see how the response is formatted and handled according to the channel constraints.
   - Type `exit` or `quit` to stop the session.
