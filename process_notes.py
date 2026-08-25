#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""处理 OCR 修复后的笔记：加 frontmatter、Wikilink、表格转换、输出到视频笔记"""

import os
import re
from datetime import datetime

OCR_FIXED_DIR = r"D:\Obsidian-Knowledge\qimendunjia\.ocr_fixed"
OUTPUT_DIR = r"D:\Obsidian-Knowledge\qimendunjia\奇门遁甲知识库\视频笔记"

# 知识库中实际存在的 .md 文件（用于 Wikilink）
KNOWN_FILES = {
    # 八神
    '玄武': '玄武', '九地': '九地', '九天': '九天', '白虎': '白虎',
    '六合': '六合', '太阴': '太阴', '朱雀': '朱雀', '腾蛇': '腾蛇', '勾陈': '勾陈',
    # 八神概述（用于别名链接）
    '八神概述': '八神概述',
    # 八门概述
    '八门概述': '八门概述',
    # 九星 (individual)
    '天芮星': '天芮星', '天辅星': '天辅星',
    '九星概述': '九星概述',
    # 九宫
    '坎一宫': '坎一宫', '艮八宫': '艮八宫', '兑七宫': '兑七宫',
    '九宫': '九宫',
    # 基础
    '八卦概述': '八卦概述',
    '十天干': '十天干', '十二地支': '十二地支',
    '十二长生': '十二长生', '烟波钓叟歌': '烟波钓叟歌',
    # 格局
    '门迫': '门迫',
    '空亡': '空亡',
    # 排盘
    '起局步骤': '起局步骤',
}

def has_kb_file(term):
    """检查术语在知识库中是否有文件"""
    return term in KNOWN_FILES

def add_wikilinks(text):
    """为常见术语添加 Wikilink（仅首次出现时添加）"""
    # 需要添加链接的术语列表（按优先顺序）
    terms = [
        # 八神（有独立文件）
        ('玄武', '玄武'), ('九地', '九地'), ('九天', '九天'),
        ('白虎', '白虎'), ('六合', '六合'), ('太阴', '太阴'),
        ('朱雀', '朱雀'), ('腾蛇', '腾蛇'), ('勾陈', '勾陈'),
        # 九星（有独立文件）
        ('天芮星', '天芮星'), ('天辅星', '天辅星'),
        # 九宫（有独立文件）
        ('坎一宫', '坎一宫'), ('艮八宫', '艮八宫'),
        ('兑七宫', '兑七宫'), ('巽四宫', None),
        ('离九宫', None), ('坤二宫', None), ('震三宫', None),
        ('乾六宫', None),
        # 基础（有独立文件）
        ('烟波钓叟歌', '烟波钓叟歌'),
        ('门迫', '门迫'), ('空亡', '空亡'),
    ]
    
    # 记录已添加的链接，避免重复
    added = set()
    
    def replace_term(match):
        nonlocal added
        full = match.group(0)
        # 检查前面是否有 [[ 或 后面是否有 ]]（已经在链接中）
        # 通过查看匹配位置前面的字符
        return full  # 简单策略：不处理已经在 wikilink 中的
    
    # 简单标记策略：扫描文本，首次出现时替换，跳过已在 [[ ]] 中的
    lines = text.split('\n')
    result_lines = []
    
    def add_link(line, term, target):
        """在一行中为首次出现的术语添加链接"""
        if term in added:
            return line
        # 检查是否已在 [[...]] 中
        pattern = re.compile(r'(?<!\[\[)' + re.escape(term) + r'(?!\]\])')
        if pattern.search(line):
            line = pattern.sub(f'[[{target}]]', line, count=1)
            added.add(term)
        return line
    
    for line in lines:
        # 跳过 YAML frontmatter 和代码块
        if line.strip().startswith('---') or line.strip().startswith('```'):
            result_lines.append(line)
            continue
        
        # 跳过表格行（用 | 分隔的行）
        if '|' in line and line.strip().startswith('|'):
            result_lines.append(line)
            continue
        
        # 添加 wikilinks
        for term, target in terms:
            if target and term not in added:
                # 检查是否已在 [[...]] 中
                if f'[[{target}]]' in line:
                    added.add(term)
                    continue
                # 避免在已有链接中替换
                escaped = re.escape(term)
                pattern = re.compile(r'(?<!\[\[)' + escaped + r'(?!\]\])')
                if pattern.search(line):
                    line = pattern.sub(f'[[{target}]]', line, count=1)
                    added.add(term)
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)

def convert_table_to_md(content):
    """将 HTML table 转换为 Markdown table，并修复表格内的 Wikilink"""
    # 匹配 <table>...</table>
    pattern = re.compile(r'<table>(.*?)</table>', re.DOTALL)
    
    def convert_match(m):
        html = m.group(1)
        # 提取所有行
        rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)
        md_rows = []
        
        for i, row in enumerate(rows):
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            # 清理单元格内容
            clean_cells = [c.strip() for c in cells]
            md_rows.append('| ' + ' | '.join(clean_cells) + ' |')
            
            # 表头后添加分隔符
            if i == 0:
                md_rows.append('| ' + ' | '.join(['---'] * len(clean_cells)) + ' |')
        
        # 修复表格内的 Wikilink 别名（表格中不能用 | 作为别名分隔符）
        result = '\n'.join(md_rows)
        
        # 找到表格内的 [[file|alias]] 并转换为 [[file]]alias
        def fix_table_link(m2):
            target = m2.group(1)
            alias = m2.group(2)
            return f'[[{target}]]{alias}'
        
        result = re.sub(r'\[\[([^\]]+)\|([^\]]+)\]\]', fix_table_link, result)
        
        return result
    
    return pattern.sub(convert_match, content)

def fix_lingering_issues(content):
    """修复二次脚本中的误替换和其他残余问题"""
    fixes = [
        # 生镸→生门的误替换（应为生长）
        ('土里生门', '土里生长'),
    ]
    for old, new in fixes:
        content = content.replace(old, new)
    return content

def create_frontmatter(title, source_name):
    """创建 YAML frontmatter"""
    today = datetime.now().strftime('%Y-%m-%d')
    return f'''---
tags: [视频笔记, 奇门遁甲]
created: {today}
sources: [{source_name}]
---

'''

def get_output_filename(folder_name):
    """生成输出文件名"""
    # 去掉 _笔记 后的数字串（如 _笔记1785330577）
    name = re.sub(r'_笔记\d*', '', folder_name)
    # 去掉开头的数字序号（如 179.）
    name = re.sub(r'^\d+\.', '', name)
    # 清理禁止字符
    for ch in ['#', '^', '|', ':', '%', '\\', '/', '?', '*', '"', '<', '>', '[', ']']:
        name = name.replace(ch, '')
    # 括号统一全角
    name = name.replace('(', '（').replace(')', '）')
    return f'{name}_矫正版.md'

def process_file(folder_name):
    """处理单个笔记文件"""
    input_path = os.path.join(OCR_FIXED_DIR, folder_name + '_ocr_fixed.md')
    if not os.path.exists(input_path):
        print(f'  [SKIP] 找不到: {input_path}')
        return None
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取原始源文件名
    source_name = folder_name + '.md'
    
    # 修复残余问题
    content = fix_lingering_issues(content)
    
    # 清理 MinerU 页面标记
    content = re.sub(r'## 第\d+页\s*\n?', '', content)
    
    # 转换 HTML 表格为 MD
    content = convert_table_to_md(content)
    
    # 添加 Wikilink
    content = add_wikilinks(content)
    
    # 添加 frontmatter
    title = folder_name
    frontmatter = create_frontmatter(title, source_name)
    content = frontmatter + content
    
    # 输出
    out_name = get_output_filename(folder_name)
    out_path = os.path.join(OUTPUT_DIR, out_name)
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'  [OK] {out_name}')
    return out_path

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    files = sorted([f.replace('_ocr_fixed.md', '') for f in os.listdir(OCR_FIXED_DIR) 
                   if f.endswith('_ocr_fixed.md')])
    
    print(f'共 {len(files)} 个文件待处理')
    print('=' * 60)
    
    for f in files:
        process_file(f)
    
    print('=' * 60)
    print('处理完成')

if __name__ == '__main__':
    main()
