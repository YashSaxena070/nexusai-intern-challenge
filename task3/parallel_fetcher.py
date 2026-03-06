import asyncio
import random
import time
from dataclasses import dataclass

@dataclass
class CustomerContext:

    phone: str
    crm_data: dict | None
    billing_data: dict | None
    ticket_data: dict | None

    data_complete: bool
    fetch_time_ms: float

async def fetch_crm(phone: str):

    await asyncio.sleep(random.uniform(0.2, 0.4))

    return {
        "account_id": "ACC123",
        "phone": phone,
        "plan": "Fiber 200 Mbps",
        "status": "active"
    }

async def fetch_billing(phone: str):

    await asyncio.sleep(random.uniform(0.15, 0.35))

    # 10% failure chance
    if random.random() < 0.1:
        raise TimeoutError("Billing system timeout")

    return {
        "last_payment": "2026-03-01",
        "amount_due": 0,
        "status": "paid"
    }

async def fetch_tickets(phone: str):

    await asyncio.sleep(random.uniform(0.1, 0.3))

    return {
        "recent_tickets": [
            "Slow internet",
            "Router reboot issue",
            "Billing query",
            "Data usage question",
            "Service upgrade request"
        ]
    }

async def fetch_sequential(phone: str):

    start = time.perf_counter()

    crm = await fetch_crm(phone)

    try:
        billing = await fetch_billing(phone)
    except TimeoutError:
        billing = None

    tickets = await fetch_tickets(phone)

    end= time.perf_counter()

    total_time = (end - start) * 1000

    return CustomerContext(
        phone=phone,
        crm_data=crm,
        billing_data=billing,
        ticket_data=tickets,
        data_complete=(crm and billing and tickets),
        fetch_time_ms=total_time
    )

async def fetch_parallel(phone: str):

    start = time.perf_counter()

    results = await asyncio.gather(
        fetch_crm(phone),
        fetch_billing(phone),
        fetch_tickets(phone),
        return_exceptions=True
    )

    crm, billing, tickets = results

    if isinstance(billing, Exception):
        print("⚠ Billing fetch failed:", billing)
        billing = None

    end = time.perf_counter()
    total_time = (end - start) * 1000

    return CustomerContect(
        phone=phone,
        crm_data=crm if not isinstance(crm, Exception) else None,
        billing_data=billing,
        ticket_data=tickets if not isinstance(tickets, Exception) else None,
        data_complete=(crm and billing and tickets),
        fetch_time_ms=total_time
    )


async def main():

    phone = "+919876543210"

    print("\nSequential Fetch")

    seq = await fetch_sequential(phone)

    print(seq)
    print("Time:", seq.fetch_time_ms, "ms")

    print("\nParallel Fetch")

    par = await fetch_parallel(phone)

    print(par)
    print("Time:", par.fetch_time_ms, "ms")

asyncio.run(main())

