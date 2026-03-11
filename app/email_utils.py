from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME= "pavithra.rajan1010@gmail.com",
    MAIL_PASSWORD= "zmva dfnl qhvm hydl",
    MAIL_FROM= "pavithra.rajan1010@gmail.com",
    MAIL_PORT= 587,
    MAIL_SERVER= "smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

async def send_email(email: str, subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
