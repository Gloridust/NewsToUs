import asyncio
import aiohttp
import feedparser
from datetime import datetime
import openai_processor
import logging

async def fetch_rss_data(rss_urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for source_name, rss_url in rss_urls.items():
            task = asyncio.create_task(fetch_single_rss(session, source_name, rss_url))
            tasks.append(task)
        return await asyncio.gather(*tasks)

async def fetch_single_rss(session, source_name, rss_url):
    try:
        async with session.get(rss_url) as response:
            rss_content = await response.text()
            feed = feedparser.parse(rss_content)
            return [
                {
                    "title": entry.title,
                    "link": entry.link,
                    "description": entry.description,
                    "published": datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d %H:%M:%S'),
                    "source_name": source_name
                }
                for entry in feed.entries
            ]
    except Exception as e:
        logging.error(f"获取 RSS 数据出错 {source_name}: {e}")
        return []

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
        for item in feed:
            html_content += f"""
            <div class="feed-item">
                <h2><a href="{item['link']}">{item['title']}</a></h2>
                <time>{item['published']} - {item['source_name']}</time>
                <p>{item['description']}</p>
            </div>
            """

    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

async def main():
    rss_urls = {
        "51CTO 推荐": "https://rsshub.app/51cto/index/recommend",
        # 可以添加更多的 RSS 源
    }
    logging.info("正在获取 RSS 数据...")
    feeds = await fetch_rss_data(rss_urls)
    logging.info("正在生成 HTML...")
    input_html = generate_html(feeds)
    output_html = await openai_processor.main(input_html)
    return output_html

if __name__ == "__main__":
    asyncio.run(main())