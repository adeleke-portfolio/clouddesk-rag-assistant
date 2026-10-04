from email_generator import generate_reply

reply = generate_reply(
    customer_name="Michael",
    complaint="This is the third time I've contacted you. Nobody responds. I'm cancelling my subscription and telling everyone I know to avoid CloudDesk.",
    ticket_number="CD-48217",
    priority="urgent",
    response_time="1 business hour",
)

print(reply)