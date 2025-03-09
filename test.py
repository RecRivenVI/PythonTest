import re
import requests
from bs4 import BeautifulSoup

def extract_md_id(url_or_md):
    """提取番剧的 md ID"""
    if url_or_md.isdigit():
        return url_or_md
    
    if "bilibili.com" in url_or_md or "b23.tv" in url_or_md:
        response = requests.get(url_or_md, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            match = re.search(r'www\.bilibili\.com/bangumi/media/md(\d+)', str(soup))
            if match:
                return match.group(1)
    
    return None

def get_official_score(md_id):
    """获取官方评分"""
    url = f"https://api.bilibili.com/pgc/review/user?media_id={md_id}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    data = response.json()
    
    if "result" in data and "media" in data["result"]:
        media = data["result"]["media"]
        return {
            "title": media.get("title", "未知番剧"),
            "score": media.get("rating", {}).get("score", "暂无评分"),
            "count": media.get("rating", {}).get("count", "未知")
        }
    
    return None

def get_user_scores(md_id, review_type="short"):
    """获取用户评分 (短评/长评)"""
    url = f"https://api.bilibili.com/pgc/review/{review_type}/list?media_id={md_id}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    data = response.json()
    
    scores = []
    if data.get("data") and data["data"].get("list"):
        for review in data["data"]["list"]:
            if "score" in review:
                scores.append(review["score"])
    
    return scores

def calculate_real_score(md_id):
    """计算真实平均评分"""
    short_scores = get_user_scores(md_id, "short")
    long_scores = get_user_scores(md_id, "long")
    
    all_scores = short_scores + long_scores
    if not all_scores:
        return "暂无数据"
    
    return round(sum(all_scores) / len(all_scores), 1)

if __name__ == "__main__":
    user_input = input("请输入番剧的 md ID 或链接: ")
    md_id = extract_md_id(user_input)
    
    if not md_id:
        print("无法获取番剧 ID，请检查输入")
    else:
        official_info = get_official_score(md_id)
        real_score = calculate_real_score(md_id)
        
        print(f"番剧名: {official_info['title']}")
        print(f"官方评分: {official_info['score']} (基于 {official_info['count']} 份评分)")
        print(f"真实平均评分: {real_score}")
