from dataclasses import dataclass

@dataclass
class CustomerContext:
    phone: str
    crm_data: dict | None
    billing_data: dict | None
    ticket_data: dict | None
    data_complete: bool
    fetch_time_ms: float