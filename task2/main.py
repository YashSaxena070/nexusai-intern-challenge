import asyncio
import asyncpg
from repository import CallRecordRepository

async def main():

    pool = await asyncpg.create_pool(
        user="postgres",
        password="password",
        database="support_db",
        host="localhost"
    )

    repo = CallRecordRepository(pool)

    call_data = {
        "phone": "+919876543210",
        "channel": "chat",
        "transcript": "My internet is not working",
        "ai_response": "Please restart your router",
        "intent_type": "network_issue",
        "outcome": "resolved",
        "confidence": 0.87,
        "csat": 4,
        "duration": 45
    }

    await repo.save(call_data)

    recent = await repo.get_recent("+919876543210")

    print(recent)

asyncio.run(main())