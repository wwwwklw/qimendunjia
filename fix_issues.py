#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复三个问题：
1. 文件名加回编号前缀
2. 删除 ![](images/...) 图片引用
3. 添加笔记间交叉链接
"""
import os
import re

SRC_DIR = r"D:\Obsidian-Knowledge\qimendunjia\奇门遁甲知识库\.原始笔记"
OUT_DIR = r"D:\Obsidian-Knowledge\qimendunjia\奇门遁甲知识库\视频笔记"

def get_source_num(frontmatter_source):
    """从 frontmatter 的 sources 数组提取编号"""
    # sources: ["179.奇门遁甲奇门穿壬第七集_笔记.md"]
    m = re.search(r'(\d+)\.', frontmatter_source)
    return int(m.group(1)) if m else None

def get_folder_title(num):
    """从原始笔记文件夹获取标题（去掉编号）"""
    folders = os.listdir(SRC_DIR)
    for f in folders:
        if f.startswith(f'{num}.'):
            return re.sub(r'^\d+\.', '', f).replace('_笔记', '')
    return None

def main():
    renamed = 0
    img_cleaned = 0
    
    for f in sorted(os.listdir(OUT_DIR)):
        if not f.endswith('_矫正版.md'):
            continue
        
        # 跳过已有编号前缀的文件
        if re.match(r'^\d+\.', f):
            continue
        
        old_path = os.path.join(OUT_DIR, f)
        
        with open(old_path, 'r', encoding='utf-8') as fp:
            content = fp.read()
        
        # 从 frontmatter 提取原始编号
        m = re.search(r'sources:\s*\["?(\d+)\.', content)
        if not m:
            print(f"  [SKIP] 无法提取编号: {f}")
            continue
        
        num = int(m.group(1))
        
        # 建立新文件名
        # 从原始文件夹获取正确标题
        title = get_folder_title(num)
        if not title:
            print(f"  [SKIP] 查找原始标题失败: {num}")
            continue
        
        new_name = f"{num}.{title}_矫正版.md"
        new_path = os.path.join(OUT_DIR, new_name)
        
        modified = False
        
        # 删除图片引用 ![](images/xxx.jpg)
        img_pattern = re.compile(r'!\[.*?\]\(images/[^)]+\)\s*\n?')
        img_count = len(img_pattern.findall(content))
        if img_count > 0:
            content = img_pattern.sub('', content)
            modified = True
            img_cleaned += img_count
        
        if modified:
            with open(old_path, 'w', encoding='utf-8') as fp:
                fp.write(content)
        
        os.rename(old_path, new_path)
        renamed += 1
        info = f"  {f} → {new_name}"
        if img_count:
            info += f" [删{img_count}张图]"
        print(info)
    
    print(f"\n重命名: {renamed} 个")
    print(f"删除图片引用: {img_cleaned} 处")

if __name__ == '__main__':
    main()
