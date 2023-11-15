import smtplib
import poplib
from email import parser
import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('user_database.db')
cursor = conn.cursor()

# 创建用户表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE
    )
''')
conn.commit()

# 处理注册的函数
def handle_registration(email_content):
    # 从邮件内容中提取用户邮箱地址
    start_index = email_content.find(':') + 1
    end_index = email_content.find('\n')
    user_email = email_content[start_index:end_index].strip()

    # 将邮箱地址注册为用户
    try:
        cursor.execute('INSERT INTO users (email) VALUES (?)', (user_email,))
        conn.commit()
        print(f"User {user_email} registered successfully.")
    except sqlite3.IntegrityError:
        print(f"User {user_email} is already registered.")

# 处理管理员发送的内容邮件的函数
def handle_admin_email(email_content):
    # 获取所有注册用户的邮箱地址
    cursor.execute('SELECT email FROM users')
    registered_users = [row[0] for row in cursor.fetchall()]

    # 实现将邮件内容发送给所有注册用户的逻辑
    for user_email in registered_users:
        # 发送邮件给用户（这里只是打印信息，实际应用中需要连接到SMTP服务器发送邮件）
        print(f"Sending content email to {user_email}:\n{email_content}")

# 连接到邮件服务器
mail_server = poplib.POP3('your_mail_server')  # 修改为你的邮件服务器地址
mail_server.user('mailme@maneg.life')  # 修改为你的服务账户邮箱
mail_server.pass_('your_password')  # 修改为你的服务账户邮箱密码

# 获取未读邮件
num_messages = len(mail_server.list()[1])
for i in range(num_messages):
    _, msg_data, _ = mail_server.retr(i+1)
    email_content = b'\n'.join(msg_data).decode('utf-8')

    # 检查邮件是注册还是管理员发送的内容
    if email_content.startswith("Register:"):
        handle_registration(email_content)
    elif email_content.startswith("AdminContent:"):
        handle_admin_email(email_content)

# 关闭连接
mail_server.quit()

# 关闭数据库连接
conn.close()
