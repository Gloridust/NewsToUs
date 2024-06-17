import os
import requests
import feedparser
from datetime import datetime

def fetch_rss_data(rss_urls):
    feeds = []
    for source_name, rss_url in rss_urls.items():
        response = requests.get(rss_url)
        rss_content = response.content
        feed = feedparser.parse(rss_content)
        for entry in feed.entries:
            feeds.append({
                "title": entry.title,
                "link": entry.link,
                "description": entry.description,
                "published": datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d %H:%M:%S'),
                "source_name": source_name
            })
    return feeds

def generate_html(feeds):
    today_date = datetime.now().strftime('%Y-%m-%d')
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NewsToMe - {today_date}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
            .container {{ padding: 20px; }}
            .feed-item {{ margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
            .feed-item h2 {{ margin: 0 0 10px; }}
            .feed-item p {{ margin: 0 0 10px; }}
            .feed-item a {{ text-decoration: none; color: #007BFF; }}
            .feed-item a:hover {{ text-decoration: underline; }}
            .feed-item time {{ display: block; color: #555; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
    """

    for feed in feeds:
        html_content += f"""
        <div class="feed-item">
            <h2><a href="{feed['link']}">{feed['title']}</a></h2>
            <time>{feed['published']} - {feed['source_name']}</time>
            <p>{feed['description']}</p>
        </div>
        """

    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

def write_html_to_file(html_content, output_dir):
    today_date = datetime.now().strftime('%Y-%m-%d')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f"rss_feed_{today_date}.html")
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"HTML 资讯页面已生成：{output_file}")

def main():
    rss_urls = {
        "51CTO 推荐": "https://rsshub.app/51cto/index/recommend",
        # "智闻 AI": "https://rsshub.app/informedainews/zh-Hans/docs/world-news-daily",
        # "IT之家": "https://rsshub.app/ithome/ranking/24h",
        # "v2ex 最热": "https://rsshub.app/v2ex/topics/latest"
    }
    print("fetching rss to data...")
    feeds = fetch_rss_data(rss_urls)
    print("generating html...")
    html_content = generate_html(feeds)
    return html_content

if __name__ == "__main__":
    html_content = main()
    write_html_to_file(html_content, "./rss-htmls")
