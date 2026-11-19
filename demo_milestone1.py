"""Complete Milestone 1 demo (slides 17-18) - no web UI needed."""
from pipeline import process_ticket

tickets = [
    """URGENT: VPN is not connecting.
I cannot work and I have an important client meeting.""",
    "I forgot my password and my account is locked, I cannot login",
    "My laptop screen is flickering and the keyboard is not working",
    "Please increase my mailbox storage, shared drive is full",
    "Need admin rights to install software on my PC",
    "Request for leave balance and payroll details from HR",
    "URGENT: system is down for all users, production outage, client demo today",
]
for t in tickets:
    r = process_ticket(t)
    print("Ticket:         ", t.replace("\n", " "))
    print("Category:       ", r["category"], f'({r["confidence"]}% confidence)')
    print("Severity:       ", r["severity"], f'({r["severity_score"]:.0f}%)')
    print("Business impact:", r["business_impact"])
    print("Priority:       ", r["priority"])
    print("-" * 60)
