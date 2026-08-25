#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""笔记间交叉链接 —— 提取关键术语，匹配相关笔记，添加双向 [[Wikilink]]"""
import os
import re
from collections import Counter

OUT_DIR = r"D:\Obsidian-Knowledge\qimendunjia\奇门遁甲知识库\视频笔记"

# 奇门关键术语集（用于提取笔记主题）
QI_MEN_TERMS = {
    # 八门
    '休门', '生门', '伤门', '杜门', '景门', '死门', '惊门', '开门',
    # 九星
    '天蓬星', '天芮星', '天冲星', '天辅星', '天禽星', '天心星', '天柱星', '天任星', '天英星',
    # 八神
    '值符', '腾蛇', '太阴', '六合', '白虎', '玄武', '九地', '九天', '勾陈', '朱雀',
    # 九宫
    '坎一宫', '坤二宫', '震三宫', '巽四宫', '乾六宫', '兑七宫', '艮八宫', '离九宫',
    # 四害/格局
    '击刑', '入墓', '门迫', '门破', '空亡', '马星',
    # 基础概念
    '旬首', '旬空', '符头', '值使', '排盘', '起局', '定局',
    '阴阳遁', '阳遁', '阴遁', '拆补', '置闰', '超神接气',
    '十二长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养', '长生',
    '十天干', '十二地支',
    '烟波钓叟歌', '终生局', '飞盘', '转盘', '阴盘', '阳盘',
    # 六壬穿壬
    '月将', '神将', '十二建星', '青龙', '贵人', '功曹', '太冲', '天罡',
    '太乙', '胜光', '小吉', '传送', '从魁', '河魁', '大吉', '神后',
    '大六壬', '奇门穿壬',
    # 常见主题
    '应期', '用神', '化解', '四害', '卦象', '纳音', '六亲',
    '风水', '阴宅', '阳宅', '疾病', '婚姻', '财运', '官讼', '考试', '文昌',
    # 天干
    '甲子戊', '甲戌己', '甲申庚', '甲午辛', '甲辰壬', '甲寅癸',
}

def extract_terms(content):
    """从笔记内容中提取出现的奇门术语"""
    found = set()
    for term in QI_MEN_TERMS:
        if term in content:
            found.add(term)
    return found

def get_title_from_filename(filename):
    """从文件名提取简短标题"""
    # 如 "179.奇门遁甲奇门穿壬第七集_矫正版.md" → "奇门穿壬第七集"
    name = filename.replace('_矫正版.md', '')
    name = re.sub(r'^\d+\.', '', name)
    # 截取前20字
    if len(name) > 25:
        name = name[:25] + '…'
    return name

def main():
    # 列出所有矫正版笔记
    all_files = sorted([f for f in os.listdir(OUT_DIR) if f.endswith('_矫正版.md')])
    new_files = [f for f in all_files if re.match(r'^(179|18\d|19\d|20\d|21\d|22[01])\.', f)]
    existing_files = [f for f in all_files if f not in new_files]
    
    print(f"新笔记: {len(new_files)} 篇")
    print(f"已有笔记: {len(existing_files)} 篇")
    print("=" * 60)
    
    # 构建所有笔记的术语索引
    print("构建术语索引...")
    note_terms = {}       # filename → set of terms
    note_titles = {}      # filename → short title
    note_contents = {}    # filename → full content (for new files only)
    
    for f in all_files:
        path = os.path.join(OUT_DIR, f)
        try:
            with open(path, 'r', encoding='utf-8') as fp:
                content = fp.read()
        except:
            continue
        note_terms[f] = extract_terms(content)
        note_titles[f] = get_title_from_filename(f)
        if f in new_files:
            note_contents[f] = content
    
    # 为每篇新笔记找匹配的已有笔记
    print("匹配相关笔记...")
    total_links_added = 0
    
    for new_f in new_files:
        new_terms = note_terms[new_f]
        if not new_terms:
            print(f"  {new_f}: 无关键术语，跳过")
            continue
        
        # 计算与每篇已有笔记的术语重叠数
        matches = []
        for exist_f in existing_files:
            overlap = new_terms & note_terms[exist_f]
            if len(overlap) >= 2:  # 至少2个共同术语
                matches.append((exist_f, len(overlap), overlap))
        
        if not matches:
            print(f"  {new_f}: 无相关笔记")
            continue
        
        # 按重叠数排序，取前5个
        matches.sort(key=lambda x: -x[1])
        top_matches = matches[:5]
        
        # 构建 相关笔记 小节
        related_section = "\n## 相关笔记\n\n"
        common_terms_display = set()
        for mf, count, terms in top_matches:
            common = '、'.join(sorted(list(terms))[:4])
            related_section += f"- [[{mf.replace('.md', '')}]] — 共同涉及{common}\n"
            common_terms_display.update(terms)
        
        # 添加到新笔记末尾
        path = os.path.join(OUT_DIR, new_f)
        content = note_contents[new_f]
        
        # 检查是否已有相关笔记小节
        if '## 相关笔记' not in content:
            content = content.rstrip() + '\n' + related_section
            with open(path, 'w', encoding='utf-8') as fp:
                fp.write(content)
            total_links_added += len(top_matches)
        
        # 反向链接：在匹配的已有笔记中添加新笔记的链接
        for mf, count, terms in top_matches:
            mpath = os.path.join(OUT_DIR, mf)
            with open(mpath, 'r', encoding='utf-8') as fp:
                mcontent = fp.read()
            
            existing_section = mcontent.split('## 相关笔记')
            
            # 检查是否已有该链接
            new_link = f"[[{new_f.replace('.md', '')}]]"
            if new_link in mcontent:
                continue
            
            # 在已有笔记末尾添加
            common = '、'.join(sorted(list(terms))[:3])
            link_line = f"\n- {new_link} — 共同涉及{common}"
            
            if len(existing_section) > 1:
                # 已有相关笔记小节，追加
                mcontent = mcontent.rstrip() + link_line
            else:
                # 新建相关笔记小节
                mcontent = mcontent.rstrip() + '\n\n## 相关笔记\n' + link_line
            
            with open(mpath, 'w', encoding='utf-8') as fp:
                fp.write(mcontent)
        
        # 报告
        term_summary = '、'.join(sorted(list(new_terms))[:5])
        file_summary = ', '.join([f"{note_titles[mf]}({c})" for mf, c, t in top_matches[:3]])
        print(f"  {new_f} [{term_summary}…] → {file_summary}")
    
    print(f"\n{'=' * 60}")
    print(f"完成，添加 {total_links_added} 条交叉链接")

if __name__ == '__main__':
    main()
