import logging
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

from .utils.config_parser import config

logger = logging.getLogger("PyAirLink")


def serverchan(title, desp='', options=None):
    """
    照抄自 https://github.com/easychen/serverchan-demo
    """
    sendkey = config.server_chan()
    options = options if options else {}
    # 判断 sendkey 是否以 'sctp' 开头，并提取数字构造 URL
    if sendkey.startswith('sctp'):
        match = re.match(r'sctp(\d+)t', sendkey)
        if match:
            num = match.group(1)
            url = f'https://{num}.push.ft07.com/send/{sendkey}.send'
        else:
            raise ValueError('Invalid sendkey format for sctp')
    else:
        url = f'https://sctapi.ftqq.com/{sendkey}.send'
    data = {
        'title': title,
        'desp': desp,
        **options
    }
    try:
        response = requests.post(url, json=data)
        if response.ok:
            logger.info(f"serverChan has been pushed, return: {response.json()}")
            return True
        else:
            logger.warning(f"serverChan push failed, return: {response.json()}")
    except Exception as e:
        logger.error(f"serverChan push error: {e}")
    return False


def bark(title, body, options=None):
    """
    使用 Bark 推送消息
    """
    bark_config = config.bark()
    url = f"{bark_config.get('url')}/push"
    key = bark_config.get('key')
    options = options if options else {}
    data = {"title": title, "body": body, "device_key": key, **options}
    try:
        response = requests.post(url, json=data)
        if response.ok:
            logger.info(f"Bark push has been sent, return: {response.json()}")
            return True
        else:
            logger.warning(f"Bark push failed, return: {response.text}")
    except Exception as e:
        logger.error(f"Bark push error: {e}")
    return False


def wecom(title, body, options=None):
    """
    使用企业微信机器人推送消息。
    """
    wecom_config = config.wecom()
    key = wecom_config.get('key')
    if not key:
        logger.error("WeCom push error: KEY is not configured")
        return False

    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"
    options = options if options else {}
    content = f"{title}\n\n{body}" if body else title
    data = {
        "msgtype": "text",
        "text": {
            "content": content,
            **options
        }
    }
    try:
        response = requests.post(url, json=data)
        if response.ok:
            result = response.json()
            if result.get("errcode") == 0:
                logger.info(f"WeCom push has been sent, return: {result}")
                return True
            logger.warning(f"WeCom push failed, return: {result}")
        else:
            logger.warning(f"WeCom push failed, return: {response.text}")
    except Exception as e:
        logger.error(f"WeCom push error: {e}")
    return False


def send_email(subject, body):
    email_account = config.mail()
    try:
        msg = MIMEMultipart()
        msg['From'] = email_account.get('account')
        msg['To'] = email_account.get('mail_to')
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(email_account.get('smtp_server'), email_account.get('smtp_port'), timeout=5)

        if email_account.get('tls'):
            server.starttls()

        server.login(email_account.get('account'), email_account.get('password'))
        server.sendmail(email_account.get('account'), email_account.get('mail_to'), msg.as_string())
        server.quit()

        logger.info(f"Successfully sent email to: {email_account.get('mail_to')}")
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
