import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

def sendEmail(reciever_email, product_name, product_link, alert_price, curr_price):
    sender_email = os.getenv('SENDER_EMAIL')
    sender_pass = os.getenv('SENDER_PASS')

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    subject = "Price Drop Alert for Your Tracked Product!"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; font-size: 15px;">
        <p>The price of the product you’re tracking has dropped below your set alert price.</p>
        
        <h3>Product Details:</h3>
        <ul>
            <li><b>Product Name:</b> {product_name}</li>
            <li><b>Current Price:</b> ₹ {curr_price}</li>
            <li><b>Your Alert Price:</b> ₹ {alert_price}</li>
            <li><b>Product Link:</b> <a href="{product_link}">View Product</a></li>
        </ul>
        
        <p>Thank you for using our Price Tracking Software. We hope this alert helps.</p>
        <p>Happy Shopping,<br>Price Tracker India</p>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = reciever_email
    msg["Subject"] = subject

    # Attach the body to the email
    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_pass)
        server.sendmail(sender_email, reciever_email, msg.as_string())
        server.quit()
        return 1

    except:
        print(f"Error sending email to: {reciever_email}")
        return -1
