async def get_problem_intents(pool):

    query = """
    SELECT
        intent_type,
        COUNT(*) AS total_calls,
        SUM(CASE WHEN outcome='resolved' THEN 1 ELSE 0 END)::float
        / COUNT(*) AS resolution_rate,
        AVG(csat_score) AS avg_csat
    FROM call_records
    WHERE created_at >= NOW() - INTERVAL '7 days'
    GROUP BY intent_type
    ORDER BY resolution_rate ASC
    LIMIT 5
    """

    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    return [dict(row) for row in rows]