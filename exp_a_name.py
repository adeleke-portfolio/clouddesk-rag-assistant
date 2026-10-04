from email_generator import generate_reply

reply = generate_reply(
    customer_name="Michael",
    complaint="I've been trying to log in for two days and keep getting an error. This is unacceptable.",
    ticket_number="CD-48215",
    priority="high",
    response_time="4 business hours",
)

print(reply)