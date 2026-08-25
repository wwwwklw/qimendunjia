#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""全面检查 147-221 矫正笔记的质量"""
import os
import re

OUT_DIR = r"D:\Obsidian-Knowledge\qimendunjia\奇门遁甲知识库\视频笔记"
VAULT_ROOT = r"D:\Obsidian-Knowledge\qimendunjia\奇门遁甲知识库"

# OCR 残余字符
OCR_RESIDUALS = ['镸', '', '', '⻔', '⻘', '⻰', '⻛', '⻩', '⽊', '⽔', '⻓',
                 '⼀', '⼤', '⼋', '⼈', '⼿', '⼼', '⼝', '⼭', '⼟', '⽕',
                 '⽞', '⾦', '⾉', '⾊', '⽅', '⽩', '⽂', '⽣', '⽉', '⽇']

# 常见术语错误
TERM_ERRORS = {
    '畸形': '击刑', '机型': '击刑',
    '滕蛇': '腾蛇', '藤蛇': '腾蛇', '螣蛇': '腾蛇',
    '直符': '值符', '植符': '值符',
    '直使': '值使', '植使': '值使',
    '入目': '入墓', '入幕': '入墓',
    '巡首': '旬首', '寻首': '旬首',
    '巡空': '旬空',
    '斧头': '符头', '浮头': '符头', 
    '马心': '马星', '马兴': '马星',
    '智润': '置闰', '至润': '置闰',
    '超神节气': '超神接气', '超神接器': '超神接气',
    '木鱼': '沐浴', '牧鱼': '沐浴',
    '官带': '冠带', '冠戴': '冠带',
    '林官': '临官',
    '地旺': '帝旺', '弟旺': '帝旺',
    '对漆拱': '兑七宫', '对漆工': '兑七宫', '对七宫': '兑七宫', '修士宫': '兑七宫',
    '修门': '休门', '声门': '生门', '凯门': '开门',
    '四门': '死门', '商门': '伤门', '度门': '杜门', '堵门': '杜门',
    '井门': '景门', '警门': '景门', '金门': '惊门', '京门': '惊门',
    '天瑞星': '天芮星', '天府星': '天辅星',
    '天棚星': '天蓬星', '天新星': '天心星',
    '天住星': '天柱星', '天人星': '天任星',
    '天充星': '天冲星', '天鹰星': '天英星', '天琴星': '天禽星',
    '白户': '白虎', '百户': '白虎',
    '旋武': '玄武', '悬武': '玄武',
    '就天': '九天', '久天': '九天',
    '六和': '六合', '太音': '太阴', '泰阴': '太阴',
    '沟陈': '勾陈', '钩陈': '勾陈', '猪雀': '朱雀',
    '跟卦': '艮卦', '训卦': '巽卦', '砍卦': '坎卦', '阵卦': '震卦', '对卦': '兑卦',
    '12剑星': '十二建星', '十二剑星': '十二建星',
    '烟波调子科': '烟波钓叟歌', '烟波调子': '烟波钓叟',
}

def find_all_md_files(vault_root):
    """递归查找 vault 中所有 md 文件，返回 {filename: fullpath}"""
    md_map = {}
    for root, dirs, files in os.walk(vault_root):
        # 跳过 .开头的隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if f.endswith('.md'):
                md_map[f] = os.path.join(root, f)
    return md_map

def check_wikilinks(content, all_md_files, note_dir):
    """检查笔记中的 wikilink 是否都能解析"""
    # 提取所有 [[target|alias]] 或 [[target]]
    links = re.findall(r'\[\[([^\]]+)\]\]', content)
    orphan = []
    for link in links:
        # 取链接目标（去掉管道别名）
        target = link.split('|')[0].strip()
        # 目标文件名
        target_file = target + '.md'
        
        # 先在视频笔记目录找
        local_path = os.path.join(note_dir, target_file)
        if os.path.exists(local_path):
            continue
        
        # 再在整个 vault 找
        if target_file in all_md_files:
            continue
        
        orphan.append(link)
    return orphan

def main():
    # 建立 vault 全部 md 文件索引
    print("构建 vault 文件索引...")
    all_md_files = find_all_md_files(VAULT_ROOT)
    print(f"  共 {len(all_md_files)} 个 md 文件")
    
    # 获取 147-221 范围内的笔记
    note_files = sorted([f for f in os.listdir(OUT_DIR) 
                        if f.endswith('_矫正版.md')])
    target_files = []
    for f in note_files:
        m = re.match(r'^(1[4-9]\d|2[01]\d|22[01])\.', f)
        if m:
            target_files.append(f)
    
    print(f"\n检查 {len(target_files)} 篇笔记 (147-221)")
    print("=" * 70)
    
    stats = {
        'no_yaml': [], 'img_remain': [], 'ocr_residual': [],
        'term_errors': [], 'orphan_links': [], 'no_crosslink': [],
        'html_table': [],
    }
    
    for f in target_files:
        path = os.path.join(OUT_DIR, f)
        try:
            with open(path, 'r', encoding='utf-8') as fp:
                content = fp.read()
        except:
            print(f"  [错误] 无法读取: {f}")
            continue
        
        issues = []
        
        # 1. YAML frontmatter
        if not content.startswith('---\n'):
            issues.append('缺YAML')
            stats['no_yaml'].append(f)
        
        # 2. 图片引用残留
        img_count = len(re.findall(r'!\[.*?\]\(images/', content))
        if img_count > 0:
            issues.append(f'{img_count}张图片残留')
            stats['img_remain'].append((f, img_count))
        
        # 3. OCR 残余字符
        ocr_issues = []
        for ch in OCR_RESIDUALS:
            if ch in content:
                count = content.count(ch)
                ocr_issues.append(f'{ch}({count})')
        if ocr_issues:
            issues.append(f'OCR:{",".join(ocr_issues[:3])}')
            stats['ocr_residual'].append((f, ocr_issues))
        
        # 4. 术语错误
        term_issues = []
        for wrong, correct in TERM_ERRORS.items():
            count = content.count(wrong)
            if count > 0:
                term_issues.append(f'"{wrong}"→"{correct}" x{count}')
        if term_issues:
            stats['term_errors'].append((f, term_issues))
            issues.append(f'术语:{len(term_issues)}处')
        
        # 5. 暗节点
        orphan = check_wikilinks(content, all_md_files, OUT_DIR)
        if orphan:
            stats['orphan_links'].append((f, orphan))
            issues.append(f'暗节点:{len(orphan)}个')
        
        # 6. 交叉链接
        if '## 相关笔记' not in content:
            # 只对 179+ 检查（第一批可能本来就没有）
            m = re.match(r'^(1[7-9]\d|2[01]\d|22[01])', f)
            if m and int(m.group(1)) >= 179:
                stats['no_crosslink'].append(f)
                issues.append(f'无相关笔记')
        
        # 7. HTML 表格残留
        if '<table>' in content or '<tr>' in content:
            stats['html_table'].append(f)
            issues.append('HTML表格')
        
        if issues:
            print(f"  {f}: {' | '.join(issues)}")
    
    # 汇总报告
    print("\n" + "=" * 70)
    print("质量检查汇总")
    print("=" * 70)
    
    if stats['no_yaml']:
        print(f"\n❌ 缺YAML frontmatter ({len(stats['no_yaml'])}篇):")
        for f in stats['no_yaml']:
            print(f"    {f}")
    
    if stats['img_remain']:
        total_imgs = sum(x[1] for x in stats['img_remain'])
        print(f"\n❌ 图片引用残留 ({len(stats['img_remain'])}篇, {total_imgs}张):")
        for f, n in stats['img_remain'][:10]:
            print(f"    {f}: {n}张")
        if len(stats['img_remain']) > 10:
            print(f"    ...还有 {len(stats['img_remain'])-10} 篇")
    
    if stats['ocr_residual']:
        print(f"\n❌ OCR残余字符 ({len(stats['ocr_residual'])}篇):")
        for f, issues in stats['ocr_residual'][:10]:
            print(f"    {f}: {', '.join(issues[:5])}")
        if len(stats['ocr_residual']) > 10:
            print(f"    ...还有 {len(stats['ocr_residual'])-10} 篇")
    
    if stats['term_errors']:
        total_terms = sum(len(x[1]) for x in stats['term_errors'])
        print(f"\n❌ 术语错误 ({len(stats['term_errors'])}篇, {total_terms}处):")
        for f, issues in stats['term_errors'][:15]:
            print(f"    {f}:")
            for issue in issues[:3]:
                print(f"      {issue}")
            if len(issues) > 3:
                print(f"      ...还有 {len(issues)-3} 处")
        if len(stats['term_errors']) > 15:
            print(f"    ...还有 {len(stats['term_errors'])-15} 篇")
    
    if stats['orphan_links']:
        total_orphan = sum(len(x[1]) for x in stats['orphan_links'])
        print(f"\n❌ 暗节点 ({len(stats['orphan_links'])}篇, {total_orphan}个):")
        for f, orphan in stats['orphan_links'][:15]:
            print(f"    {f}:")
            for o in orphan[:5]:
                print(f"      [[{o}]]")
            if len(orphan) > 5:
                print(f"      ...还有 {len(orphan)-5} 个")
        if len(stats['orphan_links']) > 15:
            print(f"    ...还有 {len(stats['orphan_links'])-15} 篇")
    
    if stats['no_crosslink']:
        print(f"\n⚠️  无相关笔记 ({len(stats['no_crosslink'])}篇):")
        for f in stats['no_crosslink'][:10]:
            print(f"    {f}")
    
    if stats['html_table']:
        print(f"\n⚠️  HTML表格残留 ({len(stats['html_table'])}篇):")
        for f in stats['html_table'][:10]:
            print(f"    {f}")
    
    # 通过总结
    all_good = all(len(v) == 0 for v in stats.values())
    if all_good:
        print("\n✅ 全部通过！")
    else:
        total_issues = sum(len(v) for v in stats.values())
        print(f"\n总计 {total_issues} 个问题需要修复")

if __name__ == '__main__':
    main()
