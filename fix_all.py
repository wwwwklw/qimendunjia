#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""批量修复质量检查发现的所有问题"""
import os
import re
from datetime import datetime

OUT_DIR = r"D:\Obsidian-Knowledge\qimendunjia\奇门遁甲知识库\视频笔记"
SRC_DIR = r"D:\Obsidian-Knowledge\qimendunjia\奇门遁甲知识库\.原始笔记"

# === 1. 术语修正 ===
TERM_FIXES = [
    ('螣蛇', '腾蛇'), ('藤蛇', '腾蛇'),
    ('直符', '值符'), ('直使', '值使'),
    ('商门', '伤门'), ('入目', '入墓'),
    ('金门', '惊门'), ('四门', '死门'),
    ('修门', '休门'), ('声门', '生门'),
    ('马心', '马星'),
    ('畸形', '击刑'),
    ('天府星', '天辅星'),
    ('12剑星', '十二建星'),
]

# === 2. OCR 残余 ===
OCR_FIXES = {
    '': '',      # PDF 项目符号残余，直接删除
    '⼀': '一', '⼈': '人', '⼭': '山', '⽇': '日', '⽕': '火',
    '⼤': '大', '⼋': '八', '⽔': '水', '⽊': '木', '⼿': '手',
    '⼼': '心', '⼝': '口', '⼟': '土', '⽞': '玄', '⾦': '金',
    '⾉': '艮', '⽅': '方', '⽩': '白', '⽂': '文', '⽣': '生',
}

def get_source_info(filename):
    """从原始笔记文件夹获取 source 信息"""
    m = re.match(r'^(\d+)\.(.+)_矫正版\.md$', filename)
    if not m:
        return None, None
    num = m.group(1)
    title = m.group(2)
    # 查找原始文件夹
    for f in os.listdir(SRC_DIR):
        if f.startswith(f'{num}.'):
            return num, f'{f}.md'
    return num, None

def convert_table(content):
    """HTML table → MD table"""
    pattern = re.compile(r'<table>(.*?)</table>', re.DOTALL)
    def convert(m):
        html = m.group(1)
        rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)
        md_rows = []
        for i, row in enumerate(rows):
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            clean = [c.strip() for c in cells]
            md_rows.append('| ' + ' | '.join(clean) + ' |')
            if i == 0:
                md_rows.append('| ' + ' | '.join(['---']*len(clean)) + ' |')
        return '\n'.join(md_rows)
    return pattern.sub(convert, content)

def add_yaml(content, filename):
    """添加 YAML frontmatter"""
    num, source = get_source_info(filename)
    if not source:
        return content
    today = datetime.now().strftime('%Y-%m-%d')
    yaml = f'---\ntags: [视频笔记, 奇门遁甲]\ncreated: {today}\nsources: [{source}]\n---\n\n'
    return yaml + content

def fix_file(filepath, filename):
    """修复单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    fixes_done = []
    
    # YAML
    if not content.startswith('---\n'):
        content = add_yaml(content, filename)
        fixes_done.append('YAML')
    
    # OCR 残余
    for old, new in OCR_FIXES.items():
        if old in content:
            content = content.replace(old, new)
            fixes_done.append(f'OCR:{old}')
    
    # 术语
    for old, new in TERM_FIXES:
        if old in content:
            count = content.count(old)
            content = content.replace(old, new)
            fixes_done.append(f'{old}→{new}({count})')
    
    # HTML 表格
    if '<table>' in content:
        content = convert_table(content)
        fixes_done.append('HTML→MD')
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return fixes_done

def main():
    files = sorted([f for f in os.listdir(OUT_DIR) 
                   if f.endswith('_矫正版.md') and re.match(r'^(1[4-9]\d|2[01]\d|22[01])\.', f)])
    
    total = 0
    for f in files:
        path = os.path.join(OUT_DIR, f)
        fixes = fix_file(path, f)
        if fixes:
            print(f"  {f}: {' | '.join(fixes)}")
            total += 1
    
    print(f"\n修复 {total} 篇笔记")

if __name__ == '__main__':
    main()
