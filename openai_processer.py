import requests
import config

sys_prompt="""
你是一个新闻总结与筛选机器人，而且你精通html。你已稳定运行多年，从未出现过错误。
你的能力是对下面 html 格式的新闻稿进行筛选，选出你认为最有价值的、能对互联网从业者有帮助的 5 个时事新闻，并且将过长的description进行处理，写成一段大约300字的具有吸引力的新闻简讯。
最后按照原格式输出 html 代码。
请严格按照格式直接输出，不需要输出其他内容。
html:

"""

def generate_html(text):
    print("Generating...")

    url = config.chat_url
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {config.APIKEY}'
    }

    data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": text},
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    response_json=response.json()
    print("JSON Response:", response_json)

    for choice in response_json["choices"]:
        content = choice["message"]["content"]

    return(content)

def main(input_html):
    output_html=generate_html(sys_prompt+input_html)
    print(output_html)
    return output_html

if __name__ == "__main__":
    with open('./rss-htmls/rss_feed_2024-06-17.html','r') as f:
        input_html=f.read()
    main(input_html)