#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
借命分镜 CSV v3:摄影质感升级
============================
v2 解决了"PPT 感"病根(锁死词清零),
v3 解决"AI 味太重"病根 — 画出来的图像修图样片,不像真实摄影。

参考:
- OpenAI Cookbook / image2_prompt_guide 黄金公式
- awesome-gpt-image 顶级案例的共同模式

关键洞察:成功 prompt 都用「photorealistic candid / 35mm film / authentic」
         而不是「电影级打光、电影感」
         后者在 MJ 时代有用,在 GPT-image-2 上反而触发"样片修图美学"

通用反修图约束已放入 GUI 模板层(v0.12),CSV 层只负责场景专属质感描述。

策略:
  • 不动"首帧:xxx;尾帧:xxx"(v2 已优化)
  • 在场景主体描述末尾补一个【质感锚 trailer】
  • 每条只加 30-50 字,不让 prompt 超 360 字
"""

import csv, re
from pathlib import Path

SRC = Path("借命_第一集_分镜.csv")
DST = Path("借命_第一集_分镜.csv")

# 按场景类别分配不同的质感锚
# - 动作/人物特写:candid photography + skin detail
# - 空镜/环境:cinematic still + real location feel
# - 夜景:film noir + grain
# - 白天:natural daylight + nothing glamorized

# 6 类质感锚
ANCHOR_NIGHT_ACTION = (
    "摄影风格:photorealistic candid action shot,shot on 35mm film,"
    "motion blur,subtle grain,natural rain-soaked atmosphere;"
    "真实感锚:真实皮肤纹理、湿发贴额、汗水/雨水自然流淌,"
    "不修图不美化,不要 HDR 光晕"
)
ANCHOR_NIGHT_STILL = (
    "摄影风格:cinematic photorealistic still,shot on 35mm film,"
    "long exposure,film grain,rain mist,real street ambience;"
    "真实感锚:像一位摄影师在街角架机位实拍,不是 CG 渲染,不要过饱和"
)
ANCHOR_NIGHT_CLOSEUP = (
    "摄影风格:photorealistic close-up,50mm lens,shallow depth of field,"
    "subtle film grain,dim neon rim light;"
    "真实感锚:可见毛孔、皮肤瑕疵、雨珠质感,不要假皮肤,不要过度锐化"
)
ANCHOR_DAY_DOC = (
    "摄影风格:documentary-style photograph,natural daylight,"
    "slight motion,candid framing,realistic color science;"
    "真实感锚:像手机随拍抓到的生活片段,不要棚拍感,不要过饱和"
)
ANCHOR_INDOOR_WARM = (
    "摄影风格:candid indoor photograph,natural window light,"
    "35mm film feel,warm ambient shadow;"
    "真实感锚:真实皮肤纹理、自然毛发、房间杂物可见,不美化不修图"
)
ANCHOR_TWILIGHT = (
    "摄影风格:cinematic twilight photograph,shot on 35mm film,"
    "natural magic-hour light,subtle film grain;"
    "真实感锚:像纪录片质感,不要过度锐化,不要 HDR"
)

# 每个场景分配锚(按 id 1-30)
SCENE_ANCHORS = {
    # 雨夜段 1-13
    1: ANCHOR_NIGHT_STILL,      # 雨夜远景
    2: ANCHOR_NIGHT_STILL,      # 标题浮现(物件)
    3: ANCHOR_NIGHT_CLOSEUP,    # 巷内负伤
    4: ANCHOR_NIGHT_CLOSEUP,    # 黑卡特写
    5: ANCHOR_NIGHT_ACTION,     # 走出巷口
    6: ANCHOR_NIGHT_STILL,      # 七人现身
    7: ANCHOR_NIGHT_CLOSEUP,    # 举枪书生
    8: ANCHOR_NIGHT_CLOSEUP,    # 刀疤打手
    9: ANCHOR_NIGHT_CLOSEUP,    # 男子怒目
    10: ANCHOR_NIGHT_ACTION,    # 突然前冲
    11: ANCHOR_NIGHT_ACTION,    # 一刀断枪
    12: ANCHOR_NIGHT_ACTION,    # 群起围攻
    13: ANCHOR_NIGHT_CLOSEUP,   # 仰倒凝望
    # 过渡 + 清晨 14-22
    14: ANCHOR_TWILIGHT,        # 夜转晨
    15: ANCHOR_TWILIGHT,        # 晨光初现
    16: ANCHOR_INDOOR_WARM,     # 惊醒坐起
    17: ANCHOR_INDOOR_WARM,     # 对镜凝视
    18: ANCHOR_INDOOR_WARM,     # 一拳入墙
    19: ANCHOR_INDOOR_WARM,     # 翻找枕下
    20: ANCHOR_INDOOR_WARM,     # 学生证
    21: ANCHOR_INDOOR_WARM,     # 手机震动
    22: ANCHOR_INDOOR_WARM,     # 握机沉默
    # 白天段 23-28
    23: ANCHOR_DAY_DOC,         # 出门推门
    24: ANCHOR_DAY_DOC,         # 白昼巷尾
    25: ANCHOR_DAY_DOC,         # 取回黑卡
    26: ANCHOR_DAY_DOC,         # 银行取款
    27: ANCHOR_INDOOR_WARM,     # 网吧键入
    28: ANCHOR_DAY_DOC,         # 中天大厦
    # 黄昏收尾 29-30
    29: ANCHOR_TWILIGHT,        # 苏郁侧影
    30: ANCHOR_TWILIGHT,        # 镜中誓言
}

# 读、改、写
with open(SRC, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

assert len(rows) == 30, f"期望 30 行,实际 {len(rows)}"

modified = 0
for i, r in enumerate(rows, 1):
    anchor = SCENE_ANCHORS.get(i)
    if not anchor:
        continue
    old = r['gpt_prompt']
    
    # 幂等检查:如果已经加过质感锚,跳过
    if '摄影风格:' in old or '真实感锚:' in old:
        print(f"⚠️  场景 {i} 已有质感锚,跳过")
        continue
    
    # 在"首帧:"之前插入质感锚
    m = re.search(r'(首帧[::])', old)
    if not m:
        print(f"⚠️  场景 {i} 没找到'首帧:'标记,在开头附加")
        new = old + ' ' + anchor + '。'
    else:
        # 在"首帧:"之前插入
        pos = m.start()
        new = old[:pos] + anchor + '。' + old[pos:]
    
    r['gpt_prompt'] = new
    modified += 1

print(f"\n✅ 升级完成:{modified}/30 场景加了摄影质感锚")

# 长度复查
lens = [len(r['gpt_prompt']) for r in rows]
print(f"升级后 prompt 平均 {sum(lens)//len(lens)} 字,最短 {min(lens)},最长 {max(lens)}")

# 质感锚覆盖率复查
cov = sum(1 for r in rows if '摄影风格:' in r.get('gpt_prompt',''))
print(f"摄影锚覆盖率: {cov}/30")

# 禁用词继续清零验证(继承 v2)
for w in ['同一机位', '同一构图', '同一角度', '只有细微变化']:
    hits = 0
    for r in rows:
        m = re.search(r'尾帧[::](.+?)(?=【|$)', r.get('gpt_prompt',''))
        if m and w in m.group(1):
            hits += 1
    print(f"  尾帧段里的「{w}」: {hits} 场景(应为 0)")

# 写回
with open(DST, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(rows)

print(f"\n📝 已写入 {DST}")
