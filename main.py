import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

username = "kdttw24@gmail.com"
login_password = "?Fr33d0m24?"
password = "pyjz jwat qbga qpyo"
target_website = "noreply-operations@transfeero.com"


def get_unread_emails():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    print("Login Succeed")
    mail.select("inbox")
    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()
    return mail, email_ids


def process_email(mail, email_id):
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            from_ = msg.get("From")
            if target_website in from_:
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                print("Subject:", subject)

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if "attachment" not in content_disposition:
                            if (
                                content_type == "text/plain"
                                or content_type == "text/html"
                            ):
                                body = part.get_payload(decode=True).decode()
                                if content_type == "text/html":
                                    html_content = body
                                    return html_content
                else:
                    content_type = msg.get_content_type()
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/html":
                        html_content = body
                        return html_content
    return None


def extract_and_click_link(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    # Find the link with the title "REVIEW RIDE"
    link = soup.find("a", title="REVIEW RIDE")
    if link:
        confirm_url = link["href"]
        print("Review Ride URL:", confirm_url)
        options = uc.ChromeOptions()
        options.add_extension("./extension.crx")
        driver = uc.Chrome(options=options)
        driver.get(confirm_url)
        time.sleep(3)

        if "login" in driver.current_url:
            email_input = driver.find_element(By.NAME, "email")
            password_input = driver.find_element(By.NAME, "password")

            email_input.send_keys(username)
            password_input.send_keys(login_password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(10)

            # while "login" in driver.current_url:
            #     pass
            # while driver.execute_script("return document.readyState") != "complete":
            #     pass

        driver.quit()
    else:
        print("Review Ride link not found in the email.")

def main():
    while True:
        try:
            mail, email_ids = get_unread_emails()
            if email_ids:
                for email_id in email_ids:
                    html_content = process_email(mail, email_id)
                    if html_content:
                        extract_and_click_link(html_content)
            else:
                print("Not found unread email.")
            mail.close()
            mail.logout()
        except Exception as e:
            print("An error occurred:", e)
        time.sleep(60)


if __name__ == "__main__":
    main()
