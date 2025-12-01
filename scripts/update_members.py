import os
import requests
import re
import math

# 配置部分
ORG_NAME = os.environ['ORG_NAME']
TOKEN = os.environ['GH_TOKEN']
README_PATH = "profile/README.md"
COLUMNS = 6  # 你想要一行显示几个成员？

def get_members():
    url = f"https://api.github.com/orgs/{ORG_NAME}/members"
    headers = {
        "Authorization": f"Bearer {TOKEN}", # Fine-grained token 使用 Bearer 也行，token 也可以
        "Accept": "application/vnd.github.v3+json"
    }
    members = []
    page = 1
    
    while True:
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

def generate_markdown_table(members):
    if not members:
        return "No members found."

    # 1. 初始化表格头
    # 表头留空即可，或者你可以写 "Avatar" 之类的，这里为了美观留空
    # 语法: |   |   |   |   |   |
    header = "|" + " |" * COLUMNS + "\n"
    
    # 2. 分割线 (居中对齐 :---:)
    # 语法: | :---: | :---: | ...
    separator = "|" + " :---: |" * COLUMNS + "\n"
    
    body = ""
    
    # 3. 遍历成员，按每行 COLUMNS 个进行切片
    total_members = len(members)
    # 计算需要多少行
    num_rows = math.ceil(total_members / COLUMNS)

    for row_idx in range(num_rows):
        row_str = "|"
        
        # 获取当前行的成员切片
        start = row_idx * COLUMNS
        end = start + COLUMNS
        row_members = members[start:end]
        
        for member in row_members:
            login = member['login']
            avatar = member['avatar_url']
            profile = member['html_url']
            
            # 核心单元格内容构造
            # <br> 用于换行，<img> 默认就是方形的，不加 border-radius 即可
            # width="100px" 控制大小，防止图片太大撑爆表格
            cell_content = (
                f'<a href="{profile}">'
                f'<img src="{avatar}" width="100px" alt="{login}">'
                f'</a><br>'
                f'<a href="{profile}"><b>{login}</b></a>'
            )
            
            row_str += f" {cell_content} |"
        
        # 如果最后一行不满 COLUMNS 个，需要补齐空的单元格，否则 Markdown 表格会乱
        missing_cells = COLUMNS - len(row_members)
        if missing_cells > 0:
            row_str += " |" * missing_cells
            
        row_str += "\n"
        body += row_str
            
    return header + separator + body

def update_readme(content):
    if not os.path.exists(README_PATH):
        print(f"README not found at {README_PATH}")
        return

    with open(README_PATH, 'r', encoding='utf-8') as f:
        old_content = f.read()

    # 正则替换 <!-- MEMBERS-LIST:START --> 和 END 之间的内容
    pattern = r'(<!-- MEMBERS-LIST:START -->)(.*?)(<!-- MEMBERS-LIST:END -->)'
    # 注意：Markdown 表格前后最好留空行，确保渲染正常
    replacement = f'\\1\n\n{content}\n\n\\3'
    
    new_content = re.sub(pattern, replacement, old_content, flags=re.DOTALL)
    
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == "__main__":
    print(f"Fetching members for {ORG_NAME}...")
    members = get_members()
    print(f"Found {len(members)} members.")
    
    # 按名字排序（可选）
    members.sort(key=lambda x: x['login'].lower())
    
    table_content = generate_markdown_table(members)
    update_readme(table_content)
    print("README updated successfully.")
