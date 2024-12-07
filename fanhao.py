import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


def search_torrent_kitty(keyword):
    # Torrent Kitty 的搜索 URL 格式
    base_url = "https://torkitty.com/search/"
    search_url = f"{base_url}{keyword}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

    try:
        # 发送请求
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 提取磁力链接
        results = []
        for row in soup.select("tr"):
            # 提取标题
            title_tag = row.select_one('td.name')
            if not title_tag:
                continue
            title = title_tag.text.strip()
            if title != keyword:
                continue

            # 提取磁力链接
            magnet_tag = row.select_one('td.action a[rel="magnet"]')
            if not magnet_tag:
                continue
            magnet = magnet_tag["href"]

            results.append((title, magnet))

        return results

    except requests.RequestException as e:
        print(f"请求出错：{e}")
        return []


def process_keyword(keyword):
    print(f"正在搜索: {keyword}")
    return search_torrent_kitty(keyword)


if __name__ == "__main__":
    # 读取关键词文件
    try:
        with open("./keyword.txt", "r", encoding="utf-8") as file:
            keywords = [line.strip() for line in file if line.strip()]

        all_results = []

        # 使用线程池并发请求
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(process_keyword, keyword): keyword for keyword in keywords}
            for future in futures:
                keyword = futures[future]
                try:
                    results = future.result()
                    if results:
                        all_results.extend(results)
                    else:
                        print(f"未找到与 '{keyword}' 相关的磁力链接。")
                except Exception as e:
                    print(f"关键字 '{keyword}' 处理时出错：{e}")

        # 写入结果到文件
        with open("magnet.txt", "w", encoding="utf-8") as file:
            for title, magnet in all_results:
                file.write(f"{title}\n{magnet}\n\n")

        print("搜索完成，结果已保存到 magnet.txt 文件中。")

    except FileNotFoundError:
        print("未找到 keyword.txt 文件，请确保文件存在并重新运行程序。")
