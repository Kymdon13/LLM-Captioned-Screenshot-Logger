import smtplib
from email.mime.text import MIMEText
from email.header import Header

def send_email(sender_email='', sender_password='', receiver_email='', subject='An Email from Python', body='Hello, this is a test email sent from Python!'):
    # 配置 SMTP 服务器
    # 对于 QQ 邮箱，SMTP 服务器是 smtp.qq.com，端口是 465（SSL）或 587（TLS）
    # 对于 163 邮箱，SMTP 服务器是 smtp.163.com，端口是 465（SSL）
    # 请根据你的邮箱类型修改以下配置
    smtp_server = 'smtp.163.com'  # SMTP 服务器地址
    smtp_port = 465               # SMTP 端口号

    # 创建邮件内容
    # MIMEText 用于创建纯文本邮件
    # 'plain' 表示邮件内容是纯文本
    # 'utf-8' 表示邮件内容的编码方式
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['From'] = Header(sender_email)     # 发件人
    msg['To'] = Header(receiver_email)     # 收件人
    msg['Subject'] = Header(subject)       # 邮件主题

    try:
        # 连接到 SMTP 服务器
        # smtplib.SMTP_SSL 用于 SSL 加密的连接，端口通常是 465
        # smtplib.SMTP 用于非 SSL 连接，然后可以使用 starttls() 升级为 TLS，端口通常是 587
        smtp_obj = smtplib.SMTP_SSL(smtp_server, smtp_port)
        
        # 登录到邮箱服务器
        # 这里需要你的邮箱账号和授权码（不是邮箱密码，需要去邮箱设置里开启 SMTP 服务并获取）
        smtp_obj.login(sender_email, sender_password)
        
        # 发送邮件
        # sendmail(发件人邮箱, 收件人邮箱列表, 邮件内容字符串)
        smtp_obj.sendmail(sender_email, [receiver_email], msg.as_string())
        print("邮件发送成功！")
    except smtplib.SMTPException as e:
        print(f"邮件发送失败: {e}")
    finally:
        # 关闭 SMTP 连接
        smtp_obj.quit()
