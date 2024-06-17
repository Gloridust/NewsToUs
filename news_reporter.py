import openai_processer
import rss_to_html
import os
from datetime import datetime
    
def write_html_to_file(html_content, output_dir):
    today_date = datetime.now().strftime('%Y-%m-%d')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f"rss_feed_{today_date}.html")
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"HTML 资讯页面已生成：{output_file}")

def main():
    input_html=rss_to_html.main()
    output_html=openai_processer.main(input_html)
    write_html_to_file(output_html,"./rss-htmls")
    return output_html
    
if __name__ == "__main__":
    main()