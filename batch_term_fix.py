#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""批量修复常见术语错误"""
import os
import re

OUTPUT_DIR = r"D:\Obsidian-Knowledge\qimendunjia\奇门遁甲知识库\视频笔记"

TERM_FIXES = [
    ('烟波调子科', '烟波钓叟歌'), ('烟波调子', '烟波钓叟'),
    ('12剑星', '十二建星'), ('十二剑星', '十二建星'), ('12建星', '十二建星'),
    ('丑为阴木', '丑为阴土'), ('丑属阴木', '丑属阴土'),
    ('土里生门', '土里生长'),
    ('跟卦', '艮卦'), ('训卦', '巽卦'), ('砍卦', '坎卦'),
    ('阵卦', '震卦'), ('对卦', '兑卦'),
    ('银巳', '寅巳'), ('寅四', '寅巳'),
    ('金门', '惊门'), ('京门', '惊门'), ('度门', '杜门'), ('堵门', '杜门'),
    ('井门', '景门'), ('警门', '景门'), ('四门', '死门'),
    ('商门', '伤门'), ('修门', '休门'), ('声门', '生门'), ('凯门', '开门'),
    ('天瑞星', '天芮星'), ('天府星', '天辅星'), ('天棚星', '天蓬星'),
    ('天新星', '天心星'), ('天住星', '天柱星'), ('天人星', '天任星'),
    ('天充星', '天冲星'), ('天鹰星', '天英星'), ('天琴星', '天禽星'),
    ('滕蛇', '腾蛇'), ('藤蛇', '腾蛇'), ('螣蛇', '腾蛇'),
    ('白户', '白虎'), ('百户', '白虎'),
    ('旋武', '玄武'), ('悬武', '玄武'),
    ('就天', '九天'), ('久天', '九天'),
    ('六和', '六合'), ('太音', '太阴'), ('泰阴', '太阴'),
    ('沟陈', '勾陈'), ('钩陈', '勾陈'), ('猪雀', '朱雀'),
    ('直符', '值符'), ('植符', '值符'), ('直使', '值使'), ('植使', '值使'),
    ('入目', '入墓'), ('入幕', '入墓'),
    ('巡首', '旬首'), ('寻首', '旬首'), ('巡空', '旬空'),
    ('斧头', '符头'), ('浮头', '符头'),
    ('马心', '马星'), ('马兴', '马星'),
    ('子毛刑', '子卯刑'), ('子某刑', '子卯刑'),
    ('智润', '置闰'), ('至润', '置闰'),
    ('超神节气', '超神接气'), ('超神接器', '超神接气'),
    ('木鱼', '沐浴'), ('牧鱼', '沐浴'),
    ('官带', '冠带'), ('冠戴', '冠带'),
    ('林官', '临官'), ('地旺', '帝旺'), ('弟旺', '帝旺'),
    ('对漆拱', '兑七宫'), ('对漆工', '兑七宫'), ('对七宫', '兑七宫'),
    ('修士宫', '兑七宫'),
    ('畸形', '击刑'), ('机型', '击刑'),
]

def main():
    files = sorted(os.listdir(OUTPUT_DIR))
    new_only = []
    for f in files:
        if not f.endswith('_矫正版.md'):
            continue
        basename = f.replace('_矫正版.md', '')
        m = re.match(r'^(\d+)\.', basename)
        if m and int(m.group(1)) <= 177:
            continue
        new_only.append(f)
    
    print(f'检查 {len(new_only)} 个新文件')
    print('=' * 60)
    
    total_fixes = 0
    for f in new_only:
        path = os.path.join(OUTPUT_DIR, f)
        with open(path, 'r', encoding='utf-8') as fp:
            content = fp.read()
        
        original = content
        file_changes = []
        for old, new in TERM_FIXES:
            count = content.count(old)
            if count > 0:
                content = content.replace(old, new)
                file_changes.append((old, new, count))
        
        if file_changes:
            with open(path, 'w', encoding='utf-8') as fp:
                fp.write(content)
            print(f'\n  {f}:')
            for old, new, count in file_changes:
                print(f'    "{old}" → "{new}" x{count}')
                total_fixes += count
    
    print(f'\n{"=" * 60}')
    print(f'总计修正 {total_fixes} 处')

if __name__ == '__main__':
    main()
