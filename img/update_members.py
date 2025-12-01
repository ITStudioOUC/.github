import os
import requests
import re

# 配置部分
ORG_NAME = os.environ['ORG_NAME'] # 从环境变量获取组织名
TOKEN = os.environ['GH_TOKEN']
README_PATH = "profile/README.md" # 你的 README 路径，根据实际情况调整

def get_members():
    url = f"https://api.github.com/orgs/{ORG_NAME}/members"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    members = []
    page = 1
    
    while True:
        # 获取所有分页的成员
        response = requests.get(f"{url}?per_page=100&page={page}", headers=headers)
        if response.status_code != 200:
            print(f"Error fetching members: {response.text}")
            break
        
        data = response.json()
        if not data:
            break
            
        members.extend(data)
        page += 1
        
    return members

def generate_html(members):
    # 生成类似 contributors-readme-action 的圆形头像表格/列表
    html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">\n'
    
    for member in members:
        login = member['login']
        avatar = member['avatar_url']
        profile = member['html_url']
        
        # 样式：圆形头像，宽度 50px，带链接
        html += f'''
    <a href="{profile}" title="{login}">
        <img src="{avatar}" width="50" height="50" style="border-radius: 50%;" alt="{login}">
    </a>'''
        
    html += '\n</div>'
    return html

def update_readme(html_content):
    if not os.path.exists(README_PATH):
        print(f"README not found at {README_PATH}")
        return

    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 使用正则替换标记之间的内容
    pattern = r'(<!-- MEMBERS-LIST:START -->)(.*?)(<!-- MEMBERS-LIST:END -->)'
    replacement = f'\\1\n{html_content}\n\\3'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == "__main__":
    print(f"Fetching members for {ORG_NAME}...")
    members = get_members()
    print(f"Found {len(members)} members.")
    
    html = generate_html(members)
    update_readme(html)
    print("README updated successfully.")
