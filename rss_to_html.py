import requests
import feedparser
from datetime import datetime

# RSS订阅源URL
rss_url = "https://rsshub.app/51cto/index/recommend"

# 获取RSS数据
response = requests.get(rss_url)
rss_content = response.content

# 解析RSS数据
feed = feedparser.parse(rss_content)

# 生成HTML内容
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RSS Feed</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
        .container { padding: 20px; }
        .feed-item { margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .feed-item h2 { margin: 0 0 10px; }
        .feed-item p { margin: 0 0 10px; }
        .feed-item a { text-decoration: none; color: #007BFF; }
        .feed-item a:hover { text-decoration: underline; }
        .feed-item time { display: block; color: #555; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
"""

# 添加RSS数据到HTML内容
for entry in feed.entries:
    title = entry.title
    link = entry.link
    description = entry.description
    published = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d %H:%M:%S')

    html_content += f"""
    <div class="feed-item">
        <h2><a href="{link}">{title}</a></h2>
        <time>{published}</time>
        <p>{description}</p>
    </div>
    """

html_content += """
    </div>
</body>
</html>
"""

# 保存HTML到文件
with open("rss_feed.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTML 资讯页面已生成：rss_feed.html")
