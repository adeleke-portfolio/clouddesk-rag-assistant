from email_generator import generate_reply

reply = generate_reply(
    customer_name="Michael",
    complaint="I was charged twice this month and no one has replied to my emails. I want my money back.",
    ticket_number="CD-48216",
    priority="urgent",
    response_time="2 business hours",
)

print(reply)