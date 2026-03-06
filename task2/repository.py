import asyncpg

class CallRecordRepository:

    def __init__(self, pool):
        self.pool = pool

    async def save(self, call_data: dict):

        query = """
        INSERT INTO call_records
        (customer_phone, channel, transcript, ai_response,
         intent_type, outcome, confidence, csat_score, duration)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
        """

        async with self.pool.acquire() as conn:
            await conn.execute(
                query,
                call_data["phone"],
                call_data["channel"],
                call_data["transcript"],
                call_data["ai_response"],
                call_data["intent_type"],
                call_data["outcome"],
                call_data["confidence"],
                call_data.get("csat"),
                call_data["duration"]
            )

    async def get_recent(self, phone: str, limit: int = 5):

        query = """
        SELECT *
        FROM call_records
        WHERE customer_phone = $1
        ORDER BY created_at DESC
        LIMIT $2
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, phone, limit)

        return [dict(row) for row in rows]