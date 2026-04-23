#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI Wan 2.2 首尾帧批量生成工具(GUI 版)
===========================================
v0.13 更新日志:
  - 📚 对齐:基于 OpenAI 官方 gpt-image-2 Cookbook(2026-04-21)做模板微调
    · 官方原话:"For wide, cinematic, low-light, rain, or neon scenes,
      add extra detail about scale, atmosphere, and color so the model
      does not trade mood for surface realism."
    · 雨夜场景模板补 scale(远近尺度)+ atmosphere(空气质感)说明
    · "No glamorization, no heavy retouching" 改为官方原文措辞
    · photorealistic 关键词提前放置,增强触发真实感模式
    · 加入 composition cues:framing + viewpoint + lighting/mood

v0.12 更新日志:
  - 🎯 升级:4 个首尾帧模板加入「摄影质感锚定」+「反修图指令」
    · 参考 GPT-image-2 官方 Cookbook + awesome-gpt-image 顶级案例的共性
    · 旧模板"电影级/写实风格"→ 新模板"photorealistic candid / 35mm film / authentic slice"
    · 加入"no glamorization / no over-retouch / no watermark"等 negative 约束
    · 强调"中国都市"锚定,双保险避免日式霓虹文字
    · 首帧加「构图中性,为尾帧运动留白」,尾帧加「differ from start frame visibly」

v0.11 更新日志:
  - 🆕 新增:🔄 每场景新开对话 — 批量 / 单独 GPT 生图时,每个场景画完首尾帧后
    自动点 GPT 网页的「新聊天」按钮,开干净对话继续下一场景
    · 目的:隔离上下文,避免长对话污染导致后续场景画风漂移 / 记错设定
    · UI:素材库行右侧新增复选框,默认开启
    · 多重选择器兜底(aria-label / data-testid / nav a[href="/"])
    · 最后一个场景不新开(省一次点击)

v0.10 更新日志:
  - 🔧 修复:空镜 / 人物镜头首尾帧「PPT 感」问题 — 改写硬性要求模板
    · 旧模板里尾帧还写着「同一机位同一构图」「只有细微变化」,GPT 画双胞胎导致 Wan 2.2 插值无运动
    · 新模板要求首尾必须命中差异(空镜 3 轴 2 命中、人物镜头 2 轴 1 命中)
    · 明确禁用词:同一机位、同一构图、略、稍微、基本不变、几乎相同
  - 🆕 新增:⬜ 空镜模板 按钮 — AI 助手栏新增,可在 GUI 里编辑 4 个首尾帧模板
    · 首帧·空镜 / 首帧·人物 / 尾帧·空镜 / 尾帧·人物 分 4 个 tab
    · 支持恢复默认、保存到 config.json,下次启动自动加载
  - 🆕 新增:📥 GPT 图目录 输入框 — 彻底干掉每次批量生图的弹窗
    · 填好后记忆到 config.json,下次不再弹窗直接用
    · 留空才会弹窗(保留旧行为做兜底)

v0.9 更新日志:
  - 修复:📂 配置文件/素材库/预设文件 路径改为脚本所在目录(SCRIPT_DIR),
    从任何工作目录启动都能正确读取配置
  - 修复:🔍 素材库自动匹配角色图 — 导入 CSV 后自动扫描素材库,
    根据 prompt 中的角色名匹配参考图并在日志中显示结果
  - 新增:📁 素材库递归扫描 — 支持子文件夹内的图片,不再只读根目录
  - 新增:⏸ 批量 GPT 生图支持暂停/继续 — 新增「暂停」「继续」按钮
  - 新增:🎯 单独 GPT 生图 — 右键菜单可对选中场景单独生成首尾帧
  - 新增:▶ 单独生成视频 — 右键菜单可对选中场景单独提交 ComfyUI 生成
  - 新增:🔍 自动匹配素材按钮 — 批量检查所有场景的角色匹配情况
  - 优化:GPT 批量生图增加进度条显示
  - 优化:导入 CSV 后自动触发素材匹配检查

v0.8 更新日志:
  - 改进:🖼 批量 GPT 生图 — 拆成「两次请求」流程,提高出图成功率
    · 原流程:一次发送 prompt,要求 GPT 同时生成首帧 + 尾帧(共 2 张)
      实际观察到 GPT 经常只生成 1 张,或者把两帧合并成一张拼接图输出
    · 新流程:先发 prompt A 只要首帧(1 张),等图到手回填 start,
      再发 prompt B 基于上一张要尾帧(1 张,强调同一场景同一构图),
      等图到手回填 end
    · 更稳定,同时两次请求之间 GPT 能基于 "上一张图" 生成更一致的尾帧
  - 改进:📐 默认方向改为横屏 16:9(960×544)
    · 新项目更适合做横版短剧/解说视频
    · 竖屏 9:16 仍可一键切换
  - 说明:此版本不修改 workflow 本身的分辨率行为,只改 UI 默认值和 GPT 请求文案

v0.7 更新日志:
  - 新增:📐 分辨率设置 UI — 横屏/竖屏/方图切换,宽高帧数可在主界面直接改
    · 节点配置第 2 行:竖屏 9:16 / 横屏 16:9 / 方图 1:1 / 自定义 下拉
    · 扫描节点时自动读取 workflow 里的分辨率回填 UI
    · 批量运行时所有 WanFirstLastFrameToVideo 类节点的 width/height/length 自动同步
    · 尺寸设置持久化到 config.json
  - 新增:🖼 批量 GPT 生图 — 一键让 GPT 网页根据任务列表批量画图
    · 自动注入色板前缀 + 素材库匹配参考图 + 等图 + 下载 + 回填首尾帧
    · 任务列表新增「批量 GPT 生图」按钮
  - 新增:CSV 「gpt_prompt」列 — 给 GPT 画图用的提示词可独立编辑/存盘
    · 场景编辑对话框加「GPT 提示词」文本框(留空则 fallback 到主 prompt)
    · CSV 导入导出增加 gpt_prompt 列

v0.6 更新日志:
  - 新增:🎨 色彩锚点 — 统一分镜色彩,解决 AI 画图时段色彩漂移问题
    · 6 个预设色板(雨夜/过渡/清晨/白天/黄昏/室内夜)
    · 小说改编 AI 自动为每格分配色板
    · 发送提示词到 ComfyUI / GPT 时自动注入色板锚点
    · 场景表新增「🎨」列,场景编辑对话框加色板下拉
    · 色彩锚点管理对话框(增删改/应用到选中/自动检测/恢复默认/预览)

v0.5 更新日志:
  - 新增:主界面独立按钮「📝 GPT 提示词库」— 不用挂 GPT 网页也能管理
  - 优化:提示词库按钮放到 AI 助手栏,更显眼
  - 修复:没启动浏览器时提示词依然可编辑 / 复制

v0.4 更新日志:
  - 新增:素材库管理 — 按文件名存人物/物品图
  - 新增:智能匹配 — 从提示词提取名字自动找图
  - 新增:GPT 网页自动上传参考图
  - 新增:手动提示词库(GPT + Wan 2.2)

v0.3 更新日志:
  - 新增:三种 Chrome 启动模式(attach / standalone / temp)
  - 新增:Chrome 启动失败的诊断与引导

v0.2 更新日志:
  - 新增:OpenAI LLM 集成、GPT 网页挂载

v0.1 更新日志:
  - 新增:拖拽图片、双击预览、版本号

依赖:
  必需:Python 3.8+(Tkinter 自带)
  可选:
    - pip install tkinterdnd2   启用原生文件拖拽
    - pip install selenium      启用 GPT 网页控制
运行:python comfy_wan22_gui.py
"""

__version__ = "0.13"

import os
import sys
import re
import json
import csv
import time
import uuid
import queue
import shutil
import threading
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# 可选依赖 1:拖拽
HAS_DND = False
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    pass

# 可选依赖 2:selenium(GPT 网页控制)
HAS_SELENIUM = False
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    pass


# ============== 脚本目录(所有相对路径基于此,不依赖 CWD) ==============
SCRIPT_DIR = Path(__file__).resolve().parent

# ============== 默认配置 ==============
DEFAULT_HOST = "127.0.0.1:8188"
DEFAULT_OUTPUT_DIR = str(SCRIPT_DIR / "videos_output")
POLL_INTERVAL = 3
TIMEOUT_SECS = 3600
CLIENT_ID = str(uuid.uuid4())
CONFIG_FILE = str(SCRIPT_DIR / "wan22_gui_config.json")

# ============== v0.10 首尾帧硬性要求模板(4 个)==============
# 架构沿用 v0.8+ 的两次请求模式:先首帧(A)再尾帧(B)
# 病根在 B 请求的尾帧模板 — 以前写着「同一机位同一构图、只有细微变化」
# 导致 GPT 画双胞胎,Wan 2.2 首尾插值计算无位移 → PPT 感
# 把两张图的差异要求写到尾帧模板里,而不是硬要求「几乎相同」

DEFAULT_START_EMPTY_TMPL = (
    "━━━━━━━━━━━━━━━━━━━━━━━\n"
    "Generate one image (wide 16:9 landscape).\n"
    "请根据以上描述,生成【首帧图】一张(横屏 16:9)。\n\n"
    "【⚠️ 这是纯环境空镜,硬性要求】\n"
    "1. ⭐ 本次【只要 1 张图】,不要生成两张拼接图\n"
    "2. ❌❌❌ 画面中绝对不得出现任何人物、剪影、背影、手、脸或人影 ❌❌❌\n"
    "3. 只拍建筑、街道、天空、云层、水面、雨幕、室内陈设、物品等环境元素\n"
    "4. ❌ 不要添加描述里【没有提到】的建筑、文字招牌、道具\n"
    "5. ❌ 不要出现日文/韩文招牌文字,故事背景是【中国都市 Chinese city】\n"
    "6. 📐 构图请预留视觉变化空间(主体不要填满画面,给尾帧相机运动留位置)\n\n"
    "【Photography style — anchor (official gpt-image-2 phrasing)】\n"
    "  • Shot like a photorealistic cinematic still, captured on 35mm film.\n"
    "  • Natural lighting, subtle film grain, authentic atmosphere.\n"
    "  • Describe real physical detail: wet pavement reflections, visible raindrops\n"
    "    on surfaces, mist hanging in the air, neon glow scatter in humid air.\n"
    "  • Scale & atmosphere cues(官方针对雨夜/霓虹场景必需):\n"
    "    — specify the distance from camera to subject (e.g. ~15m / mid-shot)\n"
    "    — specify air humidity, street damp, how far neon light travels\n\n"
    "【Constraints — what to avoid (official wording)】\n"
    "  ❌ No glamorization, no heavy retouching.\n"
    "  ❌ No HDR-like glow, no over-saturation, no plastic CGI look.\n"
    "  ❌ No watermark, no extra text, no logos.\n"
    "  ❌ Avoid cinematic color grading that trades mood for realism."
)

DEFAULT_START_PEOPLE_TMPL = (
    "━━━━━━━━━━━━━━━━━━━━━━━\n"
    "Generate one image (wide 16:9 landscape).\n"
    "请根据以上描述,生成【首帧图】一张(横屏 16:9)。\n\n"
    "【硬性要求】\n"
    "1. ⭐ 本次【只要 1 张图】,不要生成两张拼接图,也不要首尾帧并排\n"
    "2. ❌ 不要添加描述里【没有提到】的人物、道具、建筑、文字招牌\n"
    "3. ❌ 不要出现日文/韩文招牌文字,故事背景是【中国都市 Chinese city】\n"
    "4. ✅ 上传的参考图是角色/道具的外观参考,必须严格遵循其外貌特征\n"
    "5. ✅ 这张图用于后续尾帧的构图基准,需场景/人物特征清晰可辨\n"
    "6. 📐 构图请预留动作变化空间(给尾帧里人物动作或相机运动留余地)\n\n"
    "【Photography style — anchor (official gpt-image-2 phrasing)】\n"
    "  • Shot like a photorealistic candid photograph, captured on 35mm film,\n"
    "    50mm lens, eye-level or slightly off-angle, shallow depth of field,\n"
    "    subtle film grain, honest and unposed.\n"
    "  • Render real skin texture with visible wrinkles, pores, sun/weather texture,\n"
    "    imperfect hair strands, worn fabric, everyday detail.\n"
    "  • Composition cues: specify framing(close-up/medium/wide),\n"
    "    viewpoint(eye-level/low-angle), lighting mood(soft diffuse / harsh rim).\n\n"
    "【Constraints — official wording, important】\n"
    "  ❌ No glamorization.\n"
    "  ❌ No heavy retouching.\n"
    "  ❌ No plastic/smoothed skin, no perfect symmetry, no airbrush look.\n"
    "  ❌ No cinematic color grading, no movie-poster styling.\n"
    "  ❌ No watermark, no extra text, no logos."
)

DEFAULT_END_EMPTY_TMPL = (
    "━━━━━━━━━━━━━━━━━━━━━━━\n"
    "Generate one image (wide 16:9 landscape) based on the first frame you just made.\n"
    "请基于你【刚刚生成的首帧图】,生成对应的【尾帧图】一张(横屏 16:9)。\n\n"
    "【⚠️ 这是纯环境空镜,硬性要求】\n"
    "1. ⭐ 本次【只要 1 张图】,不要生成两张拼接图\n"
    "2. ❌❌❌ 画面中仍然绝对不得出现任何人物、剪影、背影、手、脸或人影 ❌❌❌\n"
    "3. ✅ 保持首帧的场景空间、建筑位置、物体摆放不变(是同一个地方的下一瞬间)\n"
    "4. ❌ 不要添加首帧【没有出现】的建筑、文字招牌、道具\n"
    "5. ❌ 不要出现日文/韩文招牌文字\n\n"
    "【Preserve list — 继承首帧,不要漂移(official edit pattern)】\n"
    "  ✅ Keep the same photography style (photorealistic cinematic still, 35mm).\n"
    "  ✅ Keep the same color temperature, grain density, and lens character.\n"
    "  ✅ Keep the same building layout, object positions, spatial geometry.\n"
    "  ✅ Keep camera model/sensor feel consistent — same photographer, next moment.\n\n"
    "【⚠️ Change list — 首尾帧差异硬性要求(Wan 2.2 插值必需)】\n"
    "Meet at least TWO of the three axes below, each described explicitly:\n"
    "  ① Camera motion: dolly / push / pull / pan / tilt / crane\n"
    "     — specify direction AND distance (e.g. push-in 10% of frame width)\n"
    "  ② Weather/light: give 起始→终末 values\n"
    "     (rain light→heavy, mist thin→dense, neon flicker off→on)\n"
    "  ③ Dynamic elements: ripples spreading, light patches shifting,\n"
    "     branches moving in wind, cloud drift across ~N% of frame\n\n"
    "⛔ 禁用词(出现任一就等于没动):\n"
    "  「同一机位」「同一构图」「同一角度」「只有细微变化」「几乎相同」「基本不变」\n\n"
    "【Constraints】\n"
    "  ❌ No glamorization, no heavy retouching.\n"
    "  ❌ No HDR glow, no over-saturation.\n"
    "  ❌ No watermark, no extra text.\n\n"
    "🔍 Self-check: 首尾放一起能一眼看出相机动了/天气变了吗?不能就增强差异。"
)

DEFAULT_END_PEOPLE_TMPL = (
    "━━━━━━━━━━━━━━━━━━━━━━━\n"
    "Generate one image (wide 16:9 landscape) based on the first frame you just made.\n"
    "请基于你【刚刚生成的首帧图】,生成对应的【尾帧图】一张(横屏 16:9)。\n\n"
    "【硬性要求】\n"
    "1. ⭐ 本次【只要 1 张图】,不要生成两张拼接图\n"
    "2. ✅ 保持首帧的场景、色调、人物造型、服装完全一致(是同一瞬间的下一帧)\n"
    "3. ✅ 人物特征必须与首帧及参考图一致(脸型/服装/发型不得改)\n"
    "4. ❌ 不要换场景(比如一张街景一张室内)\n"
    "5. ❌ 不要出现日文/韩文招牌文字\n\n"
    "【Preserve list — 不要漂移(official edit pattern)】\n"
    "  ✅ Preserve identity: face, facial features, skin tone,\n"
    "     body shape, hairstyle, exact likeness from first frame.\n"
    "  ✅ Preserve photography style: photorealistic candid, 35mm film,\n"
    "     50mm lens, same grain density, same lighting direction.\n"
    "  ✅ Preserve scene: camera angle, framing, background objects.\n"
    "  ✅ Same photographer, next moment — like the next shutter click.\n\n"
    "【⚠️ Change list — 首尾帧差异(Wan 2.2 插值必需)】\n"
    "Meet at least ONE of these two axes, both is better:\n"
    "  ① Camera motion: dolly / push / pull / pan / tilt\n"
    "     — specify direction AND amount (e.g. slight push-in ~15cm)\n"
    "     — 若需保持静止机位,明确写 'camera locked, no motion'\n"
    "  ② Subject action/expression: first frame and last frame should be\n"
    "     the 【start】 and 【end】 points of a single action arc\n"
    "     (head-down → head-up, fist-relaxed → fist-clenched, etc.)\n"
    "     — not two near-identical moments.\n\n"
    "⛔ 禁用词(会导致 Wan 2.2 插值无运动):\n"
    "  「同一机位同一构图」「只有细微变化」「几乎相同」「基本不变」\n\n"
    "【Constraints】\n"
    "  ❌ No glamorization.\n"
    "  ❌ No heavy retouching, no plastic skin, no over-sharpening.\n"
    "  ❌ No watermark, no extra text, no logos."
)

# OpenAI 兼容 API 默认配置(支持中转和自建站)
DEFAULT_OPENAI_BASE = "https://api.openai.com/v1"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_GPT_WEB_URL = "https://gpt.aimonkey.plus/"


# Wan 2.2 动作指令编写原则(GUI 里直接可查)
WAN22_TIPS = """━━━━━━━━━━ Wan 2.2 动作指令编写原则 ━━━━━━━━━━

【核心 5 原则】
① 动词优先:推近 / 旋转 / 上升 / 飘落 / 握紧
② 控制在 20 字以内(中文)或 15 词以内(英文)
③ 镜头 + 主体动作 + 环境 三要素齐全
④ 避免抽象词:不要写"情绪变化""氛围浓郁"
⑤ 强度词加量:缓慢 / 快速 / 猛然 / 渐渐

【✅ 好指令示范】
· 镜头缓慢推近 雨丝斜飘 角色抬头
· 瞳孔骤缩瞬间翻滚 武士刀钉入墙面颤动
· 夜空转为晨光 云层流动 雨丝渐停
· 角色猛然前冲 拖出残影 水花四溅

【❌ 别这样写】
· "角色变得很愤怒"      → 改:眉头皱起 瞳孔收缩
· "氛围紧张起来"        → 改:雨势加大 闪电划过
· "表情很复杂"          → 改:嘴角下垂 眼神闪烁
· "慢慢慢慢地移动"      → 改:缓慢移动

【常用词汇表】
镜头:推近 / 拉远 / 上升 / 下降 / 旋转 / 跟随 / 俯视 / 仰视
速度:慢动作 / 快速 / 猛然 / 缓慢 / 渐渐
环境:雨丝飘落 / 尘土飞扬 / 光线穿透 / 风吹 / 烟雾 / 火花

【时长建议】
· 动作戏(冲刺、挥刀): 3 秒
· 情感戏(倒下、凝视): 4-5 秒
· 过渡戏(时空转场):   5 秒
"""


# ============== HTTP / ComfyUI API ==============
def _http_post(host, path, data, is_json=True):
    url = f"http://{host}{path}"
    body = json.dumps(data).encode("utf-8") if is_json else data
    headers = {"Content-Type": "application/json"} if is_json else {}
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def _http_get_json(host, path):
    url = f"http://{host}{path}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read())


def _http_get_bytes(host, path):
    url = f"http://{host}{path}"
    with urllib.request.urlopen(url, timeout=300) as resp:
        return resp.read()


def upload_image(host, local_path):
    local_path = Path(local_path)
    if not local_path.exists():
        raise FileNotFoundError(f"图片不存在: {local_path}")
    boundary = f"----ComfyBoundary{uuid.uuid4().hex}"
    filename = local_path.name
    with open(local_path, "rb") as f:
        file_bytes = f.read()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + file_bytes + (
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="overwrite"\r\n\r\n'
        f"true\r\n--{boundary}--\r\n"
    ).encode("utf-8")
    req = urllib.request.Request(
        f"http://{host}/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
    return result.get("name", filename)


def queue_prompt(host, workflow_api):
    r = _http_post(host, "/prompt", {"prompt": workflow_api, "client_id": CLIENT_ID})
    if "prompt_id" not in r:
        raise RuntimeError(f"提交失败: {r}")
    return r["prompt_id"]


def wait_done(host, prompt_id, log_cb=None):
    start = time.time()
    while True:
        if time.time() - start > TIMEOUT_SECS:
            raise TimeoutError(f"任务 {prompt_id} 超时")
        try:
            h = _http_get_json(host, f"/history/{prompt_id}")
        except urllib.error.HTTPError:
            h = {}
        if prompt_id in h:
            return h[prompt_id]
        if log_cb:
            log_cb(f"   ⏳ 排队/生成中... ({int(time.time()-start)}s)")
        time.sleep(POLL_INTERVAL)


def find_output_videos(history):
    videos = []
    outputs = history.get("outputs", {})
    for node_id, out in outputs.items():
        for key in ("gifs", "videos", "files", "images"):
            for item in out.get(key, []) or []:
                name = item.get("filename", "")
                if name.lower().endswith((".mp4", ".webm", ".mkv", ".gif", ".mov")):
                    videos.append(item)
    return videos


def download_output(host, item, save_dir, rename_to=None):
    q = urllib.parse.urlencode({
        "filename":  item["filename"],
        "subfolder": item.get("subfolder", ""),
        "type":      item.get("type", "output"),
    })
    data = _http_get_bytes(host, f"/view?{q}")
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    target = Path(save_dir) / (rename_to or item["filename"])
    with open(target, "wb") as f:
        f.write(data)
    return target


# ============== 工作流改写 ==============
class WorkflowFormatError(Exception):
    pass


def load_workflow_api(path):
    """
    加载工作流 JSON。
    - API 格式: 顶层是 dict,key 是节点ID字符串,value 有 class_type 字段
    - UI  格式: 顶层是 dict,含 "nodes" (list)、"links" (list) 等字段
    本函数只接受 API 格式,遇到 UI 格式会抛出清晰的错误。
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise WorkflowFormatError("JSON 根元素必须是对象")

    # UI 格式特征
    if "nodes" in data and isinstance(data.get("nodes"), list):
        raise WorkflowFormatError(
            "⚠️ 你加载的是 UI 格式 JSON(ComfyUI 画布布局),不能直接执行。\n\n"
            "✅ 正确做法(汉化版):\n"
            "  1. 在 ComfyUI 里加载这个工作流\n"
            "  2. 右上角齿轮 ⚙ → 勾选「启用开发者模式」\n"
            "  3. 界面会多出「保存(API 格式)」按钮\n"
            "  4. 点它导出一份新的 json,用这个文件!\n\n"
            "📖 详细图文步骤点本工具底部「❓ 如何导出 API JSON」按钮"
        )

    # API 格式校验:至少有一个 value 含 class_type
    sample_ok = False
    for k, v in data.items():
        if isinstance(v, dict) and "class_type" in v:
            sample_ok = True
            break
    if not sample_ok:
        raise WorkflowFormatError(
            "这份 JSON 不是标准的 ComfyUI API 格式(找不到 class_type 字段)。\n"
            "请用 ComfyUI 的「Save (API Format)」重新导出。"
        )

    return data


def scan_workflow(wf):
    """自动扫描工作流,找出 LoadImage / 文本节点"""
    load_imgs = []
    text_nodes = []
    for nid, node in wf.items():
        # 防御性判断:跳过非字典节点
        if not isinstance(node, dict):
            continue
        ctype = node.get("class_type", "")
        inputs = node.get("inputs", {})
        if not isinstance(inputs, dict):
            inputs = {}
        if ctype == "LoadImage":
            load_imgs.append(nid)
        # 提示词节点候选
        if ctype in ("CLIPTextEncode", "Text", "ShowText", "String",
                     "WanVideoTextEncode", "WanTextEncode"):
            text_nodes.append(nid)
        elif "text" in inputs or "prompt" in inputs or "positive" in inputs:
            # 排除 link(list 类型)仅看字符串字段
            for k in ("text", "prompt", "positive"):
                v = inputs.get(k)
                if isinstance(v, str):
                    text_nodes.append(nid)
                    break
    # 按节点 ID 数字排序(通常较小的在前)
    try:
        load_imgs.sort(key=lambda x: int(x))
        text_nodes.sort(key=lambda x: int(x))
    except ValueError:
        pass
    return load_imgs, text_nodes


def find_prompt_field(wf, node_id):
    """返回节点中字符串类型的 prompt 字段名"""
    inputs = wf[node_id].get("inputs", {})
    for k in ("text", "prompt", "positive", "input_text"):
        if k in inputs and isinstance(inputs[k], str):
            return k
    # 找第一个字符串输入
    for k, v in inputs.items():
        if isinstance(v, str):
            return k
    return None


def scan_workflow_resolution(wf):
    """
    从 workflow 中扫描出第一个设置了 width/height/length 的节点
    (比如 WanFirstLastFrameToVideo、EmptyLatentVideo 等),
    返回 (width, height, length) 或 None。
    """
    if not wf:
        return None
    for nid, node in wf.items():
        inputs = node.get("inputs", {})
        if ("width" in inputs and "height" in inputs
                and isinstance(inputs.get("width"), int)
                and isinstance(inputs.get("height"), int)):
            w = inputs["width"]
            h = inputs["height"]
            l = inputs.get("length") if isinstance(inputs.get("length"), int) else None
            return (w, h, l)
    return None


def patch_workflow(wf_template, start_node, end_node, prompt_node, prompt_field,
                   start_img_name, end_img_name, prompt_text,
                   width=None, height=None, length=None):
    wf = json.loads(json.dumps(wf_template))
    if start_node not in wf:
        raise RuntimeError(f"首帧节点 {start_node} 不存在")
    if end_node not in wf:
        raise RuntimeError(f"尾帧节点 {end_node} 不存在")
    if prompt_node not in wf:
        raise RuntimeError(f"提示词节点 {prompt_node} 不存在")
    wf[start_node]["inputs"]["image"] = start_img_name
    wf[end_node]["inputs"]["image"] = end_img_name
    if prompt_field not in wf[prompt_node].get("inputs", {}):
        raise RuntimeError(f"提示词节点 {prompt_node} 无字段 {prompt_field}")
    wf[prompt_node]["inputs"][prompt_field] = prompt_text
    # 同步所有带 width/height 的节点(WanFirstLastFrameToVideo/EmptyLatentVideo 等)
    if width is not None or height is not None or length is not None:
        for nid, node in wf.items():
            inputs = node.get("inputs", {})
            if "width" in inputs and "height" in inputs:
                if width is not None:
                    inputs["width"] = int(width)
                if height is not None:
                    inputs["height"] = int(height)
                if length is not None and "length" in inputs:
                    inputs["length"] = int(length)
    return wf


# ============== OpenAI 兼容 API 客户端 ==============
def openai_chat(api_key, base_url, model, messages, temperature=0.7, timeout=180):
    """
    调用 OpenAI 兼容 API(openai/azure/deepseek/moonshot/one-api 等)。
    返回 assistant 回复的 content 字符串。
    """
    base_url = (base_url or DEFAULT_OPENAI_BASE).rstrip("/")
    url = f"{base_url}/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


# ============== 小说改编分镜 Prompt 模板 ==============
NOVEL_SYSTEM_PROMPT = """你是一位专业的漫画分镜师与 AI 视频导演,擅长将小说章节改编成适合 AI 视频生成(Wan 2.2)的「首尾帧动态漫画」分镜脚本。

【重要规则】
1. 你必须输出严格合法的 JSON 数组,不要有任何多余文字、前后说明、markdown 代码块围栏
2. 数组每一项是一个分镜,格式为:
   {"name":"场景名","prompt":"动作指令","color":"色板ID"}
3. 场景名简短(6-12字),例如"雨夜巷尾"、"倒下瞬间"
4. 动作指令必须遵循 Wan 2.2 规范:
   - 动词优先:推近/旋转/上升/飘落/握紧
   - 控制在 20 字以内
   - 镜头 + 主体动作 + 环境 三要素
   - 避免抽象词(不要写"情绪变化""氛围浓郁")
   - 用逗号或空格分隔元素
5. 避免过于血腥暴力场景,遇到可弱化或用过渡镜头替代
6. 分镜要连贯,有起承转合

【色板 ID(color 字段必须从下列中选一个)】
- rainy_night   : 雨夜巷道/夜景冷色,深蓝紫+粉紫/青霓虹
- transition    : 夜→晨过渡,色温从深蓝向金色流转
- dawn          : 清晨,5000K 暖色,米白+原木,窗光斜射
- daylight      : 白天室内/室外,中性色温 6500K,明亮通透
- sunset        : 黄昏,橙金+紫红,长影子
- night_indoor  : 夜晚室内,暖灯 3200K,局部光源为主

【色板分配原则】
- 同一物理场景 / 同一时间段 的连续分镜,必须用同一个 color(保证视觉连贯)
- 换场景或时段切换时才换 color
- 如果不确定,优先 daylight

【好的动作指令示例】
- 镜头缓慢推近 雨丝斜飘 角色抬头
- 瞳孔骤缩瞬间翻滚 武士刀钉入墙面颤动
- 夜空转为晨光 云层流动 雨丝渐停

【输出示例】
[
  {"name":"雨夜巷尾","prompt":"镜头缓慢推近 雨丝斜飘 角色轮廓渐清晰","color":"rainy_night"},
  {"name":"伤势特写","prompt":"角色低头抚伤 缓慢抬头 眼神由疲惫转锐利","color":"rainy_night"},
  {"name":"夜转晨","prompt":"夜空转为晨光 云层流动 雨丝渐停","color":"transition"},
  {"name":"出租屋醒来","prompt":"男生猛然睁眼 晨光斜射脸上 手按胸口","color":"dawn"}
]
"""

PROMPT_SYSTEM_PROMPT = """你是 Wan 2.2 动作指令生成专家。用户给你一个场景的描述或名字,你返回一条符合以下规范的指令:
- 动词优先:推近/旋转/上升/飘落/握紧
- 控制在 20 字以内
- 镜头 + 主体动作 + 环境 三要素
- 避免抽象词

只返回一条指令,不要任何其它文字、引号、解释。
"""


def extract_json_array(text):
    """从 LLM 输出中抽出 JSON 数组,容错处理 markdown 围栏、首尾空文字"""
    text = text.strip()
    # 去掉 ```json ``` 围栏
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if m:
        text = m.group(1).strip()
    # 找第一个 [ 到最后一个 ]
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start:end + 1])
    return json.loads(text)


# ============== 素材库管理器 ==============
class AssetLibrary:
    """
    素材库:目录里每张图的文件名(不含扩展名)就是匹配关键字。
    比如:
      素材库目录/
        ├─ 林默.png          ← 关键字: "林默"
        ├─ 苏郁.jpg          ← 关键字: "苏郁"
        ├─ 蔷薇宫.png        ← 关键字: "蔷薇宫"
        ├─ 雨夜巷子.png      ← 关键字: "雨夜巷子"
        └─ aliases.json     ← 可选,别名映射

    aliases.json 格式:
      {
        "林默": ["林渊", "主角", "渊哥"],
        "苏郁": ["苏女神", "老板"]
      }
    """

    EXT_IMG = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")

    def __init__(self, root_dir=None, log_cb=None):
        self.root_dir = Path(root_dir) if root_dir else None
        self.log = log_cb or (lambda s: None)
        self._index = {}     # {"关键字": "绝对路径"}
        self._aliases = {}   # {"别名": "正式名"}

    def set_root(self, root_dir):
        self.root_dir = Path(root_dir) if root_dir else None
        self.rescan()

    def rescan(self):
        """扫描目录(含子目录),重建索引"""
        self._index.clear()
        self._aliases.clear()
        if not self.root_dir or not self.root_dir.exists():
            return 0
        # 读别名(根目录和子目录都扫)
        for alias_file in self.root_dir.rglob("aliases.json"):
            try:
                with open(alias_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for main, alist in data.items():
                    for a in (alist if isinstance(alist, list) else [alist]):
                        self._aliases[a] = main
            except Exception as e:
                self.log(f"⚠️ 读 {alias_file} 失败: {e}")
        # 递归扫图(子文件夹也扫)
        for f in self.root_dir.rglob("*"):
            if f.is_file() and f.suffix.lower() in self.EXT_IMG:
                key = f.stem  # 不含扩展名
                # 如果有同名,优先根目录的
                if key not in self._index:
                    self._index[key] = str(f.resolve())
        return len(self._index)

    def list_all(self):
        """返回 [(关键字, 文件路径)] 列表,按关键字长度降序(便于匹配时优先匹长的)"""
        items = list(self._index.items())
        items.sort(key=lambda x: -len(x[0]))
        return items

    def get(self, name):
        """取某个名字对应的图片路径"""
        if name in self._index:
            return self._index[name]
        # 别名
        if name in self._aliases:
            real = self._aliases[name]
            return self._index.get(real)
        return None

    def match(self, text):
        """
        从任意文本里抽取所有匹配到的素材路径。
        返回按出现顺序的 [(关键字, 文件路径)] 列表,去重。
        匹配策略:按关键字长度降序匹配,避免"苏郁"先被"苏"截胡。
        """
        if not text or not self._index:
            return []
        found = []  # 保持顺序
        seen = set()
        # 组合索引 + 别名
        keys = list(self._index.keys()) + list(self._aliases.keys())
        keys.sort(key=lambda x: -len(x))

        # 贪心扫描:每找到一个就从 text 里挖掉(防重复)
        t = text
        while True:
            best = None
            best_pos = None
            for k in keys:
                pos = t.find(k)
                if pos >= 0 and (best_pos is None or pos < best_pos):
                    best = k
                    best_pos = pos
            if not best:
                break
            # 映射到路径
            real = self._aliases.get(best, best)
            path = self._index.get(real)
            if path and path not in seen:
                found.append((best, path))
                seen.add(path)
            # 用空格替换匹到的片段,防止下次重复
            t = t[:best_pos] + (" " * len(best)) + t[best_pos + len(best):]
        return found



# ============== 色彩锚点管理器 ==============
DEFAULT_COLOR_ANCHORS = {
    "rainy_night": {
        "name": "🌧 雨夜",
        "text": ("【雨夜色板】冷色调 6500K,主色深蓝紫 #2a3352,"
                 "点缀粉紫霓虹 #d946ef + 青色霓虹 #06b6d4,"
                 "湿润地面反光,雨丝斜飞。画面中等亮度,避免纯黑,细节清晰。"),
        "keywords": ["雨夜", "雨中", "巷", "霓虹", "湿漉", "深夜雨", "暴雨"],
    },
    "transition": {
        "name": "🌅 夜→晨过渡",
        "text": ("【过渡色板】时间流转,色温从 #2a3352 深蓝 → #8b7db5 淡紫 "
                 "→ #ffc19b 浅橙 → #ffd89b 金。云层流动,雨丝渐停,"
                 "城市轮廓在晨雾中浮现。柔和光影,8K,电影氛围。"),
        "keywords": ["过渡", "夜转晨", "黎明", "天色渐明", "色温", "流转"],
    },
    "dawn": {
        "name": "☀️ 清晨",
        "text": ("【清晨色板】暖色 5000K,明亮通透。米白墙面 #f5efe0,"
                 "原木色家具,窗光从画面右侧 45 度斜射而入,淡金晨雾,"
                 "柔和温暖,8K,细节清晰。"),
        "keywords": ["清晨", "早晨", "醒来", "起床", "晨光", "朝阳", "天亮"],
    },
    "daylight": {
        "name": "🏙 白天",
        "text": ("【白天色板】中性色温 6500K,天光均匀,明亮通透。"
                 "冷暖平衡,阴影柔和。画面自然真实,8K,细节丰富。"),
        "keywords": ["白天", "日间", "中午", "正午", "下午", "学校", "办公室"],
    },
    "sunset": {
        "name": "🌇 黄昏",
        "text": ("【黄昏色板】暖色 3500K,主色金橙 #ffa552 + 紫红 #9b5fb4,"
                 "天空渐变紫金,长影子斜长。氛围浪漫,逆光剪影,8K。"),
        "keywords": ["黄昏", "傍晚", "日落", "夕阳", "晚霞"],
    },
    "night_indoor": {
        "name": "🕯 夜晚室内",
        "text": ("【室内夜色板】暖灯 3200K,局部光源(台灯/吊灯/屏幕光),"
                 "主色深棕 #2a1f18 + 暖黄 #ffb96b,阴影沉稳。"
                 "画面有对比度,氛围温馨或压抑(视场景),8K。"),
        "keywords": ["晚上", "深夜室内", "台灯", "卧室", "书房", "酒吧", "房间夜"],
    },
}

# 匹配已经存在于 prompt 中的色板前缀,用于去重
_COLOR_ANCHOR_RE = re.compile(r"【[^】]*色板[^】]*】[^\n]*\n?")


class ColorAnchors:
    """
    色彩锚点:给每个分镜贴一个色板标签,生成时自动把色板描述注入到 prompt 前缀。
    这样 AI 画图 / Wan 2.2 生视频时,整组画面色彩不会漂移。

    数据格式(color_anchors.json):
      {
        "rainy_night": {"name": "🌧 雨夜", "text": "【雨夜色板】...", "keywords": [...]},
        ...
      }
    """

    def __init__(self, file_path=None, log_cb=None):
        self.file_path = file_path or str(Path.cwd() / "color_anchors.json")
        self.log = log_cb or (lambda s: None)
        self.anchors = {}  # {id: {name, text, keywords}}
        self.load()

    def load(self):
        """从 JSON 文件加载色板;文件不存在时写入默认 6 个。"""
        p = Path(self.file_path)
        if not p.exists():
            self.anchors = {k: dict(v) for k, v in DEFAULT_COLOR_ANCHORS.items()}
            self.save()
            return
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self.anchors = data
            else:
                self.anchors = {k: dict(v) for k, v in DEFAULT_COLOR_ANCHORS.items()}
        except Exception as e:
            self.log(f"⚠️ 读 color_anchors.json 失败: {e},使用默认色板")
            self.anchors = {k: dict(v) for k, v in DEFAULT_COLOR_ANCHORS.items()}

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.anchors, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"⚠️ 保存 color_anchors.json 失败: {e}")

    def reset_defaults(self):
        self.anchors = {k: dict(v) for k, v in DEFAULT_COLOR_ANCHORS.items()}
        self.save()

    def list_ids(self):
        return list(self.anchors.keys())

    def get(self, anchor_id):
        return self.anchors.get(anchor_id)

    def get_text(self, anchor_id):
        a = self.anchors.get(anchor_id)
        return a["text"] if a else ""

    def get_name(self, anchor_id):
        a = self.anchors.get(anchor_id)
        return a["name"] if a else ""

    def set(self, anchor_id, name, text, keywords=None):
        self.anchors[anchor_id] = {
            "name": name,
            "text": text,
            "keywords": keywords or [],
        }
        self.save()

    def delete(self, anchor_id):
        if anchor_id in self.anchors:
            del self.anchors[anchor_id]
            self.save()
            return True
        return False

    def auto_detect(self, text):
        """根据提示词关键字猜一个色板 id,猜不中返回 'daylight' 作兜底。"""
        if not text:
            return "daylight"
        best_id = None
        best_score = 0
        for aid, a in self.anchors.items():
            kws = a.get("keywords", [])
            score = sum(1 for kw in kws if kw and kw in text)
            if score > best_score:
                best_score = score
                best_id = aid
        return best_id or "daylight"

    def inject(self, prompt, anchor_id):
        """
        在 prompt 前面拼上色板描述。已经带有【xxx色板】前缀的会先去掉,
        防止多次注入后越积越多。
        """
        if not anchor_id:
            return prompt
        a = self.anchors.get(anchor_id)
        if not a:
            return prompt
        # 去掉旧的色板前缀
        clean = _COLOR_ANCHOR_RE.sub("", prompt or "").lstrip()
        return a["text"] + "\n" + clean



class GPTWebController:
    """
    用 selenium 控制一个 Chrome 浏览器,访问 gpt.aimonkey.plus(或其它 GPT 镜像)。
    功能:
      - 打开网页
      - 自动填输入框并发送
      - 读取最新 AI 回复
      - 保存会话 cookies(用户登录一次就够)

    三种启动模式:
      - attach:    连接到用户手动以 --remote-debugging-port 启动的 Chrome(最稳,推荐)
      - standalone: 独立启动一个 Chrome 实例,用 user-data-dir 保存登录
      - temp:      临时 Chrome(每次要重新登录,避免 profile 冲突)
    """
    INPUT_SELECTOR = "#prompt-textarea"
    LAST_REPLY_SELECTOR = 'div[data-message-author-role="assistant"]:last-child .markdown'
    IMG_IN_REPLY = 'div[data-message-author-role="assistant"] img'

    def __init__(self, url=DEFAULT_GPT_WEB_URL, user_data_dir=None, log_cb=None,
                 mode="standalone", debug_port=9222, chrome_path=None):
        if not HAS_SELENIUM:
            raise RuntimeError("未安装 selenium,请先:pip install selenium")
        self.url = url
        self.log = log_cb or (lambda s: None)
        self.driver = None
        self.mode = mode  # 'attach' | 'standalone' | 'temp'
        self.debug_port = debug_port
        self.chrome_path = chrome_path
        self.profile_dir = user_data_dir or str(Path.cwd() / ".gpt_chrome_profile")

    @staticmethod
    def find_chrome_exe():
        """探测 Chrome 可执行文件路径(Windows/macOS/Linux)"""
        candidates = []
        if sys.platform == "win32":
            for pf in (os.environ.get("ProgramFiles", r"C:\Program Files"),
                       os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
                       os.environ.get("LocalAppData", "")):
                if pf:
                    candidates.append(Path(pf) / "Google/Chrome/Application/chrome.exe")
        elif sys.platform == "darwin":
            candidates.append(Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"))
        else:
            for p in ("/usr/bin/google-chrome", "/usr/bin/chromium-browser",
                      "/usr/bin/chromium", "/snap/bin/chromium"):
                candidates.append(Path(p))
        for c in candidates:
            if c.exists():
                return str(c)
        return None

    @classmethod
    def launch_debug_chrome(cls, port=9222, user_data_dir=None, chrome_path=None):
        """
        主动启动一个带远程调试端口的 Chrome。
        这样独立于本程序,用户也能手动操作,selenium 再 attach 上去。
        """
        # —— 预校验阶段:显式报错优于 Chrome 内部闷声死掉 ——
        # 1. 端口占用
        if cls._port_in_use(port):
            raise RuntimeError(
                f"端口 {port} 已被占用 —— 可能之前的调试 Chrome 还开着。\n\n"
                f"✅ 解决:\n"
                f"  • 直接去那个 Chrome 里操作,或\n"
                f"  • 把这里的「端口」改成 9223 / 9224 等别的端口重试,或\n"
                f"  • 在任务管理器里结束所有 chrome.exe 进程"
            )

        # 2. chrome 可执行文件
        if chrome_path:
            if not os.path.isfile(chrome_path):
                raise RuntimeError(
                    f"指定的 Chrome 路径不存在:\n  {chrome_path}\n\n"
                    f"请改成正确路径,例如:\n"
                    f"  C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                )
        else:
            chrome_path = cls.find_chrome_exe()
            if not chrome_path:
                raise RuntimeError(
                    "找不到 Chrome 可执行文件 —— 这些路径都不存在:\n"
                    "  • C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\n"
                    "  • C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe\n\n"
                    "✅ 解决:\n"
                    "  1. 确认已安装 Google Chrome\n"
                    "  2. 在 AI 行填入 Chrome 路径,或在弹出的文件选择框里手动指定"
                )

        # 3. user-data-dir 可写
        user_data_dir = user_data_dir or str(Path.cwd() / ".gpt_chrome_profile")
        try:
            Path(user_data_dir).mkdir(parents=True, exist_ok=True)
            # 写个临时文件测试权限
            test_f = Path(user_data_dir) / ".write_test"
            test_f.write_text("x")
            test_f.unlink()
        except Exception as e:
            raise RuntimeError(
                f"Profile 目录不可写:\n  {user_data_dir}\n\n"
                f"原因:{e}\n\n"
                f"✅ 解决:选一个有权限的目录,避免路径含中文 / 空格"
            )

        # 4. 锁文件检查
        if cls._profile_is_locked(user_data_dir):
            raise RuntimeError(
                f"Profile 已被另一个 Chrome 占用:\n  {user_data_dir}\n\n"
                f"✅ 解决:\n"
                f"  • 关闭所有使用该 profile 的 Chrome\n"
                f"  • 或手动删除目录里的 SingletonLock / SingletonSocket / SingletonCookie"
            )

        # —— 真正启动 ——
        cmd = [
            chrome_path,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
        ]
        kwargs = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = 0x00000008  # DETACHED_PROCESS
        subprocess.Popen(cmd, **kwargs)

        # —— 启动后验证端口在 5s 内起来,起不来就判断为失败 ——
        for _ in range(10):
            time.sleep(0.5)
            if cls._port_in_use(port):
                break
        else:
            raise RuntimeError(
                f"Chrome 已启动但端口 {port} 5 秒内未监听 ——\n"
                f"可能是 Chrome 崩了,或者 --remote-debugging-port 参数被忽略。\n\n"
                f"手动试试运行:\n  {' '.join(cmd)}"
            )
        return cmd

    @staticmethod
    def _profile_is_locked(profile_dir):
        """检测 user-data-dir 是否正被另一个 Chrome 占用"""
        p = Path(profile_dir)
        if not p.exists():
            return False
        # Chrome 的锁文件
        for lock in ("SingletonLock", "SingletonSocket", "SingletonCookie"):
            f = p / lock
            if f.exists() or f.is_symlink():
                return True
        return False

    @staticmethod
    def _port_in_use(port):
        """检测本地端口是否已被占用(比如调试 Chrome 在跑)"""
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        try:
            result = s.connect_ex(("127.0.0.1", int(port)))
            return result == 0
        finally:
            s.close()

    def _preflight_check(self):
        """启动前的预检:显式校验配置,给出可执行建议,而不是让 selenium 丢模糊错"""
        # 1. Chrome 可执行文件(如果用户指定了)
        if self.chrome_path:
            if not os.path.isfile(self.chrome_path):
                raise RuntimeError(
                    f"配置的 Chrome 路径不存在:\n  {self.chrome_path}\n\n"
                    f"请在顶部 AI 行点「❓ Chrome 启动失败怎么办」查看排查方法,\n"
                    f"或把路径改成例如:\n"
                    f"  C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                )
            self.log(f"  ✓ Chrome binary: {self.chrome_path}")

        # 2. 按模式做针对性检查
        if self.mode == "attach":
            if not self._port_in_use(self.debug_port):
                raise RuntimeError(
                    f"端口 {self.debug_port} 上没有 Chrome 在监听 ——\n"
                    f"attach 模式需要先启动一个带调试端口的 Chrome。\n\n"
                    f"✅ 解决:点 AI 行的「🚀 启动调试 Chrome」按钮先开一个,\n"
                    f"   然后在弹出的 Chrome 里登录 GPT,再回来点「🌐 打开 GPT」。"
                )
            self.log(f"  ✓ 检测到端口 {self.debug_port} 有 Chrome 监听")

        elif self.mode == "standalone":
            if self._profile_is_locked(self.profile_dir):
                raise RuntimeError(
                    f"Profile 目录被锁定,无法启动第二个 Chrome:\n"
                    f"  {self.profile_dir}\n\n"
                    f"原因:目录里有 SingletonLock 等锁文件,说明有 Chrome 正在用这个 profile。\n\n"
                    f"✅ 三种解决办法:\n"
                    f"  1. 关掉所有使用该 profile 的 Chrome 窗口,再试\n"
                    f"  2. 改用「attach」模式(推荐)\n"
                    f"  3. 改用「temp」模式(临时实例,每次重登)\n"
                    f"  4. 手动删除 {self.profile_dir} 里的 Singleton* 文件(慎用)"
                )
            Path(self.profile_dir).mkdir(parents=True, exist_ok=True)
            self.log(f"  ✓ Profile 目录可用: {self.profile_dir}")

        # 3. selenium 版本提醒
        try:
            import selenium as _se
            ver = _se.__version__
            major = int(ver.split(".")[0])
            if major < 4:
                self.log(f"  ⚠️ selenium 版本 {ver} 过老,建议 pip install -U selenium")
            else:
                self.log(f"  ✓ selenium 版本: {ver}")
        except Exception:
            pass

    def start(self):
        if self.driver:
            return
        self.log(f"🌐 启动 Chrome (mode={self.mode}) ...")
        self._preflight_check()

        opts = ChromeOptions()

        # 显式应用 chrome_path(用户指定时优先用这个)
        if self.chrome_path and os.path.isfile(self.chrome_path):
            opts.binary_location = self.chrome_path

        if self.mode == "attach":
            # 连接到已经开的 Chrome(需要用户已运行 --remote-debugging-port)
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")
            self.log(f"  → 连接 127.0.0.1:{self.debug_port}")
        elif self.mode == "temp":
            # 临时实例:不用 user-data-dir,避免冲突
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_experimental_option("excludeSwitches", ["enable-automation"])
            opts.add_experimental_option("useAutomationExtension", False)
            self.log("  → 临时实例模式(每次需重新登录)")
        else:  # standalone
            opts.add_argument(f"--user-data-dir={self.profile_dir}")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_experimental_option("excludeSwitches", ["enable-automation"])
            opts.add_experimental_option("useAutomationExtension", False)
            self.log(f"  → 独立模式 profile={self.profile_dir}")

        try:
            self.driver = webdriver.Chrome(options=opts)
        except Exception as e:
            msg = str(e)
            hint = self._diagnose_error(msg)
            raise RuntimeError(f"{msg}\n\n{hint}")

        try:
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
            })
        except Exception:
            pass

        # attach 模式下不要强制跳转,保留用户已有的标签
        if self.mode != "attach":
            self.driver.get(self.url)
        else:
            # 检查当前 URL 是否已经在目标站,否则打开新标签到 self.url
            try:
                cur = self.driver.current_url or ""
                if self.url and ("gpt" not in cur and "openai" not in cur and "aimonkey" not in cur):
                    self.driver.execute_script(f"window.open('{self.url}', '_blank');")
                    # 切到新标签
                    handles = self.driver.window_handles
                    self.driver.switch_to.window(handles[-1])
            except Exception:
                pass
        self.log(f"✅ 浏览器已就绪")

    @staticmethod
    def _diagnose_error(msg):
        """根据错误信息给出诊断建议"""
        m = msg.lower()
        if "session not created" in m and "chrome instance exited" in m:
            return ("【诊断】Chrome 启动后立刻退出,通常原因:\n"
                    "  1. 【最常见】Chrome 正在使用同一个 user-data-dir\n"
                    "     → 关掉所有 Chrome 窗口重试\n"
                    "     → 或在 AI 设置里改「模式」为「attach(连接已运行 Chrome)」\n"
                    "  2. Chrome 版本与 ChromeDriver 不匹配\n"
                    "     → 升级 selenium:pip install -U selenium\n"
                    "  3. user-data-dir 路径被锁(有 SingletonLock 文件)\n"
                    "     → 删除 .gpt_chrome_profile 文件夹后重试\n\n"
                    "✅ 推荐方案:点工具里的「🚀 启动调试 Chrome」按钮,\n"
                    "   然后把模式改成「attach」,再点「🌐 打开 GPT」")
        if "chrome not reachable" in m:
            return "【诊断】无法连接 Chrome,端口不对或 Chrome 已关闭"
        if "chromedriver" in m and ("version" in m or "mismatch" in m):
            return ("【诊断】ChromeDriver 版本不匹配。\n"
                    "  执行:pip install -U selenium\n"
                    "  selenium 4.6+ 会自动下载匹配版本")
        if "no such file" in m or "not found" in m:
            return "【诊断】找不到 Chrome 浏览器。请确认已安装 Google Chrome。"
        return "【诊断】未知错误。建议尝试:\n  1. 关闭所有 Chrome 窗口\n  2. 改用 attach 模式"

    def stop(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def is_alive(self):
        if not self.driver:
            return False
        try:
            _ = self.driver.current_url
            return True
        except Exception:
            return False

    def new_chat(self, wait_ready=True, timeout=10):
        """v0.11:点 GPT 网页左上角「新聊天」按钮,开一个干净的新对话。
        
        用于批量生图时每个场景之间隔离上下文,避免上下文污染导致画风漂移。
        
        - wait_ready:点完是否等输入框出现(确认新对话已就绪)
        - timeout:等输入框的最长秒数
        
        返回 True 成功 / False 失败(失败已打日志,调用者决定是否继续)
        """
        if not self.is_alive():
            return False
        d = self.driver
        
        # 多重选择器 — GPT 网页版本可能变,尽量兜底
        # 1. aria-label 常见值:"新聊天" / "New chat" / "开启新聊天"
        # 2. data-testid:"create-new-chat-button"(老版本)
        # 3. 图标按钮:href="/" 的 a 标签
        js = """
        function findNewChatBtn() {
            // 方案 1:aria-label 匹配
            const labels = ['新聊天', 'New chat', '新建聊天', '开启新聊天', '새 채팅'];
            for (const lab of labels) {
                const el = document.querySelector(`[aria-label="${lab}" i]`);
                if (el) return el;
            }
            // 方案 2:data-testid
            const ids = ['create-new-chat-button', 'new-chat-button'];
            for (const id of ids) {
                const el = document.querySelector(`[data-testid="${id}"]`);
                if (el) return el;
            }
            // 方案 3:侧边栏 href="/" 的链接(ChatGPT 本站 / 镜像站都适用)
            const links = document.querySelectorAll('nav a[href="/"], aside a[href="/"]');
            if (links.length > 0) return links[0];
            // 方案 4:遍历按钮找带 plus 图标 + 文字包含"新"/"new"
            const btns = document.querySelectorAll('button, a');
            for (const b of btns) {
                const txt = (b.textContent || '').trim().toLowerCase();
                if (txt === '新聊天' || txt === 'new chat' || txt === '新建聊天') return b;
            }
            return null;
        }
        const btn = findNewChatBtn();
        if (!btn) return 'NOT_FOUND';
        btn.click();
        return 'OK';
        """
        try:
            r = d.execute_script(js)
            if r != "OK":
                self.log(f"   ⚠️ 新聊天按钮未找到(结果:{r}),跳过新开对话")
                return False
            self.log("   🔄 已点击新聊天按钮")
        except Exception as e:
            self.log(f"   ⚠️ 点击新聊天失败:{e}")
            return False
        
        if wait_ready:
            # 等输入框出现,确认页面已切到新对话
            import time as _t
            deadline = _t.time() + timeout
            while _t.time() < deadline:
                try:
                    ready = d.execute_script(
                        f"return !!document.querySelector('{self.INPUT_SELECTOR}');")
                    if ready:
                        self.log("   ✅ 新对话已就绪")
                        _t.sleep(0.5)  # 让 DOM 完全稳定
                        return True
                except Exception:
                    pass
                _t.sleep(0.3)
            self.log("   ⚠️ 等待新对话输入框超时(但可能已切换,继续)")
            return True  # 宽容:按钮点到了就算成功
        return True

    def send(self, text, wait_reply=True, timeout=180):
        """填入输入框,点发送,可选等回复完成"""
        if not self.is_alive():
            self.start()
        d = self.driver
        # 记录发送前的最后一条 assistant 消息 id,用于判断新回复
        prev_id = self._last_reply_id()

        # 用 JS 直接塞文本到 ProseMirror 再触发 input 事件,比 send_keys 稳
        escaped = json.dumps(text)
        js = f"""
        const box = document.querySelector('{self.INPUT_SELECTOR}');
        if (!box) return 'NO_BOX';
        box.focus();
        // ProseMirror 清空再插入
        box.innerHTML = '';
        const p = document.createElement('p');
        p.textContent = {escaped};
        box.appendChild(p);
        box.dispatchEvent(new InputEvent('input', {{bubbles:true}}));
        return 'OK';
        """
        r = d.execute_script(js)
        if r != "OK":
            raise RuntimeError(f"找不到输入框(结果: {r})")
        time.sleep(0.3)
        # 发送:先尝试找 data-testid='send-button',否则回车
        sent = d.execute_script("""
            const btn = document.querySelector('[data-testid="send-button"]')
                      || document.querySelector('button[aria-label*="发送" i]')
                      || document.querySelector('button[aria-label*="Send" i]');
            if (btn && !btn.disabled) { btn.click(); return true; }
            return false;
        """)
        if not sent:
            # 回车兜底
            box = d.find_element(By.CSS_SELECTOR, self.INPUT_SELECTOR)
            box.send_keys(Keys.ENTER)
        self.log(f"📤 已发送:{text[:40]}...")

        if not wait_reply:
            return None
        return self.wait_reply(prev_id=prev_id, timeout=timeout)

    def _last_reply_id(self):
        try:
            return self.driver.execute_script("""
                const nodes = document.querySelectorAll('div[data-message-author-role="assistant"]');
                if (!nodes.length) return null;
                return nodes[nodes.length-1].getAttribute('data-message-id');
            """)
        except Exception:
            return None

    def wait_reply(self, prev_id=None, timeout=180, stable_secs=3):
        """
        等待新 assistant 消息出现并稳定(文本连续 stable_secs 秒不变就认为写完)
        返回回复文本。
        """
        start = time.time()
        last_text = ""
        stable_start = None
        while time.time() - start < timeout:
            try:
                cur_id = self._last_reply_id()
                if cur_id and cur_id != prev_id:
                    txt = self.driver.execute_script(f"""
                        const el = document.querySelector(
                            'div[data-message-id="{cur_id}"] .markdown');
                        return el ? el.innerText : '';
                    """) or ""
                    if txt and txt == last_text:
                        if stable_start is None:
                            stable_start = time.time()
                        elif time.time() - stable_start >= stable_secs:
                            return txt
                    else:
                        stable_start = None
                        last_text = txt
            except Exception:
                pass
            time.sleep(1)
        return last_text or "(等待超时,未获得完整回复)"

    def get_last_reply(self):
        """只读最新 assistant 消息,不发送"""
        if not self.is_alive():
            return ""
        try:
            return self.driver.execute_script("""
                const nodes = document.querySelectorAll(
                    'div[data-message-author-role="assistant"] .markdown');
                return nodes.length ? nodes[nodes.length-1].innerText : '';
            """) or ""
        except Exception as e:
            self.log(f"❌ 读取失败: {e}")
            return ""

    def get_last_images(self):
        """
        返回对话区所有"GPT 生成图片"的 URL 列表(按 DOM 顺序,末尾 = 最新)。

        用多策略定位,适配标准 ChatGPT + 各种镜像站(aimonkey/geek/openai-hk 等):
          1. 优先找标准 data-message-author-role="assistant" 容器
          2. 镜像站:找 alt 含 "已生成图片/Generated image/图片已生成" 的 <img>
          3. 兜底:main/article 区域里 src 含 estuary/files/oaiusercontent/blob 的图
        """
        if not self.is_alive():
            return []
        try:
            urls = self.driver.execute_script(r"""
                // ===== 策略 1: 标准 ChatGPT 容器 =====
                let imgs = [];
                const std = document.querySelectorAll(
                    'div[data-message-author-role="assistant"]');
                if (std.length) {
                    for (const node of std) {
                        imgs.push(...node.querySelectorAll('img'));
                    }
                }

                // ===== 策略 2: 镜像站 - alt 文本匹配 =====
                if (!imgs.length) {
                    const alts = document.querySelectorAll(
                        'main img[alt*="已生成图片"], main img[alt*="图片已生成"], ' +
                        'main img[alt*="Generated image"], main img[alt*="已创建图像"], ' +
                        'article img[alt*="已生成图片"], article img[alt*="Generated image"]'
                    );
                    imgs = Array.from(alts);
                }

                // ===== 策略 3: 兜底 - URL 特征匹配 =====
                if (!imgs.length) {
                    const root = document.querySelector('main') || document.body;
                    const all = root.querySelectorAll('img');
                    imgs = Array.from(all).filter(i => {
                        const s = i.src || '';
                        return s.includes('estuary/content')
                            || s.includes('/backend-api/files')
                            || s.includes('/backend-api/conversation')
                            || s.includes('oaiusercontent')
                            || s.includes('cdn.openai.com')
                            || (s.startsWith('blob:') && i.naturalWidth > 200);
                    });
                }

                // 去重 + 过滤无效 src + 过滤头像/logo(尺寸 < 100 通常是装饰)
                const seen = new Set();
                const out = [];
                for (const i of imgs) {
                    const s = i.src;
                    if (!s || seen.has(s)) continue;
                    // 过滤 SVG 数据 URL 和太小的装饰图
                    if (s.startsWith('data:image/svg')) continue;
                    if (i.naturalWidth && i.naturalWidth < 100
                        && !s.startsWith('data:')) continue;
                    seen.add(s);
                    out.push(s);
                }
                return out;
            """) or []
            return [u for u in urls if u and u.startswith(("http://", "https://", "data:"))]
        except Exception as e:
            try:
                self.log(f"❌ get_last_images 失败: {e}")
            except Exception:
                pass
            return []

    def get_new_images(self, before_urls):
        """
        对比基线,返回发送之后【新增】的图片 URL。
        这是批量 GPT 生图下载的关键 —— 每轮只拿本轮新生成的。
        """
        before_set = set(before_urls or [])
        cur = self.get_last_images()
        new_ones = [u for u in cur if u not in before_set]
        return new_ones

    def wait_for_images(self, min_count=1, timeout=300, stable_seconds=3,
                        before_urls=None):
        """
        轮询等待新图片出现并稳定。
        - 如果给了 before_urls:等【新增】图片数量 >= min_count,稳定后返回新增的
        - 没给:回退到老逻辑,等总数 >= min_count
        超时则返回当下能拿到的(可能为空)。
        """
        start = time.time()
        before_set = set(before_urls) if before_urls else None
        last_count = -1
        stable_since = None
        while time.time() - start < timeout:
            try:
                all_urls = self.get_last_images()
            except Exception:
                all_urls = []
            if before_set is not None:
                urls = [u for u in all_urls if u not in before_set]
            else:
                urls = all_urls
            cnt = len(urls)
            if cnt != last_count:
                last_count = cnt
                stable_since = time.time() if cnt >= min_count else None
            elif stable_since is not None and (time.time() - stable_since) >= stable_seconds:
                return urls
            time.sleep(1)
        # 超时:返回当下能拿到的(用 before 过滤)
        try:
            all_urls = self.get_last_images()
            if before_set is not None:
                return [u for u in all_urls if u not in before_set]
            return all_urls
        except Exception:
            return []

    def _fetch_via_browser(self, url):
        """
        用浏览器 fetch(带登录 cookies)下载资源,返回 (bytes, media_type)。
        对镜像站那种 URL 里带 sig 参数、需要登录 session 的必须走这条路径,
        直接 urllib.request 会 401/403。
        """
        if not self.is_alive():
            return None, None
        script = r"""
        const url = arguments[0];
        const done = arguments[arguments.length - 1];
        fetch(url, { credentials: 'include' }).then(async (resp) => {
            if (!resp.ok) {
                done({ ok: false, status: resp.status });
                return;
            }
            const ct = resp.headers.get('content-type') || '';
            const blob = await resp.blob();
            const reader = new FileReader();
            reader.onload = () => done({ ok: true, data: reader.result, type: ct });
            reader.onerror = () => done({ ok: false, error: 'read_fail' });
            reader.readAsDataURL(blob);
        }).catch(err => done({ ok: false, error: String(err) }));
        """
        try:
            self.driver.set_script_timeout(120)
            r = self.driver.execute_async_script(script, url)
            if not r or not r.get("ok"):
                return None, None
            data_url = r.get("data", "")
            if not data_url.startswith("data:"):
                return None, None
            import base64
            header, b64 = data_url.split(",", 1)
            return base64.b64decode(b64), r.get("type", "image/png")
        except Exception as e:
            try:
                self.log(f"   🔧 浏览器 fetch 失败({url[:60]}...): {e}")
            except Exception:
                pass
            return None, None

    def download_last_images(self, save_dir, urls=None):
        """下载图片到本地。如果传入 urls 用这个列表,否则自动拿最新的全部。

        优先用浏览器 fetch(带 cookies),失败再退到 urllib + UA 伪装。
        """
        if urls is None:
            urls = self.get_last_images()
        if not urls:
            return []
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        saved = []
        for i, u in enumerate(urls):
            try:
                target = None
                data = None
                media_type = None

                if u.startswith("data:"):
                    # data:image/png;base64,xxx
                    import base64
                    header, b64 = u.split(",", 1)
                    media_type = header.split(":", 1)[-1].split(";", 1)[0]
                    data = base64.b64decode(b64)
                else:
                    # 优先用浏览器 fetch(带 cookies)
                    data, media_type = self._fetch_via_browser(u)
                    if data is None:
                        # 兜底:urllib + UA 伪装(对公开 URL 有效,需 cookies 的会失败)
                        try:
                            req = urllib.request.Request(
                                u, headers={"User-Agent": "Mozilla/5.0",
                                            "Referer": self.driver.current_url if self.is_alive() else ""})
                            with urllib.request.urlopen(req, timeout=60) as r:
                                data = r.read()
                                media_type = r.headers.get("Content-Type", "image/png")
                        except Exception as e2:
                            self.log(f"   ❌ 图 {i+1} urllib 也失败: {e2}")
                            continue

                # 选扩展名
                ext = "png"
                if media_type:
                    if "jpeg" in media_type or "jpg" in media_type:
                        ext = "jpg"
                    elif "webp" in media_type:
                        ext = "webp"
                    elif "gif" in media_type:
                        ext = "gif"
                target = Path(save_dir) / f"gpt_img_{int(time.time())}_{i}.{ext}"
                with open(target, "wb") as f:
                    f.write(data)
                saved.append(str(target))
                self.log(f"   💾 图 {i+1} 已保存: {target.name} ({len(data)//1024} KB)")
            except Exception as e:
                self.log(f"   ❌ 图 {i+1} 下载失败: {e}")
        return saved

    # ============== 文件上传 ==============
    def upload_files(self, file_paths, wait_timeout=30):
        """
        给 ChatGPT / 镜像站上传图片。
        原理:找到页面里的 <input type="file">,直接 send_keys(路径),
        这会绕过系统文件对话框,selenium 推荐的标准做法。

        如果页面没有现成的 input[type=file](需要点 + 号才出现),
        会先 JS 创建一个绑定到真正上传端点的 input 再塞文件。

        参数 file_paths 是本地绝对路径列表。
        """
        if not self.is_alive():
            raise RuntimeError("浏览器未启动")
        # 验证文件
        valid_paths = []
        for p in file_paths:
            ap = str(Path(p).resolve())
            if not os.path.isfile(ap):
                self.log(f"⚠️ 跳过不存在的文件: {p}")
                continue
            valid_paths.append(ap)
        if not valid_paths:
            raise RuntimeError("没有有效的图片路径")

        d = self.driver
        self.log(f"📎 准备上传 {len(valid_paths)} 张图片...")

        # 方案 A:找现成的 input[type=file]
        # 优先级:#upload-files (aimonkey 等镜像) > 通用 input[type=file]
        inputs = d.find_elements(By.CSS_SELECTOR, "#upload-files")
        if not inputs:
            inputs = d.find_elements(By.CSS_SELECTOR, "input[type='file'][multiple]")
        if not inputs:
            inputs = d.find_elements(By.CSS_SELECTOR, "input[type='file']")
        if inputs:
            self.log(f"   找到 {len(inputs)} 个文件 input")

        # 方案 B:如果没有,先点 + 按钮让它出来(或主动触发)
        if not inputs:
            self.log("   未发现 input,尝试点击 + 按钮触发...")
            clicked = d.execute_script("""
                // ChatGPT / aimonkey / 大部分镜像站
                const selectors = [
                    '[data-testid="composer-plus-btn"]',
                    '#composer-plus-btn',
                    'button[aria-label*="添加" i]',
                    'button[aria-label*="attach" i]',
                    'button[aria-label*="upload" i]',
                ];
                for (const s of selectors) {
                    const b = document.querySelector(s);
                    if (b) { b.click(); return s; }
                }
                return null;
            """)
            if clicked:
                self.log(f"   已点击按钮: {clicked}")
                time.sleep(0.5)

            # 再次找 input
            inputs = d.find_elements(By.CSS_SELECTOR, "input[type='file']")

        # 方案 C:还是没有的话,创建一个假 input 挂到 body 上
        if not inputs:
            self.log("   未找到文件 input,创建一个临时 input...")
            d.execute_script("""
                const existing = document.getElementById('__tk_upload_input');
                if (existing) existing.remove();
                const i = document.createElement('input');
                i.type = 'file';
                i.id = '__tk_upload_input';
                i.multiple = true;
                i.accept = 'image/*';
                i.style.position = 'fixed';
                i.style.left = '-9999px';
                document.body.appendChild(i);
            """)
            inputs = d.find_elements(By.CSS_SELECTOR, "#__tk_upload_input")

        if not inputs:
            raise RuntimeError(
                "找不到可用的文件 input 元素。\n"
                "可能的原因:\n"
                "  1. 网页没有上传功能\n"
                "  2. 需要手动点一下 + 按钮\n"
                "  3. 镜像站的 DOM 结构与主流 ChatGPT 不同"
            )

        file_input = inputs[-1]  # 用最后一个(通常是刚新建的)
        # 让它可见,否则 send_keys 可能失败
        try:
            d.execute_script("""
                arguments[0].style.display='block';
                arguments[0].style.visibility='visible';
                arguments[0].style.opacity='1';
                arguments[0].removeAttribute('hidden');
            """, file_input)
        except Exception:
            pass

        # 多文件:send_keys 用 \n 分隔
        try:
            file_input.send_keys("\n".join(valid_paths))
        except Exception as e:
            raise RuntimeError(f"send_keys 失败: {e}\n\n多半是 input 元素不可交互,请手动点 + 按钮后重试")

        self.log(f"✅ 已将 {len(valid_paths)} 张图塞给 input,等待网页处理...")

        # 等待上传缩略图出现(可选,不同站点结构不同,不强求)
        try:
            WebDriverWait(d, wait_timeout).until(
                lambda driver: driver.execute_script("""
                    // 页面上出现带 img 的 attachment / file preview
                    return document.querySelectorAll(
                        'div[class*="attachment" i] img, div[class*="file-preview" i] img, img[alt*="附件" i]'
                    ).length > 0
                    || document.querySelectorAll('div[role="presentation"] img').length > 0;
                """)
            )
            self.log("   ✅ 检测到缩略图已生成")
        except Exception:
            self.log("   ⚠️ 未检测到缩略图(不一定是失败,有些站点没有这个元素)")

        return valid_paths


# ============== GUI ==============
class ComfyBatchGUI:
    def __init__(self, root):
        self.root = root
        dnd_suffix = "" if HAS_DND else "  (装 tkinterdnd2 可开启系统级拖拽)"
        self.root.title(f"ComfyUI Wan 2.2 首尾帧批量生成工具  v{__version__}{dnd_suffix}")
        self.root.geometry("1320x880")

        # 状态
        self.scenes = []  # list of dict {name, start, end, prompt, status, video_path}
        self.workflow = None
        self.workflow_path = tk.StringVar()
        self.host_var = tk.StringVar(value=DEFAULT_HOST)
        self.output_var = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
        self.start_node_var = tk.StringVar()
        self.end_node_var = tk.StringVar()
        self.prompt_node_var = tk.StringVar()
        self.prompt_field_var = tk.StringVar(value="text")
        # 分辨率(v0.8 默认改成横屏,配合拆分成两次 GPT 调用的新流程)
        self.orient_var = tk.StringVar(value="横屏 16:9")
        self.width_var = tk.IntVar(value=960)
        self.height_var = tk.IntVar(value=544)
        self.length_var = tk.IntVar(value=81)
        self.log_q = queue.Queue()
        self.worker = None
        self.stop_flag = threading.Event()

        # AI 配置
        self.ai_key_var = tk.StringVar()
        self.ai_base_var = tk.StringVar(value=DEFAULT_OPENAI_BASE)
        self.ai_model_var = tk.StringVar(value=DEFAULT_OPENAI_MODEL)
        self.gpt_url_var = tk.StringVar(value=DEFAULT_GPT_WEB_URL)
        self.gpt_mode_var = tk.StringVar(value="attach")  # attach / standalone / temp
        self.gpt_port_var = tk.IntVar(value=9222)
        self.gpt_chrome_path_var = tk.StringVar()  # 空则自动探测

        # 素材库
        self.asset_dir_var = tk.StringVar(value=str(SCRIPT_DIR / "assets_library"))
        self.asset_lib = AssetLibrary(log_cb=self._log)
        self.auto_upload_var = tk.BooleanVar(value=True)  # 发送前自动上传匹配图片

        # 色彩锚点
        self.color_anchors = ColorAnchors(log_cb=self._log)
        self.auto_inject_color_var = tk.BooleanVar(value=True)  # 发送时自动注入色板

        # v0.10:GPT 图保存目录(填了就不弹窗) + 4 个首尾帧模板
        self.gpt_save_dir_var = tk.StringVar(value=str(SCRIPT_DIR / "gpt_images"))
        self._tmpl_start_empty = DEFAULT_START_EMPTY_TMPL
        self._tmpl_start_people = DEFAULT_START_PEOPLE_TMPL
        self._tmpl_end_empty = DEFAULT_END_EMPTY_TMPL
        self._tmpl_end_people = DEFAULT_END_PEOPLE_TMPL

        # v0.11:每场景完成后自动新开 GPT 对话(隔离上下文,避免画风漂移)
        self.auto_new_chat_var = tk.BooleanVar(value=True)

        # 手动提示词库(GPT 和 Wan 2.2 各一份)
        self._prompt_presets = []  # [{"title":"...", "text":"..."}]
        self._wan22_presets = []   # [{"title":"...", "text":"..."}]
        self._prompt_presets_file = str(SCRIPT_DIR / "gpt_prompts.json")
        self._wan22_presets_file = str(SCRIPT_DIR / "wan22_prompts.json")
        self.gpt_ctrl = None  # GPTWebController 实例

        # v0.9: GPT 批量生图暂停/继续
        self.gpt_pause_flag = threading.Event()   # set = 暂停中
        self.gpt_batch_running = False             # 标记 GPT 批量是否在跑

        self._build_ui()
        self._enable_drag_drop()
        self._init_preset_files()
        self._load_last_config()
        self.root.after(100, self._drain_log)

    # ---------- UI 构建 ----------
    def _build_ui(self):
        # 顶部工具栏
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill="x")

        ttk.Label(top, text="ComfyUI 地址:").pack(side="left")
        ttk.Entry(top, textvariable=self.host_var, width=18).pack(side="left", padx=(2, 12))

        ttk.Label(top, text="工作流 API JSON:").pack(side="left")
        ttk.Entry(top, textvariable=self.workflow_path, width=40).pack(side="left", padx=2)
        ttk.Button(top, text="浏览...", command=self._pick_workflow).pack(side="left", padx=2)
        ttk.Button(top, text="扫描节点", command=self._scan_nodes).pack(side="left", padx=2)

        # 节点配置行
        node_row = ttk.LabelFrame(self.root, text="节点配置(加载工作流后点「扫描节点」自动填充)", padding=8)
        node_row.pack(fill="x", padx=8, pady=(0, 4))
        ttk.Label(node_row, text="首帧节点:").grid(row=0, column=0, sticky="w")
        self.start_combo = ttk.Combobox(node_row, textvariable=self.start_node_var, width=8)
        self.start_combo.grid(row=0, column=1, padx=(2, 12))

        ttk.Label(node_row, text="尾帧节点:").grid(row=0, column=2, sticky="w")
        self.end_combo = ttk.Combobox(node_row, textvariable=self.end_node_var, width=8)
        self.end_combo.grid(row=0, column=3, padx=(2, 12))

        ttk.Label(node_row, text="提示词节点:").grid(row=0, column=4, sticky="w")
        self.prompt_combo = ttk.Combobox(node_row, textvariable=self.prompt_node_var, width=8)
        self.prompt_combo.grid(row=0, column=5, padx=(2, 12))
        self.prompt_combo.bind("<<ComboboxSelected>>", self._on_prompt_node_change)

        ttk.Label(node_row, text="字段名:").grid(row=0, column=6, sticky="w")
        ttk.Entry(node_row, textvariable=self.prompt_field_var, width=8).grid(row=0, column=7, padx=2)

        ttk.Label(node_row, text="视频保存目录:").grid(row=0, column=8, sticky="w", padx=(12, 0))
        ttk.Entry(node_row, textvariable=self.output_var, width=28).grid(row=0, column=9, padx=2)
        ttk.Button(node_row, text="选择", command=self._pick_output).grid(row=0, column=10, padx=2)

        # 第 2 行:分辨率 / 方向 / 帧数
        ttk.Label(node_row, text="📐 输出:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        orient_cb = ttk.Combobox(node_row, textvariable=self.orient_var, width=12,
                                 values=["竖屏 9:16", "横屏 16:9", "方图 1:1", "自定义"],
                                 state="readonly")
        orient_cb.grid(row=1, column=1, padx=(2, 12), pady=(6, 0))
        orient_cb.bind("<<ComboboxSelected>>", self._on_orient_change)

        ttk.Label(node_row, text="宽:").grid(row=1, column=2, sticky="e", pady=(6, 0))
        ttk.Spinbox(node_row, textvariable=self.width_var, from_=64, to=2048,
                    increment=16, width=8).grid(row=1, column=3, padx=(2, 8), pady=(6, 0))

        ttk.Label(node_row, text="高:").grid(row=1, column=4, sticky="e", pady=(6, 0))
        ttk.Spinbox(node_row, textvariable=self.height_var, from_=64, to=2048,
                    increment=16, width=8).grid(row=1, column=5, padx=(2, 8), pady=(6, 0))

        ttk.Button(node_row, text="🔄 交换宽高",
                   command=self._swap_wh).grid(row=1, column=6, padx=(0, 12), pady=(6, 0))

        ttk.Label(node_row, text="帧数:").grid(row=1, column=7, sticky="e", pady=(6, 0))
        ttk.Spinbox(node_row, textvariable=self.length_var, from_=17, to=401,
                    increment=16, width=6).grid(row=1, column=8, padx=(2, 4), pady=(6, 0))
        ttk.Label(node_row, text="(17/33/49/65/81/97/... 推荐 81,约 5.1 秒 @ 16fps)",
                  foreground="#888").grid(row=1, column=9, columnspan=2, sticky="w", pady=(6, 0))

        # AI 助手配置行
        ai_row = ttk.LabelFrame(self.root, text="🤖 AI 助手 (OpenAI 兼容 API / 挂载 GPT 网页)", padding=8)
        ai_row.pack(fill="x", padx=8, pady=(0, 4))

        ttk.Label(ai_row, text="API Key:").grid(row=0, column=0, sticky="w")
        key_entry = ttk.Entry(ai_row, textvariable=self.ai_key_var, width=20, show="*")
        key_entry.grid(row=0, column=1, padx=(2, 8))

        ttk.Label(ai_row, text="Base URL:").grid(row=0, column=2, sticky="w")
        ttk.Entry(ai_row, textvariable=self.ai_base_var, width=28).grid(row=0, column=3, padx=(2, 8))

        ttk.Label(ai_row, text="模型:").grid(row=0, column=4, sticky="w")
        model_cb = ttk.Combobox(ai_row, textvariable=self.ai_model_var, width=18,
                                values=["gpt-4o-mini", "gpt-4o", "gpt-4.1",
                                        "gpt-5", "deepseek-chat", "deepseek-reasoner",
                                        "moonshot-v1-8k", "claude-3-5-sonnet"])
        model_cb.grid(row=0, column=5, padx=(2, 12))

        ttk.Button(ai_row, text="📚 小说一键改分镜",
                   command=self._open_novel_dialog).grid(row=0, column=6, padx=2)
        ttk.Button(ai_row, text="✨ 给选中生成提示词",
                   command=self._ai_gen_prompts).grid(row=0, column=7, padx=2)
        ttk.Button(ai_row, text="🎨 色彩锚点",
                   command=self._show_color_anchors_dialog).grid(row=0, column=8, padx=2)
        ttk.Button(ai_row, text="⬜ 空镜模板",
                   command=self._show_frame_tmpl_dialog).grid(row=0, column=9, padx=2)
        ttk.Button(ai_row, text="📝 GPT 提示词库",
                   command=self._show_gpt_preset_dialog).grid(row=0, column=10, padx=2)
        ttk.Button(ai_row, text="🧪 测试 API",
                   command=self._test_ai_api).grid(row=0, column=11, padx=2)

        # GPT 网页控制(放到第 3 行,避免第 1 行挤爆显示不全)
        ttk.Label(ai_row, text="🌐 GPT 网页地址:").grid(row=3, column=0, sticky="w", pady=(4, 0))
        ttk.Entry(ai_row, textvariable=self.gpt_url_var, width=44).grid(
            row=3, column=1, columnspan=4, sticky="we", padx=2, pady=(4, 0))
        ttk.Button(ai_row, text="🌐 打开 / 挂载 GPT",
                   command=self._open_gpt_web).grid(row=3, column=5, columnspan=2,
                                                     sticky="w", padx=4, pady=(4, 0))
        ttk.Label(ai_row, text="← 改完 URL 点此按钮重新挂载浏览器",
                  foreground="#888", font=("Microsoft YaHei", 8)).grid(
            row=3, column=7, columnspan=4, sticky="w", padx=(8, 0), pady=(4, 0))

        # 第二行:GPT 高级配置
        ttk.Label(ai_row, text="模式:").grid(row=1, column=0, sticky="w", pady=(4, 0))
        mode_cb = ttk.Combobox(ai_row, textvariable=self.gpt_mode_var, width=18,
                               values=["attach  (连接已运行 Chrome,最稳)",
                                       "standalone  (独立启动,保持登录)",
                                       "temp  (临时实例,无登录)"],
                               state="readonly")
        mode_cb.grid(row=1, column=1, columnspan=2, sticky="w", pady=(4, 0))
        mode_cb.bind("<<ComboboxSelected>>", self._on_gpt_mode_change)

        ttk.Label(ai_row, text="端口:").grid(row=1, column=3, sticky="w", padx=(8, 0), pady=(4, 0))
        ttk.Entry(ai_row, textvariable=self.gpt_port_var, width=6).grid(
            row=1, column=4, sticky="w", pady=(4, 0))

        ttk.Button(ai_row, text="🚀 启动调试 Chrome",
                   command=self._launch_debug_chrome).grid(
            row=1, column=5, columnspan=2, sticky="w", padx=(8, 0), pady=(4, 0))
        ttk.Button(ai_row, text="❓ Chrome 启动失败怎么办",
                   command=self._show_chrome_help).grid(
            row=1, column=7, columnspan=3, sticky="w", pady=(4, 0))

        # 第三行:Chrome 可执行文件路径(可选,留空则自动探测)
        ttk.Label(ai_row, text="Chrome 路径:").grid(row=2, column=0, sticky="w", pady=(4, 0))
        chrome_entry = ttk.Entry(ai_row, textvariable=self.gpt_chrome_path_var, width=56)
        chrome_entry.grid(row=2, column=1, columnspan=6, sticky="we", pady=(4, 0))
        ttk.Button(ai_row, text="浏览", width=6,
                   command=self._pick_chrome_exe).grid(row=2, column=7, padx=2, pady=(4, 0))
        ttk.Button(ai_row, text="自动探测", width=10,
                   command=self._auto_detect_chrome).grid(row=2, column=8, padx=2, pady=(4, 0))
        ttk.Label(ai_row, text="(留空会自动探测,Windows 常见:C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe)",
                  foreground="#888", font=("Microsoft YaHei", 8)).grid(
            row=3, column=0, columnspan=13, sticky="w", pady=(2, 0))

        # 第四行:素材库
        ttk.Label(ai_row, text="📁 素材库:",
                  font=("Microsoft YaHei", 9, "bold")).grid(row=4, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(ai_row, textvariable=self.asset_dir_var, width=56).grid(
            row=4, column=1, columnspan=6, sticky="we", pady=(6, 0))
        ttk.Button(ai_row, text="浏览", width=6,
                   command=self._pick_asset_dir).grid(row=4, column=7, padx=2, pady=(6, 0))
        ttk.Button(ai_row, text="🔄 扫描", width=10,
                   command=self._rescan_assets).grid(row=4, column=8, padx=2, pady=(6, 0))
        ttk.Button(ai_row, text="📋 查看库", width=10,
                   command=self._show_asset_library).grid(row=4, column=9, padx=2, pady=(6, 0))
        ttk.Checkbutton(ai_row, text="发送时自动上传匹配图",
                        variable=self.auto_upload_var).grid(
            row=4, column=10, columnspan=2, sticky="w", padx=(4, 0), pady=(6, 0))
        ttk.Checkbutton(ai_row, text="🎨 自动注入色板",
                        variable=self.auto_inject_color_var).grid(
            row=4, column=12, columnspan=3, sticky="w", padx=(4, 0), pady=(6, 0))
        # v0.11:每场景后自动新开对话
        ttk.Checkbutton(ai_row, text="🔄 每场景新开对话",
                        variable=self.auto_new_chat_var).grid(
            row=4, column=15, columnspan=3, sticky="w", padx=(4, 0), pady=(6, 0))
        ttk.Label(ai_row,
                  text="💡 把参考图放进素材库目录,文件名就是关键字(如「林默.png」)。AI 对话会自动匹配上传。",
                  foreground="#2277aa", font=("Microsoft YaHei", 8)).grid(
            row=5, column=0, columnspan=13, sticky="w", pady=(2, 0))

        # v0.10:GPT 图保存目录(填了就不弹窗)
        ttk.Label(ai_row, text="📥 GPT 图目录:",
                  font=("Microsoft YaHei", 9, "bold")).grid(row=6, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(ai_row, textvariable=self.gpt_save_dir_var, width=56).grid(
            row=6, column=1, columnspan=6, sticky="we", pady=(6, 0))
        ttk.Button(ai_row, text="浏览", width=6,
                   command=self._pick_gpt_save_dir).grid(row=6, column=7, padx=2, pady=(6, 0))
        ttk.Button(ai_row, text="📂 打开", width=10,
                   command=lambda: self._open_file(self.gpt_save_dir_var.get())
                   ).grid(row=6, column=8, padx=2, pady=(6, 0))
        ttk.Label(ai_row,
                  text="💡 批量生图会直接存到这里,不再每次弹窗。留空才会弹窗。",
                  foreground="#2277aa", font=("Microsoft YaHei", 8)).grid(
            row=7, column=0, columnspan=13, sticky="w", pady=(2, 0))

        # 中部:左任务表 + 右提示原则
        mid = ttk.Frame(self.root)
        mid.pack(fill="both", expand=True, padx=8, pady=4)

        # 左:任务列表
        left = ttk.LabelFrame(mid, text="场景任务列表(拖图片进来 / 双击编辑未完成项 / 双击完成项预览视频)",
                              padding=4)
        left.pack(side="left", fill="both", expand=True, padx=(0, 4))

        btn_bar = ttk.Frame(left)
        btn_bar.pack(fill="x")
        ttk.Button(btn_bar, text="➕ 添加场景", command=self._add_scene).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="✏️ 编辑选中", command=self._edit_scene).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="▶ 预览视频", command=self._preview_video).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="❌ 删除选中", command=self._delete_scene).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="📂 导入 CSV", command=self._import_csv).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="💾 导出 CSV", command=self._export_csv).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="🖼 批量 GPT 生图",
                   command=self._start_batch_gpt_images).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="🔍 自动匹配素材",
                   command=self._auto_match_assets_to_scenes).pack(side="left", padx=2)
        self.gpt_pause_btn = ttk.Button(btn_bar, text="⏸ 暂停生图",
                                         command=self._toggle_gpt_pause, state="disabled")
        self.gpt_pause_btn.pack(side="left", padx=2)
        self.gpt_stop_btn = ttk.Button(btn_bar, text="⏹ 停止生图",
                                        command=self._stop_batch_gpt, state="disabled")
        self.gpt_stop_btn.pack(side="left", padx=2)
        ttk.Button(btn_bar, text="🗑 清空", command=self._clear_scenes).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="🔄 重置状态", command=self._reset_status).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="📖 Wan 提示词库",
                   command=self._show_wan22_preset_dialog).pack(side="left", padx=2)

        # 拖放区提示(无拖拽库时显示文案)
        tip_text = "💡 可将图片文件 直接拖入下方列表,弹窗自动分配首尾帧" + \
                   ("" if HAS_DND else "(建议 pip install tkinterdnd2 获得最佳拖拽体验)")
        ttk.Label(left, text=tip_text, foreground="#2277aa").pack(fill="x", pady=(2, 0))

        cols = ("seq", "name", "start", "end", "color", "prompt", "status")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=16)
        headings = [("seq", "#", 40), ("name", "场景名", 130),
                    ("start", "首帧图", 140), ("end", "尾帧图", 140),
                    ("color", "🎨", 80),
                    ("prompt", "提示词", 240), ("status", "状态", 90)]
        for key, text, w in headings:
            self.tree.heading(key, text=text)
            self.tree.column(key, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, pady=(4, 0))
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        self.tree.bind("<Button-3>", self._show_tree_menu)  # 右键菜单

        # 右:提示词原则
        right = ttk.LabelFrame(mid, text="📖 Wan 2.2 动作指令编写原则", padding=4)
        right.pack(side="right", fill="both", padx=(4, 0))
        tips = scrolledtext.ScrolledText(right, width=42, height=26, wrap="word",
                                         font=("Microsoft YaHei", 9))
        tips.insert("1.0", WAN22_TIPS)
        tips.configure(state="disabled")
        tips.pack(fill="both", expand=True)

        # 底部:运行按钮 + 日志
        bot = ttk.Frame(self.root)
        bot.pack(fill="both", padx=8, pady=4)

        run_bar = ttk.Frame(bot)
        run_bar.pack(fill="x")
        self.run_btn = ttk.Button(run_bar, text="🚀 开始批量生成", command=self._start_batch)
        self.run_btn.pack(side="left", padx=2)
        self.stop_btn = ttk.Button(run_bar, text="⏹ 停止", command=self._stop_batch, state="disabled")
        self.stop_btn.pack(side="left", padx=2)
        ttk.Button(run_bar, text="🧪 测试连接", command=self._test_conn).pack(side="left", padx=2)
        ttk.Button(run_bar, text="📁 打开输出目录", command=self._open_output).pack(side="left", padx=2)
        ttk.Button(run_bar, text="❓ 如何导出 API JSON", command=self._show_help).pack(side="left", padx=2)

        self.progress = ttk.Progressbar(run_bar, mode="determinate", length=300)
        self.progress.pack(side="right", padx=4)
        self.progress_label = ttk.Label(run_bar, text="0 / 0")
        self.progress_label.pack(side="right")

        log_frame = ttk.LabelFrame(bot, text="运行日志", padding=4)
        log_frame.pack(fill="both", expand=True, pady=(4, 0))
        self.log_box = scrolledtext.ScrolledText(log_frame, height=10,
                                                 font=("Consolas", 9), wrap="word")
        self.log_box.pack(fill="both", expand=True)

    # ---------- 配置持久化 ----------
    def _load_last_config(self):
        # v0.9: 先找 SCRIPT_DIR 下的配置,再 fallback 到 CWD(兼容旧版)
        p = Path(CONFIG_FILE)
        if not p.exists():
            cwd_config = Path.cwd() / "wan22_gui_config.json"
            if cwd_config.exists():
                p = cwd_config
            else:
                return
        try:
            with open(p, "r", encoding="utf-8") as f:
                c = json.load(f)
            self.host_var.set(c.get("host", DEFAULT_HOST))
            self.workflow_path.set(c.get("workflow", ""))
            self.output_var.set(c.get("output", DEFAULT_OUTPUT_DIR))
            self.start_node_var.set(c.get("start_node", ""))
            self.end_node_var.set(c.get("end_node", ""))
            self.prompt_node_var.set(c.get("prompt_node", ""))
            self.prompt_field_var.set(c.get("prompt_field", "text"))
            # 分辨率(v0.8 默认横屏 — 如果 config 里没有相关 key,走 v0.8 默认)
            self.width_var.set(c.get("width", 960))
            self.height_var.set(c.get("height", 544))
            self.length_var.set(c.get("length", 81))
            self.orient_var.set(c.get("orient", "横屏 16:9"))
            # AI 配置
            self.ai_key_var.set(c.get("ai_key", ""))
            self.ai_base_var.set(c.get("ai_base", DEFAULT_OPENAI_BASE))
            self.ai_model_var.set(c.get("ai_model", DEFAULT_OPENAI_MODEL))
            self.gpt_url_var.set(c.get("gpt_url", DEFAULT_GPT_WEB_URL))
            self.gpt_mode_var.set(c.get("gpt_mode", "attach"))
            self.gpt_port_var.set(c.get("gpt_port", 9222))
            self.gpt_chrome_path_var.set(c.get("gpt_chrome_path", ""))
            self.asset_dir_var.set(c.get("asset_dir", self.asset_dir_var.get()))
            self.auto_upload_var.set(c.get("auto_upload", True))
            self.auto_inject_color_var.set(c.get("auto_inject_color", True))
            # v0.10:GPT 图保存目录 + 4 个首尾帧模板
            self.gpt_save_dir_var.set(c.get("gpt_save_dir", self.gpt_save_dir_var.get()))
            self._tmpl_start_empty = c.get("tmpl_start_empty", DEFAULT_START_EMPTY_TMPL)
            self._tmpl_start_people = c.get("tmpl_start_people", DEFAULT_START_PEOPLE_TMPL)
            self._tmpl_end_empty = c.get("tmpl_end_empty", DEFAULT_END_EMPTY_TMPL)
            self._tmpl_end_people = c.get("tmpl_end_people", DEFAULT_END_PEOPLE_TMPL)
            # v0.11:自动新开对话开关
            self.auto_new_chat_var.set(c.get("auto_new_chat", True))
            # 自动扫素材库一次
            d = self.asset_dir_var.get()
            if d and Path(d).exists():
                try:
                    self.asset_lib.set_root(d)
                except Exception:
                    pass
            # 加载上次的场景
            for s in c.get("scenes", []):
                self.scenes.append(s)
            self._refresh_tree()
            # 自动重新加载工作流
            if self.workflow_path.get() and Path(self.workflow_path.get()).exists():
                try:
                    self.workflow = load_workflow_api(self.workflow_path.get())
                    self._scan_nodes(silent=True)
                except Exception:
                    pass
        except Exception:
            pass

    def _save_config(self):
        c = {
            "host": self.host_var.get(),
            "workflow": self.workflow_path.get(),
            "output": self.output_var.get(),
            "start_node": self.start_node_var.get(),
            "end_node": self.end_node_var.get(),
            "prompt_node": self.prompt_node_var.get(),
            "prompt_field": self.prompt_field_var.get(),
            "width": self.width_var.get(),
            "height": self.height_var.get(),
            "length": self.length_var.get(),
            "orient": self.orient_var.get(),
            "ai_key": self.ai_key_var.get(),
            "ai_base": self.ai_base_var.get(),
            "ai_model": self.ai_model_var.get(),
            "gpt_url": self.gpt_url_var.get(),
            "gpt_mode": self.gpt_mode_var.get(),
            "gpt_port": self.gpt_port_var.get(),
            "gpt_chrome_path": self.gpt_chrome_path_var.get(),
            "asset_dir": self.asset_dir_var.get(),
            "auto_upload": self.auto_upload_var.get(),
            "auto_inject_color": self.auto_inject_color_var.get(),
            # v0.10:GPT 图保存目录 + 4 个首尾帧模板
            "gpt_save_dir": self.gpt_save_dir_var.get(),
            "tmpl_start_empty": self._tmpl_start_empty,
            "tmpl_start_people": self._tmpl_start_people,
            "tmpl_end_empty": self._tmpl_end_empty,
            "tmpl_end_people": self._tmpl_end_people,
            # v0.11
            "auto_new_chat": self.auto_new_chat_var.get(),
            "scenes": self.scenes,
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(c, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ---------- 工作流 & 节点 ----------
    def _pick_workflow(self):
        p = filedialog.askopenfilename(title="选择 workflow API JSON",
                                       filetypes=[("JSON", "*.json")])
        if not p:
            return
        self.workflow_path.set(p)
        try:
            self.workflow = load_workflow_api(p)
            self._scan_nodes()
        except WorkflowFormatError as e:
            # 格式错误,提供清晰指引 + 提示打开帮助
            if messagebox.askyesno("格式错误",
                                   f"{e}\n\n是否现在查看详细图文说明?"):
                self._show_help()
        except Exception as e:
            messagebox.showerror("加载失败", f"{e}")

    def _show_help(self):
        """弹出一个帮助窗口,图文并茂说明如何导出 API JSON"""
        help_text = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "    如何从 ComfyUI 导出 API 格式 JSON\n"
            "     (汉化版 / 秋叶整合包 专用指引)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🎯 为什么要导出 API 格式?\n\n"
            "  你手头的 JSON 有两种:\n"
            "  ① UI 格式(画布布局):网上下载或自己保存的原版\n"
            "     ❌ 里面装的是节点坐标、连线、颜色等绘图信息\n"
            "     ❌ 不能直接执行,本工具也读不懂\n\n"
            "  ② API 格式(运行指令):需要手动导出\n"
            "     ✅ 只保留「节点ID → class_type → 输入参数」\n"
            "     ✅ ComfyUI 的 /prompt 接口认这个,本工具也只认这个\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📝 汉化版操作步骤(推荐方法):\n\n"
            "  第 1 步:打开 ComfyUI 浏览器页面\n"
            "         一般是 http://127.0.0.1:8188\n\n"
            "  第 2 步:加载你的原始工作流\n"
            "         直接把 .json 文件 拖进画布\n"
            "         或者 侧边菜单点「加载」\n\n"
            "  第 3 步:打开「开发者模式」\n"
            "         点 右上角 齿轮图标 ⚙ (设置)\n"
            "         往下翻,找到这一项 👇\n"
            "            ☑ 启用开发者模式\n"
            "         (英文原名:Enable Dev mode Options)\n"
            "         勾上,关闭设置窗口\n\n"
            "  第 4 步:导出 API 格式 ✨ 关键\n"
            "         回到主界面,看 右侧竖向工具栏\n"
            "         或 顶部菜单(新版UI),会多出一个按钮:\n"
            "         ┌────────────────────────┐\n"
            "         │   保存 (API 格式)      │  ← 点它\n"
            "         │   Save (API Format)   │\n"
            "         └────────────────────────┘\n"
            "         浏览器会下载一个 json 文件\n"
            "         建议改名:workflow_api.json\n\n"
            "  第 5 步:回到本工具\n"
            "         点顶部「浏览...」选这份 API JSON\n"
            "         → 点「扫描节点」\n"
            "         → 添加场景 → 🚀 开始批量生成\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔄 不同版本的按钮位置(都试试):\n\n"
            "  【秋叶整合包 / 经典汉化版】\n"
            "     右侧浮动工具栏最下方\n"
            "     「保存(API 格式)」 或 图标是一个小齿轮+保存\n\n"
            "  【新版 ComfyUI 顶栏菜单】\n"
            "     顶部「工作流」菜单 → 「导出(API)」\n"
            "     英文:Workflow → Export (API)\n\n"
            "  【快捷键(所有版本通用)】\n"
            "     Ctrl + Shift + S\n"
            "     弹出保存对话框里选「API Format」\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🆘 实在找不到按钮的救急方案:\n\n"
            "  方法A:浏览器开发者工具\n"
            "     在 ComfyUI 页面按 F12 打开控制台,\n"
            "     输入:\n"
            "        app.graphToPrompt().then(r=>{\n"
            "          const blob = new Blob([JSON.stringify(\n"
            "            r.output, null, 2)],{type:'application/json'});\n"
            "          const a = document.createElement('a');\n"
            "          a.href = URL.createObjectURL(blob);\n"
            "          a.download = 'workflow_api.json';\n"
            "          a.click();\n"
            "        })\n"
            "     按回车,浏览器会自动下载 workflow_api.json\n\n"
            "  方法B:升级到最新版 ComfyUI\n"
            "     老版本的汉化包可能把这个按钮汉化成其他名字,\n"
            "     建议整合包更新一下,新版都有醒目的「导出 API」\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💡 小贴士:\n"
            "  • 导出只用做一次,保存好 workflow_api.json\n"
            "  • 以后修改工作流才需要重新导出\n"
            "  • 不同工作流(I2V / T2V / 升频等)要各自导出一份"
        )
        dlg = tk.Toplevel(self.root)
        dlg.title("如何导出 API 格式 JSON — 详细说明")
        dlg.geometry("720x620")
        dlg.transient(self.root)

        box = scrolledtext.ScrolledText(dlg, wrap="word",
                                        font=("Microsoft YaHei", 10),
                                        padx=12, pady=8)
        box.insert("1.0", help_text)
        box.configure(state="disabled")
        box.pack(fill="both", expand=True)

        ttk.Button(dlg, text="我知道了", command=dlg.destroy).pack(pady=8)

    def _scan_nodes(self, silent=False):
        if not self.workflow:
            if self.workflow_path.get() and Path(self.workflow_path.get()).exists():
                try:
                    self.workflow = load_workflow_api(self.workflow_path.get())
                except Exception as e:
                    if not silent:
                        messagebox.showerror("错误", f"加载失败: {e}")
                    return
            else:
                if not silent:
                    messagebox.showwarning("提示", "请先选择 workflow JSON")
                return
        load_imgs, text_nodes = scan_workflow(self.workflow)
        # 填下拉
        self.start_combo["values"] = load_imgs
        self.end_combo["values"] = load_imgs
        self.prompt_combo["values"] = text_nodes
        # 自动推荐
        if load_imgs and not self.start_node_var.get():
            self.start_node_var.set(load_imgs[0])
        if len(load_imgs) >= 2 and not self.end_node_var.get():
            self.end_node_var.set(load_imgs[1])
        if text_nodes and not self.prompt_node_var.get():
            self.prompt_node_var.set(text_nodes[0])
            f = find_prompt_field(self.workflow, text_nodes[0])
            if f:
                self.prompt_field_var.set(f)
        if not silent:
            msg = (f"扫描完成!\n\nLoadImage 节点: {load_imgs}\n"
                   f"可能的提示词节点: {text_nodes}\n\n"
                   f"已自动选择。如不对请手动下拉选择。")
            messagebox.showinfo("扫描结果", msg)
        self._log(f"🔍 扫描完成: LoadImage={load_imgs}, Text={text_nodes}")
        # 读取 workflow 里的分辨率回填 UI
        res = scan_workflow_resolution(self.workflow)
        if res:
            w, h, l = res
            self.width_var.set(w)
            self.height_var.set(h)
            if l is not None:
                self.length_var.set(l)
            # 推断方向
            if w == h:
                self.orient_var.set("方图 1:1")
            elif w * 9 == h * 16:  # 16:9
                self.orient_var.set("横屏 16:9")
            elif h * 9 == w * 16:  # 9:16
                self.orient_var.set("竖屏 9:16")
            else:
                self.orient_var.set("自定义")
            self._log(f"📐 已从 workflow 读取分辨率: {w}×{h}" + (f" ×{l}帧" if l else ""))

    def _on_orient_change(self, _event=None):
        """切换方向预设时自动填 width/height(保持 length 不变)"""
        o = self.orient_var.get()
        # 基于当前宽高的短边推算
        cur_w = self.width_var.get()
        cur_h = self.height_var.get()
        short = min(cur_w, cur_h) if cur_w > 0 and cur_h > 0 else 544
        if o == "竖屏 9:16":
            # 544x960 经典值,以 short 为宽
            self.width_var.set(544)
            self.height_var.set(960)
        elif o == "横屏 16:9":
            self.width_var.set(960)
            self.height_var.set(544)
        elif o == "方图 1:1":
            self.width_var.set(short)
            self.height_var.set(short)
        # 自定义:不动

    def _swap_wh(self):
        w = self.width_var.get()
        h = self.height_var.get()
        self.width_var.set(h)
        self.height_var.set(w)
        # 重新推断方向
        if w == h:
            self.orient_var.set("方图 1:1")
        elif h * 9 == w * 16:  # 换后 w:h = 16:9
            self.orient_var.set("横屏 16:9")
        elif w * 9 == h * 16:  # 换后 w:h = 9:16
            self.orient_var.set("竖屏 9:16")
        else:
            self.orient_var.set("自定义")

    def _on_prompt_node_change(self, _event=None):
        if not self.workflow:
            return
        nid = self.prompt_node_var.get()
        if nid in self.workflow:
            f = find_prompt_field(self.workflow, nid)
            if f:
                self.prompt_field_var.set(f)

    def _pick_output(self):
        p = filedialog.askdirectory(title="选择视频输出目录")
        if p:
            self.output_var.set(p)

    # ---------- 场景管理 ----------
    def _add_scene(self):
        self._scene_dialog()

    def _edit_scene(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(self.tree.item(sel[0], "values")[0]) - 1
        self._scene_dialog(idx)

    def _on_tree_double_click(self, event):
        """双击:已完成项播放视频,否则编辑"""
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(self.tree.item(sel[0], "values")[0]) - 1
        if 0 <= idx < len(self.scenes):
            s = self.scenes[idx]
            video_path = s.get("video_path")
            # 已完成且视频存在 → 预览;否则编辑
            if s.get("status", "").startswith("✅") and video_path and Path(video_path).exists():
                self._open_file(video_path)
                return
        self._edit_scene()

    def _preview_video(self):
        """打开选中任务生成的视频"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先选中一个已完成的任务")
            return
        idx = int(self.tree.item(sel[0], "values")[0]) - 1
        if not (0 <= idx < len(self.scenes)):
            return
        s = self.scenes[idx]
        vp = s.get("video_path")
        if not vp or not Path(vp).exists():
            # 尝试在输出目录里按场景名找
            out = Path(self.output_var.get())
            found = None
            for ext in (".mp4", ".webm", ".mkv", ".gif", ".mov"):
                cand = out / f"{s['name']}{ext}"
                if cand.exists():
                    found = cand
                    break
            if found:
                vp = str(found)
                self.scenes[idx]["video_path"] = vp
            else:
                messagebox.showwarning("提示", f"找不到视频文件。\n场景:{s['name']}")
                return
        self._open_file(vp)

    def _reset_status(self):
        """把所有任务状态清空,可重跑"""
        if not self.scenes:
            return
        if not messagebox.askyesno("确认", "重置所有任务状态?(可以再次跑一遍,视频文件不会删除)"):
            return
        for s in self.scenes:
            s["status"] = ""
            s["video_path"] = ""
        self._refresh_tree()

    def _open_file(self, path):
        """用系统默认程序打开文件"""
        try:
            p = str(Path(path).resolve())
            if sys.platform == "win32":
                os.startfile(p)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", p])
            else:
                subprocess.Popen(["xdg-open", p])
        except Exception as e:
            messagebox.showerror("打开失败", str(e))

    # ---------- 右键菜单 ----------
    def _show_tree_menu(self, event):
        row = self.tree.identify_row(event.y)
        if row:
            self.tree.selection_set(row)
        sel = self.tree.selection()
        menu = tk.Menu(self.root, tearoff=0)
        if sel:
            idx = int(self.tree.item(sel[0], "values")[0]) - 1
            s = self.scenes[idx] if 0 <= idx < len(self.scenes) else None
            menu.add_command(label="✏️ 编辑", command=self._edit_scene)
            if s and s.get("video_path") and Path(s.get("video_path","")).exists():
                menu.add_command(label="▶ 预览视频", command=self._preview_video)
                menu.add_command(label="📁 在文件夹中显示",
                                 command=lambda: self._reveal_file(s["video_path"]))
            menu.add_separator()
            # v0.9: 单独操作
            menu.add_command(label="🖼 单独 GPT 生图(此场景)",
                             command=lambda: self._single_gpt_image(idx))
            menu.add_command(label="▶ 单独生成视频(此场景)",
                             command=lambda: self._single_batch(idx))
            menu.add_separator()
            menu.add_command(label="❌ 删除", command=self._delete_scene)
        menu.add_command(label="➕ 添加场景", command=self._add_scene)
        menu.post(event.x_root, event.y_root)

    def _reveal_file(self, path):
        """在系统文件管理器中高亮显示该文件"""
        try:
            p = str(Path(path).resolve())
            if sys.platform == "win32":
                subprocess.Popen(["explorer", "/select,", p])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", p])
            else:
                subprocess.Popen(["xdg-open", str(Path(p).parent)])
        except Exception as e:
            messagebox.showerror("失败", str(e))

    # ---------- 拖放处理 ----------
    def _enable_drag_drop(self):
        """如果有 tkinterdnd2 就启用原生拖拽"""
        if HAS_DND:
            try:
                self.tree.drop_target_register(DND_FILES)
                self.tree.dnd_bind("<<Drop>>", self._on_drop)
            except Exception:
                pass

    def _on_drop(self, event):
        """处理拖入的图片文件"""
        raw = event.data
        # tkinterdnd2 在有空格路径时会用 { } 括起来,解析一下
        paths = self._parse_dnd_paths(raw)
        imgs = [p for p in paths if Path(p).suffix.lower() in
                (".png", ".jpg", ".jpeg", ".webp", ".bmp")]
        if not imgs:
            messagebox.showinfo("提示", "没有识别到图片文件")
            return
        self._handle_dropped_images(imgs)

    @staticmethod
    def _parse_dnd_paths(data):
        """解析 DND 拖拽字符串,返回路径列表"""
        if not data:
            return []
        paths = []
        cur = ""
        in_brace = False
        for c in data:
            if c == "{":
                in_brace = True
            elif c == "}":
                in_brace = False
                if cur:
                    paths.append(cur)
                    cur = ""
            elif c == " " and not in_brace:
                if cur:
                    paths.append(cur)
                    cur = ""
            else:
                cur += c
        if cur:
            paths.append(cur)
        return [p.strip().strip('"').strip("'") for p in paths if p.strip()]

    def _handle_dropped_images(self, img_list):
        """拖入图片后的分配流程:弹窗让用户选择"""
        img_list = sorted(img_list)  # 按文件名排序,让成对图容易识别

        dlg = tk.Toplevel(self.root)
        dlg.title(f"拖入了 {len(img_list)} 张图片 — 如何分配?")
        dlg.geometry("560x340")
        dlg.transient(self.root)
        dlg.grab_set()

        ttk.Label(dlg, text=f"共拖入 {len(img_list)} 张图片,请选择处理方式:",
                  font=("Microsoft YaHei", 11, "bold")).pack(pady=10)

        # 列出前 5 张做预览
        box = tk.Text(dlg, height=8, wrap="none")
        for i, p in enumerate(img_list[:10]):
            box.insert("end", f"  {i+1}. {Path(p).name}\n")
        if len(img_list) > 10:
            box.insert("end", f"  ... 共 {len(img_list)} 张\n")
        box.configure(state="disabled")
        box.pack(fill="x", padx=20)

        hint = ttk.Label(dlg, foreground="#666")
        hint.pack(pady=(6, 0))

        def mode_pair():
            """两张一组:第1张首帧,第2张尾帧"""
            if len(img_list) < 2 or len(img_list) % 2 != 0:
                messagebox.showwarning("提示",
                    f"需要偶数张图才能两两配对,当前 {len(img_list)} 张", parent=dlg)
                return
            cnt = 0
            for i in range(0, len(img_list), 2):
                self.scenes.append({
                    "name": f"场景_{len(self.scenes)+1:02d}",
                    "start": img_list[i],
                    "end": img_list[i+1],
                    "prompt": "",
                    "gpt_prompt": "",
                    "color": "",
                    "status": "",
                    "video_path": "",
                })
                cnt += 1
            self._refresh_tree()
            self._log(f"📥 成对添加了 {cnt} 个场景")
            dlg.destroy()

        def mode_single_to_selected():
            """只拖 1 张 → 添加到当前选中行的首帧 or 尾帧"""
            sel = self.tree.selection()
            if not sel:
                messagebox.showwarning("提示", "请先选中一行再拖", parent=dlg)
                return
            idx = int(self.tree.item(sel[0], "values")[0]) - 1
            # 二次弹窗问是首帧还是尾帧
            choice = messagebox.askyesnocancel(
                "分配",
                f"将 {Path(img_list[0]).name} 放到:\n\n「是」= 首帧    「否」= 尾帧    「取消」= 新建场景",
                parent=dlg)
            if choice is None:
                mode_new_empty()
                return
            if choice:
                self.scenes[idx]["start"] = img_list[0]
            else:
                self.scenes[idx]["end"] = img_list[0]
            self._refresh_tree()
            self._log(f"📥 已将图片设为场景 [{self.scenes[idx]['name']}] 的{'首帧' if choice else '尾帧'}")
            dlg.destroy()

        def mode_new_empty():
            """每张图单独一个场景,首尾帧相同(用户后续自己改)"""
            for p in img_list:
                self.scenes.append({
                    "name": f"场景_{len(self.scenes)+1:02d}_{Path(p).stem}",
                    "start": p, "end": p,
                    "prompt": "", "gpt_prompt": "", "color": "", "status": "", "video_path": "",
                })
            self._refresh_tree()
            self._log(f"📥 每张图创建一个场景({len(img_list)} 个)")
            dlg.destroy()

        def mode_all_start():
            """全部作为首帧,尾帧留空"""
            for p in img_list:
                self.scenes.append({
                    "name": f"场景_{len(self.scenes)+1:02d}_{Path(p).stem}",
                    "start": p, "end": "",
                    "prompt": "", "gpt_prompt": "", "color": "", "status": "", "video_path": "",
                })
            self._refresh_tree()
            dlg.destroy()

        btn_frame = ttk.Frame(dlg)
        btn_frame.pack(pady=12)

        if len(img_list) == 1:
            hint.config(text="推荐:分配到选中行,或单独建一个场景")
            ttk.Button(btn_frame, text="分配到选中行(首/尾帧)",
                       command=mode_single_to_selected).grid(row=0, column=0, padx=4, pady=3)
            ttk.Button(btn_frame, text="新建 1 个场景(首=尾)",
                       command=mode_new_empty).grid(row=0, column=1, padx=4, pady=3)
        else:
            hint.config(text="推荐:按文件名排序后,两张一组配成首尾帧")
            ttk.Button(btn_frame, text=f"📐 两两配对({len(img_list)//2} 个场景)",
                       command=mode_pair).grid(row=0, column=0, padx=4, pady=3)
            ttk.Button(btn_frame, text=f"📋 每张图建 1 个场景({len(img_list)} 个)",
                       command=mode_new_empty).grid(row=0, column=1, padx=4, pady=3)
            ttk.Button(btn_frame, text=f"🎯 全部作为首帧({len(img_list)} 个)",
                       command=mode_all_start).grid(row=1, column=0, padx=4, pady=3)
            if self.tree.selection():
                ttk.Button(btn_frame, text="🎯 分配第 1 张到选中行",
                           command=mode_single_to_selected).grid(row=1, column=1, padx=4, pady=3)

        ttk.Button(dlg, text="取消", command=dlg.destroy).pack(pady=(8, 10))

    def _delete_scene(self):
        sel = self.tree.selection()
        if not sel:
            return
        indices = sorted([int(self.tree.item(s, "values")[0]) - 1 for s in sel], reverse=True)
        for i in indices:
            del self.scenes[i]
        self._refresh_tree()

    def _clear_scenes(self):
        if self.scenes and not messagebox.askyesno("确认", "清空所有任务?"):
            return
        self.scenes.clear()
        self._refresh_tree()

    def _scene_dialog(self, edit_idx=None):
        dlg = tk.Toplevel(self.root)
        dlg.title("编辑场景" if edit_idx is not None else "添加场景")
        dlg.geometry("720x560")
        dlg.transient(self.root)

        s = self.scenes[edit_idx] if edit_idx is not None else {
            "name": "", "start": "", "end": "",
            "prompt": "", "gpt_prompt": "", "color": ""
        }

        name_v = tk.StringVar(value=s["name"])
        start_v = tk.StringVar(value=s["start"])
        end_v = tk.StringVar(value=s["end"])
        color_v = tk.StringVar(value=s.get("color", ""))

        pad = {"padx": 6, "pady": 4}
        ttk.Label(dlg, text="场景名:").grid(row=0, column=0, sticky="e", **pad)
        ttk.Entry(dlg, textvariable=name_v, width=60).grid(row=0, column=1, columnspan=2, sticky="we", **pad)

        ttk.Label(dlg, text="首帧图片:").grid(row=1, column=0, sticky="e", **pad)
        ttk.Entry(dlg, textvariable=start_v, width=50).grid(row=1, column=1, sticky="we", **pad)
        ttk.Button(dlg, text="浏览...", command=lambda: self._pick_img(start_v)).grid(row=1, column=2, **pad)

        ttk.Label(dlg, text="尾帧图片:").grid(row=2, column=0, sticky="e", **pad)
        ttk.Entry(dlg, textvariable=end_v, width=50).grid(row=2, column=1, sticky="we", **pad)
        ttk.Button(dlg, text="浏览...", command=lambda: self._pick_img(end_v)).grid(row=2, column=2, **pad)

        # 色板下拉
        ttk.Label(dlg, text="🎨 色板:").grid(row=3, column=0, sticky="e", **pad)
        color_frame = ttk.Frame(dlg)
        color_frame.grid(row=3, column=1, columnspan=2, sticky="we", **pad)
        ids = [""] + self.color_anchors.list_ids()
        labels = ["(不指定)"] + [f"{aid}  {self.color_anchors.get_name(aid)}"
                                  for aid in self.color_anchors.list_ids()]
        color_cb = ttk.Combobox(color_frame, width=30, state="readonly", values=labels)
        try:
            color_cb.current(ids.index(color_v.get()))
        except ValueError:
            color_cb.current(0)
        color_cb.pack(side="left", padx=(0, 6))

        def auto_detect_color():
            aid = self.color_anchors.auto_detect(prompt_box.get("1.0", "end"))
            if aid in ids:
                color_cb.current(ids.index(aid))
        ttk.Button(color_frame, text="🔍 根据提示词自动检测",
                   command=auto_detect_color).pack(side="left")

        ttk.Label(dlg, text="Wan 提示词:").grid(row=4, column=0, sticky="ne", **pad)
        prompt_box = tk.Text(dlg, width=60, height=6, wrap="word", font=("Microsoft YaHei", 10))
        prompt_box.insert("1.0", s["prompt"])
        prompt_box.grid(row=4, column=1, columnspan=2, sticky="we", **pad)

        ttk.Label(dlg, text="💡 建议格式:镜头 + 主体动作 + 环境,20 字以内,动词优先",
                  foreground="#888").grid(row=5, column=1, columnspan=2, sticky="w", padx=6)

        # GPT 提示词(用于批量 GPT 生图,留空则 fallback 用 Wan 提示词)
        ttk.Label(dlg, text="🖼 GPT 提示词:").grid(row=6, column=0, sticky="ne", **pad)
        gpt_prompt_box = tk.Text(dlg, width=60, height=5, wrap="word",
                                  font=("Microsoft YaHei", 10))
        gpt_prompt_box.insert("1.0", s.get("gpt_prompt", ""))
        gpt_prompt_box.grid(row=6, column=1, columnspan=2, sticky="we", **pad)

        ttk.Label(dlg, text="💡 专门用于 GPT 画图的描述(画面、构图、风格)。留空时用 Wan 提示词。",
                  foreground="#888").grid(row=7, column=1, columnspan=2, sticky="w", padx=6)

        def save():
            old = self.scenes[edit_idx] if edit_idx is not None else {}
            sel = color_cb.current()
            chosen_color = ids[sel] if 0 <= sel < len(ids) else ""
            new_s = {
                "name": name_v.get().strip(),
                "start": start_v.get().strip(),
                "end": end_v.get().strip(),
                "prompt": prompt_box.get("1.0", "end").strip(),
                "gpt_prompt": gpt_prompt_box.get("1.0", "end").strip(),
                "color": chosen_color,
                "status": old.get("status", ""),
                "video_path": old.get("video_path", ""),
            }
            if not new_s["name"]:
                messagebox.showwarning("提示", "场景名不能为空", parent=dlg)
                return
            if edit_idx is None:
                self.scenes.append(new_s)
            else:
                self.scenes[edit_idx] = new_s
            self._refresh_tree()
            dlg.destroy()

        bbar = ttk.Frame(dlg)
        bbar.grid(row=8, column=0, columnspan=3, pady=10)
        ttk.Button(bbar, text="保存", command=save).pack(side="left", padx=6)
        ttk.Button(bbar, text="取消", command=dlg.destroy).pack(side="left", padx=6)

        dlg.columnconfigure(1, weight=1)

    def _pick_img(self, var):
        p = filedialog.askopenfilename(title="选择图片",
                                       filetypes=[("图片", "*.png *.jpg *.jpeg *.webp *.bmp"), ("所有", "*.*")])
        if p:
            var.set(p)

    def _import_csv(self):
        p = filedialog.askopenfilename(title="导入 scenes.csv", filetypes=[("CSV", "*.csv")])
        if not p:
            return
        try:
            with open(p, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                cnt = 0
                for row in reader:
                    if not row.get("scene_name"):
                        continue
                    self.scenes.append({
                        "name": row["scene_name"].strip(),
                        "start": row.get("start_image", "").strip(),
                        "end": row.get("end_image", "").strip(),
                        "prompt": row.get("prompt", "").strip(),
                        "gpt_prompt": row.get("gpt_prompt", "").strip(),
                        "color": row.get("color", "").strip(),
                        "status": "",
                        "video_path": "",
                    })
                    cnt += 1
            self._refresh_tree()
            self._log(f"📥 从 {p} 导入 {cnt} 条")
            # v0.9: 导入后自动匹配素材库
            self._auto_match_assets_to_scenes(silent=True)
        except Exception as e:
            messagebox.showerror("导入失败", str(e))

    def _export_csv(self):
        if not self.scenes:
            messagebox.showwarning("提示", "没有任务可导出")
            return
        p = filedialog.asksaveasfilename(title="保存为 CSV", defaultextension=".csv",
                                         filetypes=[("CSV", "*.csv")])
        if not p:
            return
        try:
            with open(p, "w", encoding="utf-8-sig", newline="") as f:
                w = csv.writer(f)
                w.writerow(["scene_name", "start_image", "end_image", "prompt", "gpt_prompt", "color"])
                for s in self.scenes:
                    w.writerow([s["name"], s["start"], s["end"], s["prompt"],
                                s.get("gpt_prompt", ""),
                                s.get("color", "")])
            self._log(f"📤 已导出到 {p}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for i, s in enumerate(self.scenes, 1):
            cid = s.get("color", "")
            cname = self.color_anchors.get_name(cid) if cid else ""
            self.tree.insert("", "end", values=(
                i, s["name"],
                Path(s["start"]).name if s["start"] else "",
                Path(s["end"]).name if s["end"] else "",
                cname,
                s["prompt"][:50] + ("..." if len(s["prompt"]) > 50 else ""),
                s.get("status", "")
            ))

    def _update_status(self, idx, status):
        if 0 <= idx < len(self.scenes):
            self.scenes[idx]["status"] = status
            self._refresh_tree()

    # ---------- 日志 ----------
    def _log(self, msg):
        self.log_q.put(msg)

    def _drain_log(self):
        try:
            while True:
                msg = self.log_q.get_nowait()
                ts = time.strftime("%H:%M:%S")
                self.log_box.insert("end", f"[{ts}] {msg}\n")
                self.log_box.see("end")
        except queue.Empty:
            pass
        self.root.after(100, self._drain_log)

    # ---------- AI / OpenAI ----------
    def _test_ai_api(self):
        """测试 OpenAI 兼容 API 连通性"""
        key = self.ai_key_var.get().strip()
        if not key:
            messagebox.showwarning("提示", "请先填写 API Key")
            return
        self._log("🧪 测试 AI API...")

        def _worker():
            try:
                r = openai_chat(
                    key, self.ai_base_var.get(), self.ai_model_var.get(),
                    [{"role": "user", "content": "只回复一个字:好"}],
                    temperature=0,
                )
                self._log(f"✅ AI 连接成功,模型回复: {r.strip()[:50]}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "成功", f"✅ API 连接正常\n\n模型回复:{r.strip()[:100]}"))
            except Exception as e:
                self._log(f"❌ AI 连接失败: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "失败", f"❌ {e}\n\n检查:\n1. API Key 是否正确\n"
                            f"2. Base URL 是否正确(如中转站要以 /v1 结尾)\n"
                            f"3. 模型名是否支持"))
        threading.Thread(target=_worker, daemon=True).start()

    def _open_novel_dialog(self):
        """小说一键改分镜"""
        if not self.ai_key_var.get().strip():
            if not messagebox.askyesno("提示",
                "尚未配置 API Key,要继续吗?\n(可以先准备好文本,配置后再点生成)"):
                return

        dlg = tk.Toplevel(self.root)
        dlg.title("📚 小说一键改分镜 — 粘贴小说内容,AI 自动拆成 Wan 2.2 分镜")
        dlg.geometry("900x680")
        dlg.transient(self.root)

        # 顶部参数
        top = ttk.Frame(dlg, padding=8)
        top.pack(fill="x")

        ttk.Label(top, text="目标分镜数:").pack(side="left")
        count_var = tk.IntVar(value=20)
        ttk.Spinbox(top, from_=5, to=60, textvariable=count_var, width=6).pack(side="left", padx=(2, 12))

        ttk.Label(top, text="风格/世界观偏好:").pack(side="left")
        style_var = tk.StringVar(value="现代都市/异能/国漫条漫风格")
        ttk.Entry(top, textvariable=style_var, width=40).pack(side="left", padx=(2, 12))

        clear_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(top, text="生成前清空现有任务", variable=clear_var).pack(side="left")

        # 小说文本框
        ttk.Label(dlg, text="📖 小说内容(可粘贴整章):").pack(fill="x", padx=8)
        novel_box = scrolledtext.ScrolledText(dlg, height=18, wrap="word",
                                              font=("Microsoft YaHei", 10))
        novel_box.pack(fill="both", expand=True, padx=8, pady=4)

        # 底部日志
        status_var = tk.StringVar(value="准备就绪。粘贴小说内容后,点「🚀 生成分镜」")
        ttk.Label(dlg, textvariable=status_var, foreground="#2277aa").pack(fill="x", padx=8)

        btn_bar = ttk.Frame(dlg)
        btn_bar.pack(fill="x", padx=8, pady=8)

        def do_generate():
            novel = novel_box.get("1.0", "end").strip()
            if len(novel) < 50:
                messagebox.showwarning("提示", "小说内容太短,请粘贴至少一章", parent=dlg)
                return
            if not self.ai_key_var.get().strip():
                messagebox.showerror("提示", "请先配置 API Key", parent=dlg)
                return

            gen_btn.config(state="disabled")
            status_var.set("⏳ 正在调用 AI 拆分镜,大概需要 20-60 秒...")

            def _worker():
                try:
                    user_msg = (f"风格:{style_var.get()}\n"
                                f"目标分镜数:{count_var.get()} 个\n\n"
                                f"小说原文:\n{novel}")
                    txt = openai_chat(
                        self.ai_key_var.get(), self.ai_base_var.get(),
                        self.ai_model_var.get(),
                        [
                            {"role": "system", "content": NOVEL_SYSTEM_PROMPT},
                            {"role": "user", "content": user_msg},
                        ],
                        temperature=0.7,
                        timeout=300,
                    )
                    scenes = extract_json_array(txt)
                    if not isinstance(scenes, list) or not scenes:
                        raise RuntimeError("AI 返回格式错误")

                    def apply():
                        if clear_var.get():
                            self.scenes.clear()
                        valid_ids = set(self.color_anchors.list_ids())
                        for i, s in enumerate(scenes, 1):
                            name = s.get("name") or f"场景_{i:02d}"
                            prompt = s.get("prompt") or ""
                            # 色板:优先用 AI 返回的,无效则根据提示词自动推测
                            color = s.get("color", "")
                            if color not in valid_ids:
                                color = self.color_anchors.auto_detect(prompt)
                            self.scenes.append({
                                "name": name, "start": "", "end": "",
                                "prompt": prompt, "gpt_prompt": "", "color": color,
                                "status": "", "video_path": "",
                            })
                        self._refresh_tree()
                        status_var.set(f"✅ 已生成 {len(scenes)} 个分镜,任务列表已更新")
                        self._log(f"📚 小说改编完成:{len(scenes)} 个分镜"
                                  f"(已自动分配色板)")
                        gen_btn.config(state="normal")
                        messagebox.showinfo("完成",
                            f"✅ 已生成 {len(scenes)} 个分镜并填入任务列表!\n\n"
                            f"🎨 已自动分配色板(可在场景列表「🎨」列查看)\n\n"
                            f"下一步:\n"
                            f"• 为每个分镜添加首尾帧图片(拖图/浏览)\n"
                            f"• 或对选中的分镜用「✨ 给选中生成提示词」二次优化\n"
                            f"• 发送时会自动注入色板描述,保持整组画面色彩连贯", parent=dlg)
                    self.root.after(0, apply)
                except Exception as e:
                    self._log(f"❌ 小说改编失败: {e}")
                    self.root.after(0, lambda: (
                        status_var.set(f"❌ 失败: {e}"),
                        gen_btn.config(state="normal"),
                        messagebox.showerror("失败", str(e), parent=dlg),
                    ))
            threading.Thread(target=_worker, daemon=True).start()

        def paste_from_gpt():
            """从 GPT 网页抓取最新回复作为小说内容"""
            if not self.gpt_ctrl or not self.gpt_ctrl.is_alive():
                messagebox.showinfo("提示", "请先点顶部「🌐 打开 GPT」启动浏览器", parent=dlg)
                return
            txt = self.gpt_ctrl.get_last_reply()
            if not txt:
                messagebox.showinfo("提示", "未获取到 GPT 回复", parent=dlg)
                return
            novel_box.delete("1.0", "end")
            novel_box.insert("1.0", txt)
            status_var.set(f"📥 已导入 GPT 最新回复({len(txt)} 字)")

        gen_btn = ttk.Button(btn_bar, text="🚀 生成分镜", command=do_generate)
        gen_btn.pack(side="left", padx=4)
        ttk.Button(btn_bar, text="📥 从 GPT 网页导入",
                   command=paste_from_gpt).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="📁 从 txt 文件导入",
                   command=lambda: self._load_novel_file(novel_box)).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="关闭", command=dlg.destroy).pack(side="right", padx=4)

    def _load_novel_file(self, text_widget):
        p = filedialog.askopenfilename(title="选择小说 txt 文件",
                                       filetypes=[("文本", "*.txt *.md"), ("所有", "*.*")])
        if not p:
            return
        try:
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(p, "r", encoding="gbk", errors="ignore") as f:
                content = f.read()
        text_widget.delete("1.0", "end")
        text_widget.insert("1.0", content)

    def _ai_gen_prompts(self):
        """对选中场景(或全部没填 prompt 的)用 AI 生成动作指令"""
        if not self.ai_key_var.get().strip():
            messagebox.showerror("提示", "请先配置 API Key")
            return
        sel = self.tree.selection()
        if sel:
            indices = [int(self.tree.item(s, "values")[0]) - 1 for s in sel]
            label = f"已选中 {len(indices)} 个场景"
        else:
            indices = [i for i, s in enumerate(self.scenes) if not s.get("prompt")]
            if not indices:
                messagebox.showinfo("提示", "没有需要生成提示词的场景")
                return
            label = f"自动对 {len(indices)} 个无提示词的场景"

        if not messagebox.askyesno("确认", f"{label}调用 AI 生成 Wan 2.2 指令?"):
            return
        self._log(f"✨ {label}调用 AI 生成提示词...")

        def _worker():
            ok, fail = 0, 0
            for idx in indices:
                s = self.scenes[idx]
                try:
                    user_msg = f"场景名:{s['name']}"
                    if s.get("prompt"):
                        user_msg += f"\n已有描述(请优化):{s['prompt']}"
                    r = openai_chat(
                        self.ai_key_var.get(), self.ai_base_var.get(),
                        self.ai_model_var.get(),
                        [
                            {"role": "system", "content": PROMPT_SYSTEM_PROMPT},
                            {"role": "user", "content": user_msg},
                        ],
                        temperature=0.7, timeout=60,
                    )
                    clean = r.strip().strip('"').strip("「").strip("」").strip("「").strip()
                    # 去掉可能的句号
                    if clean.endswith("。"):
                        clean = clean[:-1]
                    self.scenes[idx]["prompt"] = clean
                    self._log(f"  [{idx+1}] {s['name']} → {clean[:40]}")
                    ok += 1
                except Exception as e:
                    self._log(f"  [{idx+1}] {s['name']} ❌ {e}")
                    fail += 1
            self.root.after(0, self._refresh_tree)
            self._log(f"✨ AI 生成完成:成功 {ok}, 失败 {fail}")
        threading.Thread(target=_worker, daemon=True).start()

    # ---------- GPT 网页控制 ----------
    def _on_gpt_mode_change(self, _event=None):
        """显示当前模式的含义"""
        mode = self._get_gpt_mode()
        tips = {
            "attach": "🔒 将连接到已运行的 Chrome(需先点「🚀 启动调试 Chrome」)",
            "standalone": "📦 独立启动,保持登录。❗ 需关掉所有 Chrome 窗口",
            "temp": "⚡ 临时启动,每次需重新登录,但不会有 profile 冲突",
        }
        self._log(tips.get(mode, ""))

    def _get_gpt_mode(self):
        """从下拉框的长文本里提取 mode 字符串"""
        raw = self.gpt_mode_var.get()
        for k in ("attach", "standalone", "temp"):
            if raw.startswith(k):
                return k
        return "standalone"

    def _pick_chrome_exe(self):
        """浏览选择 chrome.exe / chrome"""
        p = filedialog.askopenfilename(
            title="选择 Chrome 可执行文件",
            filetypes=[("Chrome", "chrome.exe chrome"), ("所有", "*.*")])
        if p:
            self.gpt_chrome_path_var.set(p)
            self._log(f"✓ Chrome 路径已设置: {p}")

    def _auto_detect_chrome(self):
        """自动探测 Chrome 路径"""
        p = GPTWebController.find_chrome_exe()
        if p:
            self.gpt_chrome_path_var.set(p)
            self._log(f"✓ 自动探测到 Chrome: {p}")
            messagebox.showinfo("找到了", f"✅ Chrome 路径:\n\n{p}")
        else:
            self._log("❌ 未自动探测到 Chrome")
            messagebox.showwarning("没找到",
                "未在常见位置找到 Chrome。\n\n"
                "常见位置:\n"
                "  Windows: C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\n"
                "  macOS:   /Applications/Google Chrome.app/Contents/MacOS/Google Chrome\n\n"
                "请点「浏览」按钮手动指定,或先安装 Chrome。")

    def _get_chrome_path(self):
        """取用户配置的 chrome 路径,空则返回 None 让控制器自动探测"""
        p = self.gpt_chrome_path_var.get().strip()
        return p if p else None

    # ---------- 素材库 ----------
    def _pick_asset_dir(self):
        p = filedialog.askdirectory(title="选择素材库目录")
        if p:
            self.asset_dir_var.set(p)
            self._rescan_assets()

    def _pick_gpt_save_dir(self):
        """v0.10:选 GPT 图保存目录,选完记忆到 config.json"""
        cur = self.gpt_save_dir_var.get().strip() or str(SCRIPT_DIR)
        p = filedialog.askdirectory(title="选择 GPT 图保存目录", initialdir=cur)
        if p:
            self.gpt_save_dir_var.set(p)
            self._log(f"📥 GPT 图保存目录已设为:{p}")

    def _rescan_assets(self):
        """扫描素材库目录,建立索引"""
        d = self.asset_dir_var.get().strip()
        if not d:
            messagebox.showwarning("提示", "请先填素材库目录")
            return
        p = Path(d)
        if not p.exists():
            if messagebox.askyesno("提示", f"目录不存在,是否创建?\n{d}"):
                p.mkdir(parents=True, exist_ok=True)
            else:
                return
        self.asset_lib.set_root(d)
        n = len(self.asset_lib._index)
        self._log(f"📁 素材库扫描完成:{n} 张图片,位于 {d}")
        if n == 0:
            messagebox.showinfo("提示",
                f"目录为空或没有图片:\n{d}\n\n"
                f"使用方法:\n"
                f"1. 把参考图拖到这个目录\n"
                f"2. 文件名改成匹配关键字,比如:\n"
                f"   林默.png、苏郁.jpg、蔷薇宫.png\n"
                f"3. 可选:在目录里放一个 aliases.json 配置别名\n\n"
                f"点 OK 打开目录")
            self._open_file(d)
        else:
            sample = list(self.asset_lib._index.keys())[:8]
            self._log(f"   样本关键字: {', '.join(sample)}{'...' if n > 8 else ''}")

    def _show_asset_library(self):
        """显示素材库内容的对话框"""
        # 先扫一次(如果还没扫)
        if not self.asset_lib._index:
            d = self.asset_dir_var.get().strip()
            if d and Path(d).exists():
                self.asset_lib.set_root(d)

        dlg = tk.Toplevel(self.root)
        dlg.title("📁 素材库浏览")
        dlg.geometry("720x560")
        dlg.transient(self.root)

        top_bar = ttk.Frame(dlg, padding=6)
        top_bar.pack(fill="x")
        ttk.Label(top_bar,
                  text=f"素材库目录: {self.asset_dir_var.get()}\n"
                       f"共 {len(self.asset_lib._index)} 张图片"
                       f",{len(self.asset_lib._aliases)} 条别名映射",
                  justify="left", foreground="#2277aa").pack(side="left")
        ttk.Button(top_bar, text="🔄 刷新",
                   command=lambda: (self.asset_lib.rescan(), _refresh())).pack(side="right", padx=2)
        ttk.Button(top_bar, text="📁 打开目录",
                   command=lambda: self._open_file(self.asset_dir_var.get())).pack(side="right", padx=2)
        ttk.Button(top_bar, text="➕ 编辑别名",
                   command=self._edit_aliases).pack(side="right", padx=2)

        cols = ("keyword", "path")
        tree = ttk.Treeview(dlg, columns=cols, show="headings", height=20)
        tree.heading("keyword", text="关键字(文件名)")
        tree.heading("path", text="路径")
        tree.column("keyword", width=180)
        tree.column("path", width=460)
        tree.pack(fill="both", expand=True, padx=6, pady=4)

        def _refresh():
            tree.delete(*tree.get_children())
            for k, p in self.asset_lib.list_all():
                tree.insert("", "end", values=(k, p))
            for alias, main in self.asset_lib._aliases.items():
                real = self.asset_lib._index.get(main, "(指向不存在的主名)")
                tree.insert("", "end", values=(f"{alias} → {main}", real),
                            tags=("alias",))
            tree.tag_configure("alias", foreground="#888")
        _refresh()

        # 测试匹配
        test_frame = ttk.LabelFrame(dlg, text="🔍 测试匹配", padding=4)
        test_frame.pack(fill="x", padx=6, pady=4)
        test_var = tk.StringVar(value="苏郁走进蔷薇宫,向林默问好")
        ttk.Entry(test_frame, textvariable=test_var, width=60).pack(side="left", padx=2)

        def do_test():
            found = self.asset_lib.match(test_var.get())
            if found:
                msg = "✅ 匹配到 " + str(len(found)) + " 张:\n" + \
                      "\n".join(f"  • {k} → {Path(p).name}" for k, p in found)
            else:
                msg = "❌ 没有匹配到"
            messagebox.showinfo("匹配测试", msg, parent=dlg)

        ttk.Button(test_frame, text="测试", command=do_test).pack(side="left", padx=2)

        ttk.Button(dlg, text="关闭", command=dlg.destroy).pack(pady=4)

    def _edit_aliases(self):
        """编辑 aliases.json"""
        d = self.asset_dir_var.get().strip()
        if not d or not Path(d).exists():
            messagebox.showwarning("提示", "请先设置好素材库目录")
            return
        alias_file = Path(d) / "aliases.json"
        if not alias_file.exists():
            example = {
                "林默": ["林渊", "主角", "渊哥"],
                "苏郁": ["苏老板", "苏女神"],
            }
            alias_file.write_text(json.dumps(example, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
        self._open_file(str(alias_file))
        messagebox.showinfo("提示",
            "已打开 aliases.json(文本编辑器)。\n\n"
            "格式:\n"
            '{\n  "正式名": ["别名1", "别名2"],\n  ...\n}\n\n'
            "编辑保存后回来点「🔄 扫描」生效。")

    # ---------- v0.9: 自动匹配素材到场景 ----------
    def _auto_match_assets_to_scenes(self, silent=False):
        """扫描素材库,对所有场景的 prompt 做角色匹配并在日志中显示结果"""
        # 确保素材库已扫描
        if not self.asset_lib._index:
            d = self.asset_dir_var.get().strip()
            if d and Path(d).exists():
                self.asset_lib.set_root(d)
        if not self.asset_lib._index:
            if not silent:
                messagebox.showinfo("提示",
                    "素材库为空或未设置。\n请先在「素材库」处选择目录并放入角色参考图。")
            return
        if not self.scenes:
            if not silent:
                messagebox.showinfo("提示", "任务列表为空,请先导入 CSV 或添加场景。")
            return

        total_matched = 0
        total_scenes = len(self.scenes)
        self._log(f"\n🔍 开始自动匹配素材(共 {total_scenes} 个场景,"
                  f"素材库 {len(self.asset_lib._index)} 张图)")
        for i, s in enumerate(self.scenes):
            raw = (s.get("gpt_prompt") or "").strip() or (s.get("prompt") or "").strip()
            if not raw:
                continue
            matched = self.asset_lib.match(raw)
            if matched:
                total_matched += 1
                names = ", ".join(k for k, _ in matched)
                self._log(f"   ✅ [{i+1}] {s['name']} → 匹配: {names}")
            else:
                self._log(f"   ⬜ [{i+1}] {s['name']} → 无匹配")

        self._log(f"🔍 匹配完成:{total_matched}/{total_scenes} 个场景有角色匹配")
        if not silent:
            messagebox.showinfo("匹配结果",
                f"匹配完成!\n\n"
                f"有角色匹配的场景:{total_matched} / {total_scenes}\n"
                f"素材库图片数:{len(self.asset_lib._index)}\n\n"
                f"详情请查看日志窗口。")

    # ---------- v0.9: 单独 GPT 生图(选中场景) ----------
    def _single_gpt_image(self, idx):
        """对单个场景执行 GPT 生图(右键菜单调用)"""
        if not (0 <= idx < len(self.scenes)):
            return
        if not self.gpt_ctrl or not self.gpt_ctrl.is_alive():
            messagebox.showerror("错误",
                "GPT 网页未挂载,请先点「🌐 打开 GPT」并确保登录。")
            return
        s = self.scenes[idx]
        # v0.10:优先用记忆目录,填了就不弹窗
        save_dir = self.gpt_save_dir_var.get().strip()
        if save_dir:
            try:
                Path(save_dir).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                messagebox.showerror("错误", f"GPT 图保存目录无法创建:\n{save_dir}\n\n{e}")
                return
        else:
            default_dir = str(SCRIPT_DIR / "gpt_images")
            save_dir = filedialog.askdirectory(
                title=f"选择保存目录(场景: {s['name']})",
                initialdir=default_dir)
            if not save_dir:
                return
            self.gpt_save_dir_var.set(save_dir)

        self.stop_flag.clear()
        self.gpt_pause_flag.clear()
        self.gpt_batch_running = True
        self._update_gpt_batch_buttons()

        def _worker():
            try:
                self._run_single_gpt_scene(idx, save_dir)
            finally:
                self.gpt_batch_running = False
                self.root.after(0, self._update_gpt_batch_buttons)

        threading.Thread(target=_worker, daemon=True).start()

    def _run_single_gpt_scene(self, idx, save_dir):
        """GPT 生图单场景逻辑(可被批量和单独调用共享)"""
        s = self.scenes[idx]
        self._log(f"\n🎨 [单独] {s['name']}")
        try:
            raw = (s.get("gpt_prompt") or "").strip() or (s.get("prompt") or "").strip()
            if not raw:
                self._log("   ⚠️ 无 prompt,跳过")
                return

            # 注入色板
            cid = s.get("color", "")
            if cid and self.auto_inject_color_var.get():
                raw = self.color_anchors.inject(raw, cid)
                self._log(f"   🎨 已注入色板:{self.color_anchors.get_name(cid)}")

            has_people = any(kw in raw for kw in self._PEOPLE_KEYWORDS)
            self._log(f"   🧭 prompt 模式:{'人物镜头' if has_people else '纯环境空镜'}")

            # 素材库匹配上传
            matched = self.asset_lib.match(raw) if self.asset_lib._index else []
            ref_paths = [p for _, p in matched]
            if ref_paths and self.auto_upload_var.get():
                self._log(f"   📎 匹配到 {len(ref_paths)} 张参考图:"
                          f"{', '.join(k for k, _ in matched)}")
                try:
                    self.gpt_ctrl.upload_files(ref_paths)
                    time.sleep(1.5)
                except Exception as e:
                    self._log(f"   ⚠️ 参考图上传失败(继续发送):{e}")

            sub = Path(save_dir) / f"{idx+1:02d}_{s['name']}"

            # 首帧
            self._log(f"   📤 [阶段 1/2] 请求首帧图...")
            start_prompt = self._build_start_frame_prompt(raw, has_people)
            start_urls, _ = self._request_single_gpt_image(start_prompt, timeout=300)
            if not start_urls:
                self._log("   ❌ 首帧超时")
                return
            start_saved = self.gpt_ctrl.download_last_images(str(sub), urls=start_urls[:1])
            if not start_saved:
                self._log("   ❌ 首帧下载失败")
                return
            start_path = start_saved[0]
            self._log(f"   ✅ 首帧已保存: {start_path}")

            time.sleep(2)

            # 尾帧
            self._log(f"   📤 [阶段 2/2] 请求尾帧图...")
            end_prompt = self._build_end_frame_prompt(raw, has_people)
            end_urls, _ = self._request_single_gpt_image(end_prompt, timeout=300)
            if not end_urls:
                self._log("   ⚠️ 尾帧超时,回退为用首帧作为尾帧")
                end_path = start_path
            else:
                end_saved = self.gpt_ctrl.download_last_images(str(sub), urls=end_urls[:1])
                if not end_saved:
                    self._log("   ⚠️ 尾帧下载失败,回退用首帧")
                    end_path = start_path
                else:
                    end_path = end_saved[0]
                    self._log(f"   ✅ 尾帧已保存: {end_path}")

            # 回填
            s["start"] = start_path
            s["end"] = end_path
            self.scenes[idx] = s
            self.root.after(0, self._refresh_tree)
            self._log(f"   🎉 单独 GPT 生图完成: {s['name']}")
            # v0.11:单独生图也自动新开对话,保持行为一致
            if self.auto_new_chat_var.get():
                try:
                    self.gpt_ctrl.new_chat(wait_ready=True, timeout=10)
                except Exception as e:
                    self._log(f"   ⚠️ 新开对话失败:{e}")
            self._save_config()
        except Exception as e:
            self._log(f"   ❌ 失败: {e}")

    # ---------- v0.9: 单独生成视频(选中场景) ----------
    def _single_batch(self, idx):
        """对单个场景执行 ComfyUI 视频生成(右键菜单调用)"""
        if not (0 <= idx < len(self.scenes)):
            return
        if not self.workflow:
            messagebox.showerror("错误", "请先选择并加载工作流 JSON")
            return
        s = self.scenes[idx]
        if not s.get("start") or not s.get("end"):
            messagebox.showerror("错误", f"场景「{s['name']}」缺少首帧或尾帧图片")
            return
        if not (self.start_node_var.get() and self.end_node_var.get() and self.prompt_node_var.get()):
            messagebox.showerror("错误", "请先完成节点配置(点「扫描节点」)")
            return

        self._save_config()
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.stop_flag.clear()
        self.progress["maximum"] = 1
        self.progress["value"] = 0

        def _worker():
            host = self.host_var.get()
            out_dir = self.output_var.get()
            sn = self.start_node_var.get()
            en = self.end_node_var.get()
            pn = self.prompt_node_var.get()
            pf = self.prompt_field_var.get()

            self._log(f"\n🎬 [单独] {s['name']}")
            self._update_status(idx, "处理中...")
            try:
                self._log(f"   📤 上传首帧: {Path(s['start']).name}")
                start_name = upload_image(host, s["start"])
                self._log(f"   📤 上传尾帧: {Path(s['end']).name}")
                end_name = upload_image(host, s["end"])

                final_prompt = s["prompt"]
                cid = s.get("color", "")
                if cid and self.auto_inject_color_var.get():
                    final_prompt = self.color_anchors.inject(final_prompt, cid)

                wf = patch_workflow(self.workflow, sn, en, pn, pf,
                                    start_name, end_name, final_prompt,
                                    width=self.width_var.get(),
                                    height=self.height_var.get(),
                                    length=self.length_var.get())
                pid = queue_prompt(host, wf)
                self._log(f"   📮 已排队 prompt_id={pid[:8]}...")
                h = wait_done(host, pid, log_cb=self._log)
                videos = find_output_videos(h)
                if not videos:
                    self._log("   ⚠️ 无视频输出")
                    self._update_status(idx, "❌ 无输出")
                else:
                    for v in videos:
                        ext = Path(v["filename"]).suffix or ".mp4"
                        target_name = f"{s['name']}{ext}"
                        path = download_output(host, v, out_dir, rename_to=target_name)
                        self._log(f"   ✅ 保存: {path}")
                        self.scenes[idx]["video_path"] = str(path)
                    self._update_status(idx, "✅ 完成")
            except Exception as e:
                self._log(f"   ❌ 失败: {e}")
                self._update_status(idx, "❌ 失败")

            self.progress["value"] = 1
            self.progress_label.config(text="1 / 1")
            self._log(f"🎉 单独生成完成: {s['name']}")
            self.run_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self._save_config()

        threading.Thread(target=_worker, daemon=True).start()

    # ---------- v0.9: GPT 批量生图暂停/继续/停止控制 ----------
    def _toggle_gpt_pause(self):
        """暂停 / 继续 GPT 批量生图"""
        if self.gpt_pause_flag.is_set():
            self.gpt_pause_flag.clear()
            self._log("▶ 继续 GPT 批量生图")
            self.gpt_pause_btn.config(text="⏸ 暂停生图")
        else:
            self.gpt_pause_flag.set()
            self._log("⏸ 已暂停,完成当前场景后暂停")
            self.gpt_pause_btn.config(text="▶ 继续生图")

    def _stop_batch_gpt(self):
        """停止 GPT 批量生图"""
        self.stop_flag.set()
        self.gpt_pause_flag.clear()  # 如果暂停中也要能停止
        self._log("⏹ 收到停止信号,将在当前场景后停止")

    def _update_gpt_batch_buttons(self):
        """根据 gpt_batch_running 状态更新按钮"""
        if self.gpt_batch_running:
            self.gpt_pause_btn.config(state="normal")
            self.gpt_stop_btn.config(state="normal")
        else:
            self.gpt_pause_btn.config(state="disabled", text="⏸ 暂停生图")
            self.gpt_stop_btn.config(state="disabled")

    # ---------- 色彩锚点管理对话框 ----------
    def _show_color_anchors_dialog(self):
        """色彩锚点管理对话框 — 管理/编辑/应用色板"""
        dlg = tk.Toplevel(self.root)
        dlg.title("🎨 色彩锚点管理")
        dlg.geometry("900x640")
        dlg.transient(self.root)

        # 顶部说明
        top = ttk.Frame(dlg, padding=8)
        top.pack(fill="x")
        ttk.Label(top,
                  text="💡 色彩锚点 = 给每格分镜贴一个色板标签,发送提示词时自动把色板描述拼到前面。\n"
                       "这样 AI 画图 / Wan 2.2 生视频时,整组画面色彩不会漂移。\n"
                       "左边:所有色板。右边:选中色板的详细内容。底部:应用到任务列表的操作。",
                  foreground="#2277aa", justify="left").pack(side="left")

        # 主体:左列表 + 右详细
        main = ttk.Frame(dlg)
        main.pack(fill="both", expand=True, padx=8, pady=4)

        # 左:列表
        left = ttk.LabelFrame(main, text="色板列表", padding=4)
        left.pack(side="left", fill="y")

        lb_cols = ("id", "name")
        lb = ttk.Treeview(left, columns=lb_cols, show="headings", height=18)
        lb.heading("id", text="ID")
        lb.heading("name", text="名称")
        lb.column("id", width=130)
        lb.column("name", width=130)
        lb.pack(fill="y", expand=True, padx=4, pady=4)

        lb_btns = ttk.Frame(left)
        lb_btns.pack(fill="x", padx=4)
        ttk.Button(lb_btns, text="➕ 新建", width=8,
                   command=lambda: _new()).pack(side="left", padx=1)
        ttk.Button(lb_btns, text="❌ 删除", width=8,
                   command=lambda: _delete()).pack(side="left", padx=1)
        ttk.Button(lb_btns, text="🔄 恢复默认", width=12,
                   command=lambda: _restore()).pack(side="left", padx=1)

        # 右:详细
        right = ttk.LabelFrame(main, text="详细内容", padding=6)
        right.pack(side="right", fill="both", expand=True, padx=(6, 0))

        ttk.Label(right, text="ID(英文小写,唯一):").grid(row=0, column=0, sticky="w", pady=2)
        id_v = tk.StringVar()
        id_entry = ttk.Entry(right, textvariable=id_v, width=40)
        id_entry.grid(row=0, column=1, sticky="we", pady=2)

        ttk.Label(right, text="显示名(中文/带 emoji):").grid(row=1, column=0, sticky="w", pady=2)
        name_v = tk.StringVar()
        ttk.Entry(right, textvariable=name_v, width=40).grid(row=1, column=1, sticky="we", pady=2)

        ttk.Label(right, text="关键字(逗号/空格分隔):").grid(row=2, column=0, sticky="nw", pady=2)
        kw_v = tk.StringVar()
        ttk.Entry(right, textvariable=kw_v, width=40).grid(row=2, column=1, sticky="we", pady=2)

        ttk.Label(right, text="色板正文(将被注入到提示词前):").grid(row=3, column=0, sticky="nw", pady=2)
        text_box = scrolledtext.ScrolledText(right, width=58, height=10, wrap="word",
                                             font=("Microsoft YaHei", 10))
        text_box.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=4)
        right.rowconfigure(4, weight=1)
        right.columnconfigure(1, weight=1)

        # 预览区
        ttk.Label(right, text="🔍 注入效果预览:",
                  foreground="#2277aa").grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 0))
        preview = scrolledtext.ScrolledText(right, width=58, height=5, wrap="word",
                                            font=("Consolas", 9), foreground="#444")
        preview.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=2)
        right.rowconfigure(6, weight=1)

        save_btn_frame = ttk.Frame(right)
        save_btn_frame.grid(row=7, column=0, columnspan=2, pady=6, sticky="w")
        ttk.Button(save_btn_frame, text="💾 保存此色板",
                   command=lambda: _save_current()).pack(side="left", padx=2)
        ttk.Button(save_btn_frame, text="🔍 刷新预览",
                   command=lambda: _refresh_preview()).pack(side="left", padx=2)

        # 底部:批量操作
        bot = ttk.LabelFrame(dlg, text="应用到任务列表", padding=6)
        bot.pack(fill="x", padx=8, pady=4)
        ttk.Button(bot, text="🎨 应用选中色板到所选场景",
                   command=lambda: _apply_to_selected()).pack(side="left", padx=4)
        ttk.Button(bot, text="🔍 自动检测所有场景的色板",
                   command=lambda: _auto_detect_all()).pack(side="left", padx=4)
        ttk.Button(bot, text="关闭", command=dlg.destroy).pack(side="right", padx=4)

        # ---------- 状态 & 回调 ----------
        current_id = {"v": None}

        def _refresh_list():
            lb.delete(*lb.get_children())
            for aid in self.color_anchors.list_ids():
                a = self.color_anchors.get(aid)
                lb.insert("", "end", iid=aid, values=(aid, a["name"]))

        def _load_to_form(aid):
            a = self.color_anchors.get(aid)
            if not a:
                return
            current_id["v"] = aid
            id_v.set(aid)
            id_entry.configure(state="disabled")  # 已存在的 ID 不允许改(避免数据丢失)
            name_v.set(a["name"])
            kw_v.set(", ".join(a.get("keywords", [])))
            text_box.delete("1.0", "end")
            text_box.insert("1.0", a["text"])
            _refresh_preview()

        def _on_select(_event=None):
            sel = lb.selection()
            if sel:
                _load_to_form(sel[0])

        lb.bind("<<TreeviewSelect>>", _on_select)

        def _refresh_preview():
            txt = text_box.get("1.0", "end").strip()
            demo = "镜头缓慢推近 雨丝斜飘 角色抬头"
            preview.configure(state="normal")
            preview.delete("1.0", "end")
            preview.insert("1.0", f"{txt}\n{demo}" if txt else demo)
            preview.configure(state="disabled")

        def _save_current():
            aid = id_v.get().strip()
            if not aid:
                messagebox.showwarning("提示", "ID 不能为空", parent=dlg)
                return
            if not re.fullmatch(r"[a-z0-9_]+", aid):
                messagebox.showwarning("提示", "ID 只能用英文小写字母、数字、下划线", parent=dlg)
                return
            name = name_v.get().strip() or aid
            text = text_box.get("1.0", "end").strip()
            kws = [k.strip() for k in re.split(r"[,, \s]+", kw_v.get()) if k.strip()]
            self.color_anchors.set(aid, name, text, kws)
            _refresh_list()
            # 保持选中
            try:
                lb.selection_set(aid)
                lb.see(aid)
            except Exception:
                pass
            current_id["v"] = aid
            id_entry.configure(state="disabled")
            self._refresh_tree()  # 名称可能变了,任务表刷新一下
            messagebox.showinfo("已保存", f"色板「{name}」已保存到 color_anchors.json",
                                parent=dlg)

        def _new():
            current_id["v"] = None
            id_entry.configure(state="normal")
            id_v.set("")
            name_v.set("")
            kw_v.set("")
            text_box.delete("1.0", "end")
            text_box.insert("1.0", "【新色板】请在这里写色板描述,将被注入到提示词前。")
            _refresh_preview()
            id_entry.focus_set()

        def _delete():
            aid = current_id["v"]
            if not aid:
                messagebox.showinfo("提示", "请先在左侧选中一个色板", parent=dlg)
                return
            if not messagebox.askyesno("确认", f"删除色板「{aid}」?\n"
                                       "已经标记此色板的场景会变成无色板。", parent=dlg):
                return
            self.color_anchors.delete(aid)
            _refresh_list()
            _new()
            self._refresh_tree()

        def _restore():
            if not messagebox.askyesno("确认",
                "恢复 6 个默认色板(会覆盖同名色板,自定义色板不会被删)?",
                parent=dlg):
                return
            for aid, v in DEFAULT_COLOR_ANCHORS.items():
                self.color_anchors.set(aid, v["name"], v["text"], v.get("keywords", []))
            _refresh_list()
            self._refresh_tree()
            messagebox.showinfo("完成", "默认色板已恢复", parent=dlg)

        def _apply_to_selected():
            aid = current_id["v"]
            if not aid:
                messagebox.showinfo("提示", "请先在左侧选中一个色板", parent=dlg)
                return
            sel = self.tree.selection()
            if not sel:
                messagebox.showinfo("提示",
                    "请先到主界面任务列表选中要应用的场景(Ctrl/Shift 多选)",
                    parent=dlg)
                return
            indices = [int(self.tree.item(s, "values")[0]) - 1 for s in sel]
            for i in indices:
                if 0 <= i < len(self.scenes):
                    self.scenes[i]["color"] = aid
            self._refresh_tree()
            self._log(f"🎨 已将色板「{self.color_anchors.get_name(aid)}」应用到 {len(indices)} 个场景")
            messagebox.showinfo("完成",
                f"已把色板「{aid}」应用到 {len(indices)} 个场景", parent=dlg)

        def _auto_detect_all():
            if not self.scenes:
                messagebox.showinfo("提示", "任务列表是空的", parent=dlg)
                return
            if not messagebox.askyesno("确认",
                f"对全部 {len(self.scenes)} 个场景自动检测色板?\n"
                "(已经手动指定的会被覆盖。如不想覆盖请先手动备份。)", parent=dlg):
                return
            cnt = 0
            for s in self.scenes:
                aid = self.color_anchors.auto_detect(s.get("prompt", ""))
                s["color"] = aid
                cnt += 1
            self._refresh_tree()
            self._log(f"🎨 已对 {cnt} 个场景自动分配色板")
            messagebox.showinfo("完成", f"已对 {cnt} 个场景自动分配色板", parent=dlg)

        # 初始化
        _refresh_list()
        ids = self.color_anchors.list_ids()
        if ids:
            lb.selection_set(ids[0])
            _load_to_form(ids[0])
        else:
            _new()

    # ---------- 提示词库(GPT 和 Wan 2.2 共用逻辑) ----------
    def _load_presets(self, file_path, default_list=None):
        """从 JSON 文件读取提示词库,返回 list"""
        p = Path(file_path)
        if not p.exists():
            # 生成默认的样本
            if default_list is None:
                default_list = []
            try:
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(default_list, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            return default_list
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as e:
            self._log(f"⚠️ 读取 {file_path} 失败: {e}")
            return []

    def _save_presets(self, file_path, presets):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(presets, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log(f"⚠️ 保存 {file_path} 失败: {e}")

    def _init_preset_files(self):
        """启动时加载两份提示词库,并给出默认值"""
        gpt_defaults = [
            {"title": "让 GPT 生成分镜首帧",
             "text": "请按照下面分镜描述,生成一张国漫条漫风格的横版 16:9 首帧图:\n\n[在这里粘贴分镜描述]"},
            {"title": "让 GPT 生成分镜尾帧",
             "text": "基于上一张图的角色和场景,生成对应的尾帧图,展示动作完成后的状态:\n\n[动作描述]"},
            {"title": "人物设定图(三视图)",
             "text": "生成一位 20 岁亚洲男大学生的角色三视图(正面+侧面+背面),黑色短发,戴无框眼镜,白衬衫+牛仔裤,国漫半写实风格,9:16 竖版"},
            {"title": "场景概念图",
             "text": "生成一张 9:16 竖版场景概念图:雨夜后巷,远处霓虹闪烁,潮湿地面反光,国漫条漫风格"},
        ]
        wan22_defaults = [
            {"title": "镜头推近",
             "text": "镜头缓慢推近 雨丝斜飘 角色抬头"},
            {"title": "动作爆发",
             "text": "角色猛然前冲 拖出残影 水花四溅"},
            {"title": "情感慢镜",
             "text": "俯视镜头缓慢上升 角色瞳孔渐渐涣散"},
            {"title": "时空过渡",
             "text": "夜空转为晨光 云层流动 雨丝渐停"},
            {"title": "惊醒",
             "text": "角色猛然睁眼坐起 手按胸口"},
            {"title": "决心",
             "text": "阳光穿透云层洒落 角色握紧拳头"},
        ]
        self._prompt_presets = self._load_presets(self._prompt_presets_file, gpt_defaults)
        self._wan22_presets = self._load_presets(self._wan22_presets_file, wan22_defaults)

    def _add_prompt_preset(self, listbox):
        """给 GPT 提示词库新增一条"""
        self._preset_dialog(self._prompt_presets, self._prompt_presets_file, listbox)

    def _edit_prompt_preset(self, listbox):
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先选中一条")
            return
        self._preset_dialog(self._prompt_presets, self._prompt_presets_file, listbox, edit_idx=sel[0])

    def _del_prompt_preset(self, listbox):
        sel = listbox.curselection()
        if not sel:
            return
        if not messagebox.askyesno("确认", "删除选中的提示词?"):
            return
        for i in sorted(sel, reverse=True):
            del self._prompt_presets[i]
        self._save_presets(self._prompt_presets_file, self._prompt_presets)
        if hasattr(self, "_load_presets_cb"):
            self._load_presets_cb()

    def _load_prompt_presets_file(self):
        """打开提示词 JSON 文件手动编辑"""
        self._open_file(self._prompt_presets_file)
        messagebox.showinfo("提示",
            f"已打开 {self._prompt_presets_file}\n\n"
            f"格式:\n"
            f'[\n  {{"title": "标题", "text": "提示词内容"}},\n  ...\n]\n\n'
            f"编辑保存后重开 GPT 面板生效。")

    def _preset_dialog(self, presets_list, save_path, listbox, edit_idx=None):
        """通用的提示词编辑对话框"""
        dlg = tk.Toplevel(self.root)
        dlg.title("编辑提示词" if edit_idx is not None else "新增提示词")
        dlg.geometry("640x400")
        dlg.transient(self.root)

        p = presets_list[edit_idx] if edit_idx is not None else {"title": "", "text": ""}
        title_v = tk.StringVar(value=p.get("title", ""))

        ttk.Label(dlg, text="标题(用于列表显示):").pack(anchor="w", padx=8, pady=(8, 0))
        ttk.Entry(dlg, textvariable=title_v, width=70).pack(fill="x", padx=8, pady=2)

        ttk.Label(dlg, text="正文(插入到输入框的实际内容):").pack(anchor="w", padx=8, pady=(6, 0))
        text_box = scrolledtext.ScrolledText(dlg, height=12, wrap="word",
                                             font=("Microsoft YaHei", 10))
        text_box.insert("1.0", p.get("text", ""))
        text_box.pack(fill="both", expand=True, padx=8, pady=2)

        def save():
            title = title_v.get().strip()
            txt = text_box.get("1.0", "end").strip()
            if not title or not txt:
                messagebox.showwarning("提示", "标题和正文都不能空", parent=dlg)
                return
            new_p = {"title": title, "text": txt}
            if edit_idx is None:
                presets_list.append(new_p)
            else:
                presets_list[edit_idx] = new_p
            self._save_presets(save_path, presets_list)
            # 刷新列表
            if hasattr(self, "_load_presets_cb"):
                self._load_presets_cb()
            if hasattr(self, "_load_wan22_presets_cb"):
                self._load_wan22_presets_cb()
            dlg.destroy()

        bar = ttk.Frame(dlg)
        bar.pack(fill="x", padx=8, pady=8)
        ttk.Button(bar, text="保存", command=save).pack(side="left", padx=4)
        ttk.Button(bar, text="取消", command=dlg.destroy).pack(side="left", padx=4)

    def _show_frame_tmpl_dialog(self):
        """v0.10:4 个首尾帧硬性要求模板编辑器(2x2 tab)"""
        dlg = tk.Toplevel(self.root)
        dlg.title("⬜ 首尾帧硬性要求模板编辑")
        dlg.geometry("920x740")
        dlg.transient(self.root)

        ttk.Label(dlg,
                  text="💡 批量 / 单独 GPT 生图时,两次调用(首帧 + 尾帧)会各自注入一个模板。"
                       "病根在「尾帧模板」里曾经的「同一机位同一构图」— 现在改成要求明确差异。",
                  foreground="#2277aa", font=("Microsoft YaHei", 9),
                  wraplength=880, justify="left").pack(fill="x", padx=8, pady=(8, 4))

        nb = ttk.Notebook(dlg)
        nb.pack(fill="both", expand=True, padx=8, pady=4)

        widgets = {}

        def add_tab(tab_title, hint, attr, default):
            tab = ttk.Frame(nb)
            nb.add(tab, text=tab_title)
            ttk.Label(tab, text=hint, foreground="#444",
                      font=("Microsoft YaHei", 8),
                      wraplength=880, justify="left").pack(fill="x", padx=6, pady=(6, 2))
            txt = scrolledtext.ScrolledText(tab, wrap="word",
                                            font=("Microsoft YaHei", 10))
            txt.pack(fill="both", expand=True, padx=6, pady=4)
            txt.insert("1.0", getattr(self, attr))
            widgets[attr] = (txt, default)
            return tab

        add_tab("🎬 首帧·空镜",
                "适用:01/02/11/14/15/24/28 等无人物场景的首帧请求。",
                "_tmpl_start_empty", DEFAULT_START_EMPTY_TMPL)
        add_tab("👤 首帧·人物",
                "适用:有林默/林渊/苏郁等角色的场景首帧请求。",
                "_tmpl_start_people", DEFAULT_START_PEOPLE_TMPL)
        add_tab("🎬 尾帧·空镜 ⚠️病根",
                "⚠️ 这个模板是 PPT 感的主要病根 — 以前写「同一机位同一构图」,"
                "现在改成要求 3 轴差异(相机/光线/动态元素)至少命中 2 轴。",
                "_tmpl_end_empty", DEFAULT_END_EMPTY_TMPL)
        add_tab("👤 尾帧·人物 ⚠️病根",
                "⚠️ 人物镜头尾帧也不能锁死「同一角度」— 现在允许相机运动 + 动作变化。",
                "_tmpl_end_people", DEFAULT_END_PEOPLE_TMPL)

        def save():
            for attr, (txt, _) in widgets.items():
                setattr(self, attr, txt.get("1.0", "end").rstrip())
            self._save_config()
            self._log("✅ 4 个首尾帧模板已保存")
            messagebox.showinfo("已保存",
                                "4 个模板已保存到 config.json,下次启动自动加载。\n\n"
                                "下次批量 / 单独 GPT 生图时会自动使用新模板。",
                                parent=dlg)

        def restore_current():
            """只恢复当前 tab"""
            cur_idx = nb.index(nb.select())
            attr = list(widgets.keys())[cur_idx]
            txt, default = widgets[attr]
            if messagebox.askyesno("确认",
                                   f"恢复当前 tab 模板为默认值?当前内容会丢失。",
                                   parent=dlg):
                txt.delete("1.0", "end")
                txt.insert("1.0", default)

        def restore_all():
            if messagebox.askyesno("确认",
                                   "4 个模板全部恢复默认值?所有当前改动会丢失。",
                                   parent=dlg):
                for attr, (txt, default) in widgets.items():
                    txt.delete("1.0", "end")
                    txt.insert("1.0", default)

        bar = ttk.Frame(dlg)
        bar.pack(fill="x", padx=8, pady=8)
        ttk.Button(bar, text="💾 保存", command=save).pack(side="left", padx=4)
        ttk.Button(bar, text="↺ 当前 tab 恢复默认",
                   command=restore_current).pack(side="left", padx=4)
        ttk.Button(bar, text="↺ 全部恢复默认",
                   command=restore_all).pack(side="left", padx=4)
        ttk.Button(bar, text="取消", command=dlg.destroy).pack(side="right", padx=4)

    def _show_gpt_preset_dialog(self):
        """GPT 提示词库独立窗口 — 不需要启动浏览器也能用"""
        dlg = tk.Toplevel(self.root)
        dlg.title("📝 GPT 提示词库 — 常用提示词管理")
        dlg.geometry("840x620")
        dlg.transient(self.root)

        ttk.Label(dlg,
                  text="📝 常用 GPT 提示词。双击复制到剪贴板,或点按钮直接发到 GPT。",
                  foreground="#2277aa", font=("Microsoft YaHei", 10)).pack(fill="x", padx=8, pady=(8, 0))

        # 左右分栏
        main_pane = ttk.PanedWindow(dlg, orient="horizontal")
        main_pane.pack(fill="both", expand=True, padx=8, pady=4)

        # 左:列表
        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)

        gpt_list = tk.Listbox(left_frame, font=("Microsoft YaHei", 10))
        gpt_list.pack(fill="both", expand=True, pady=2)

        # 右:正文预览
        right_frame = ttk.LabelFrame(main_pane, text="正文预览(可编辑)", padding=4)
        main_pane.add(right_frame, weight=2)

        preview_box = scrolledtext.ScrolledText(right_frame, wrap="word",
                                                font=("Microsoft YaHei", 10))
        preview_box.pack(fill="both", expand=True)

        # 加载列表
        current_idx = [None]
        def load():
            gpt_list.delete(0, "end")
            for p in self._prompt_presets:
                preview = p.get("title", "") + " — " + p.get("text", "")[:40]
                gpt_list.insert("end", preview)
        load()
        self._load_presets_cb = load

        def on_select(_event=None):
            sel = gpt_list.curselection()
            if not sel:
                return
            idx = sel[0]
            current_idx[0] = idx
            p = self._prompt_presets[idx]
            preview_box.delete("1.0", "end")
            preview_box.insert("1.0", p.get("text", ""))
        gpt_list.bind("<<ListboxSelect>>", on_select)

        def save_edit():
            """把右侧编辑框的内容保存回当前选中的提示词"""
            if current_idx[0] is None:
                messagebox.showinfo("提示", "请先点左侧选中一条", parent=dlg)
                return
            txt = preview_box.get("1.0", "end").strip()
            if not txt:
                return
            self._prompt_presets[current_idx[0]]["text"] = txt
            self._save_presets(self._prompt_presets_file, self._prompt_presets)
            load()
            messagebox.showinfo("已保存", "正文已更新", parent=dlg)

        def copy_to_clipboard():
            txt = preview_box.get("1.0", "end").strip()
            if not txt:
                return
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            self._log(f"📋 已复制提示词到剪贴板 ({len(txt)} 字)")

        def send_to_gpt():
            """发送到 GPT 网页(需要先启动)"""
            txt = preview_box.get("1.0", "end").strip()
            if not txt:
                return
            if not self.gpt_ctrl or not self.gpt_ctrl.is_alive():
                if messagebox.askyesno("GPT 未启动",
                    "GPT 网页未启动,是否现在启动?\n\n"
                    "(或者点「📋 复制」,然后自己粘贴到 GPT)", parent=dlg):
                    self._open_gpt_web()
                return
            # 打开 GPT 面板并把文本塞进去
            self._show_gpt_panel()
            # 等面板起来后,把当前提示词写到输入框
            # 这里简化:提示用户自己粘贴,避免 GPT 面板尚未初始化的竞态
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            messagebox.showinfo("提示",
                "✅ 提示词已复制到剪贴板。\n\n"
                "GPT 面板已打开,在输入框里 Ctrl+V 粘贴即可。\n"
                "(如果想启用「自动上传匹配素材」,请在 GPT 面板内操作)",
                parent=dlg)

        def add_new():
            self._preset_dialog(self._prompt_presets, self._prompt_presets_file, gpt_list)

        def del_selected():
            sel = gpt_list.curselection()
            if not sel:
                return
            if not messagebox.askyesno("确认", "删除选中的提示词?", parent=dlg):
                return
            for i in sorted(sel, reverse=True):
                del self._prompt_presets[i]
            self._save_presets(self._prompt_presets_file, self._prompt_presets)
            load()
            preview_box.delete("1.0", "end")
            current_idx[0] = None

        def edit_selected():
            sel = gpt_list.curselection()
            if not sel:
                messagebox.showinfo("提示", "请先选中一条", parent=dlg)
                return
            self._preset_dialog(self._prompt_presets, self._prompt_presets_file,
                                gpt_list, edit_idx=sel[0])

        def import_txt():
            """从 txt 文件批量导入,每行一条"""
            p = filedialog.askopenfilename(
                title="导入提示词(支持 .txt 每行一条 / .json 完整格式)",
                filetypes=[("文本/JSON", "*.txt *.json *.md"), ("所有", "*.*")],
                parent=dlg)
            if not p:
                return
            try:
                suffix = Path(p).suffix.lower()
                if suffix == ".json":
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if not isinstance(data, list):
                        raise ValueError("JSON 不是数组格式")
                    added = 0
                    for item in data:
                        if isinstance(item, dict) and item.get("text"):
                            self._prompt_presets.append({
                                "title": item.get("title", item["text"][:20]),
                                "text": item["text"],
                            })
                            added += 1
                else:
                    # txt / md:按空行切分段落,每段一条
                    with open(p, "r", encoding="utf-8") as f:
                        content = f.read()
                    # 先按两个换行切段
                    blocks = [b.strip() for b in content.split("\n\n") if b.strip()]
                    added = 0
                    for b in blocks:
                        # 第一行当标题
                        lines = b.split("\n", 1)
                        title = lines[0][:30]
                        text = b if len(lines) == 1 else lines[1]
                        self._prompt_presets.append({"title": title, "text": text})
                        added += 1
                self._save_presets(self._prompt_presets_file, self._prompt_presets)
                load()
                messagebox.showinfo("成功", f"✅ 导入 {added} 条提示词", parent=dlg)
            except Exception as e:
                messagebox.showerror("导入失败", str(e), parent=dlg)

        def export_json():
            p = filedialog.asksaveasfilename(
                title="导出为 JSON",
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
                parent=dlg)
            if not p:
                return
            try:
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(self._prompt_presets, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"✅ 已导出到 {p}", parent=dlg)
            except Exception as e:
                messagebox.showerror("导出失败", str(e), parent=dlg)

        # 左下:列表操作按钮
        left_btn = ttk.Frame(left_frame)
        left_btn.pack(fill="x", pady=(4, 0))
        ttk.Button(left_btn, text="➕", width=3, command=add_new).pack(side="left", padx=1)
        ttk.Button(left_btn, text="✏️", width=3, command=edit_selected).pack(side="left", padx=1)
        ttk.Button(left_btn, text="❌", width=3, command=del_selected).pack(side="left", padx=1)
        ttk.Button(left_btn, text="📥 导入",
                   command=import_txt).pack(side="left", padx=2)
        ttk.Button(left_btn, text="📤 导出",
                   command=export_json).pack(side="left", padx=2)

        # 底部:操作按钮
        bottom_bar = ttk.Frame(dlg)
        bottom_bar.pack(fill="x", padx=8, pady=8)

        ttk.Button(bottom_bar, text="💾 保存编辑",
                   command=save_edit).pack(side="left", padx=2)
        ttk.Button(bottom_bar, text="📋 复制到剪贴板",
                   command=copy_to_clipboard).pack(side="left", padx=2)
        ttk.Button(bottom_bar, text="🌐 发到 GPT 网页",
                   command=send_to_gpt).pack(side="left", padx=2)
        ttk.Button(bottom_bar, text="📂 打开 JSON 文件",
                   command=lambda: self._open_file(self._prompt_presets_file)).pack(side="left", padx=2)
        ttk.Button(bottom_bar, text="关闭",
                   command=dlg.destroy).pack(side="right", padx=2)

        # 底部统计
        ttk.Label(dlg,
                  text=f"💡 文件位置:{self._prompt_presets_file}  |  "
                       f"双击列表条目:查看/编辑  |  "
                       f"修改后记得点「💾 保存编辑」",
                  foreground="#888", font=("Microsoft YaHei", 9)).pack(fill="x", padx=8, pady=(0, 6))

    def _show_wan22_preset_dialog(self):
        """Wan 2.2 提示词库管理 + 应用到场景"""
        dlg = tk.Toplevel(self.root)
        dlg.title("📖 Wan 2.2 提示词库 — 管理 / 应用到场景")
        dlg.geometry("680x520")
        dlg.transient(self.root)

        ttk.Label(dlg,
                  text="📖 常用 Wan 2.2 动作指令。双击可应用到「选中场景」的 prompt 字段",
                  foreground="#2277aa").pack(fill="x", padx=8, pady=(8, 0))

        wan_list = tk.Listbox(dlg, font=("Microsoft YaHei", 10))
        wan_list.pack(fill="both", expand=True, padx=8, pady=4)

        def load():
            wan_list.delete(0, "end")
            for p in self._wan22_presets:
                preview = p.get("title", "") + " — " + p.get("text", "")
                wan_list.insert("end", preview)
        load()
        self._load_wan22_presets_cb = load

        def apply_to_selected():
            sel = wan_list.curselection()
            if not sel:
                return
            preset = self._wan22_presets[sel[0]]
            # 看场景表有没有选中
            tree_sel = self.tree.selection()
            if not tree_sel:
                messagebox.showinfo("提示", "请先在场景列表里选中要设置提示词的场景",
                                    parent=dlg)
                return
            cnt = 0
            for item in tree_sel:
                idx = int(self.tree.item(item, "values")[0]) - 1
                if 0 <= idx < len(self.scenes):
                    self.scenes[idx]["prompt"] = preset.get("text", "")
                    cnt += 1
            self._refresh_tree()
            messagebox.showinfo("完成",
                f"已把「{preset.get('title','')}」应用到 {cnt} 个场景", parent=dlg)

        wan_list.bind("<Double-1>", lambda e: apply_to_selected())

        btn_bar = ttk.Frame(dlg)
        btn_bar.pack(fill="x", padx=8, pady=8)
        ttk.Button(btn_bar, text="🎯 应用到选中场景",
                   command=apply_to_selected).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="➕ 新增",
                   command=lambda: self._preset_dialog(
                       self._wan22_presets, self._wan22_presets_file, wan_list)).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="✏️ 编辑",
                   command=lambda: self._wan22_edit(wan_list)).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="❌ 删除",
                   command=lambda: self._wan22_delete(wan_list)).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="📂 打开文件",
                   command=lambda: self._open_file(self._wan22_presets_file)).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="关闭", command=dlg.destroy).pack(side="right", padx=2)

    def _wan22_edit(self, listbox):
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先选中一条")
            return
        self._preset_dialog(self._wan22_presets, self._wan22_presets_file, listbox, edit_idx=sel[0])

    def _wan22_delete(self, listbox):
        sel = listbox.curselection()
        if not sel:
            return
        if not messagebox.askyesno("确认", "删除选中的提示词?"):
            return
        for i in sorted(sel, reverse=True):
            del self._wan22_presets[i]
        self._save_presets(self._wan22_presets_file, self._wan22_presets)
        if hasattr(self, "_load_wan22_presets_cb"):
            self._load_wan22_presets_cb()

    def _launch_debug_chrome(self):
        """启动一个带调试端口的 Chrome,用户可以在里面登录,然后本工具 attach 上去"""
        if not HAS_SELENIUM:
            messagebox.showerror("提示", "请先 pip install selenium")
            return
        port = self.gpt_port_var.get() or 9222

        # 先用用户配置的路径;空则自动探测;都找不到才弹浏览框
        chrome = self._get_chrome_path()
        if chrome and not os.path.isfile(chrome):
            messagebox.showerror("路径错误",
                f"配置的 Chrome 路径不存在:\n{chrome}\n\n请重新浏览选择。")
            return
        if not chrome:
            chrome = GPTWebController.find_chrome_exe()
        if not chrome:
            chrome = filedialog.askopenfilename(
                title="找不到 Chrome,请手动指定 chrome.exe 路径",
                filetypes=[("Chrome", "chrome.exe"), ("所有", "*.*")])
            if not chrome:
                return
            # 顺手保存到配置里
            self.gpt_chrome_path_var.set(chrome)

        try:
            profile = str(Path.cwd() / ".gpt_chrome_profile")
            cmd = GPTWebController.launch_debug_chrome(
                port=port, user_data_dir=profile, chrome_path=chrome)
            self._log(f"🚀 已启动调试 Chrome (端口 {port})")
            self._log(f"   命令: {' '.join(cmd)}")
            self.gpt_mode_var.set("attach  (连接已运行 Chrome,最稳)")
            msg = (f"✅ 已启动 Chrome(端口 {port})\n\n"
                   f"浏览器窗口会自己打开。现在请:\n\n"
                   f"1. 在浏览器里打开 {self.gpt_url_var.get()}\n"
                   f"2. 登录你的 GPT 账号(只需一次,cookies 会保存)\n"
                   f"3. 回到本工具点「🌐 打开 GPT」完成连接\n\n"
                   f"⚠️ 注意:这个 Chrome 窗口不要直接叉掉,否则 attach 会断开。")
            messagebox.showinfo("启动成功", msg)
        except Exception as e:
            self._log(f"❌ 启动调试 Chrome 失败: {e}")
            messagebox.showerror("失败", str(e))

    def _show_chrome_help(self):
        """弹出 Chrome 启动失败排查指南"""
        help_text = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "    Chrome 启动失败排查指南\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔥 最常见错误:\n\n"
            "   「session not created: Chrome instance exited」\n\n"
            "📋 原因分析:\n\n"
            "   Chrome 不能同时用同一个 user-data-dir 启动两次。\n"
            "   如果你本来就开着 Chrome,再用 standalone 模式启动就会冲突。\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ 推荐解决方案:attach 模式(最稳)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "步骤:\n"
            "  1. 关闭所有 Chrome 窗口(系统托盘里也要退出)\n"
            "  2. 点工具里「🚀 启动调试 Chrome」按钮\n"
            "     → 会弹出一个新 Chrome 窗口\n"
            "  3. 在这个窗口里打开 GPT 网页并登录\n"
            "  4. 把「模式」下拉选择为 attach\n"
            "  5. 点「🌐 打开 GPT」→ 本工具连上去\n\n"
            "  💡 之后每次用,重复 2~5 步即可(登录状态会保留)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🛠 手动启动调试 Chrome(替代方案)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Windows 命令提示符:\n"
            '  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" \\\n'
            "    --remote-debugging-port=9222 \\\n"
            '    --user-data-dir="C:\\ChromeDebug"\n\n'
            "Mac:\n"
            '  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\\n'
            "    --remote-debugging-port=9222 \\\n"
            '    --user-data-dir="$HOME/ChromeDebug"\n\n'
            "然后在工具里选 attach 模式,点「🌐 打开 GPT」。\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🚨 其它可能的错误\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "• ChromeDriver version mismatch\n"
            "  → pip install -U selenium  (4.6+ 自动管理 driver)\n\n"
            "• 找不到 Chrome\n"
            "  → 装 Chrome:https://www.google.cn/chrome/\n\n"
            "• profile 目录锁定(SingletonLock 文件)\n"
            "  → 删除 .gpt_chrome_profile 文件夹后重试\n\n"
            "• 代理/VPN 干扰\n"
            "  → 临时关闭全局代理"
        )
        dlg = tk.Toplevel(self.root)
        dlg.title("Chrome 启动失败 — 排查指南")
        dlg.geometry("720x640")
        dlg.transient(self.root)
        box = scrolledtext.ScrolledText(dlg, wrap="word",
                                        font=("Microsoft YaHei", 10),
                                        padx=12, pady=8)
        box.insert("1.0", help_text)
        box.configure(state="disabled")
        box.pack(fill="both", expand=True)
        ttk.Button(dlg, text="好的", command=dlg.destroy).pack(pady=8)

    def _open_gpt_web(self):
        if not HAS_SELENIUM:
            messagebox.showerror("缺少依赖",
                "🚫 未安装 selenium,无法控制浏览器。\n\n"
                "请在命令行运行:\n    pip install selenium\n\n"
                "另外需要 Chrome 浏览器已安装。\n"
                "新版 selenium (4.6+) 会自动管理 driver,无需手动下载。")
            return

        if self.gpt_ctrl and self.gpt_ctrl.is_alive():
            self._show_gpt_panel()
            return

        mode = self._get_gpt_mode()

        def _start():
            try:
                self.gpt_ctrl = GPTWebController(
                    url=self.gpt_url_var.get().strip() or DEFAULT_GPT_WEB_URL,
                    log_cb=self._log,
                    mode=mode,
                    debug_port=self.gpt_port_var.get() or 9222,
                    chrome_path=self._get_chrome_path(),
                )
                self.gpt_ctrl.start()
                self.root.after(0, self._show_gpt_panel)
            except Exception as e:
                self.gpt_ctrl = None
                err = str(e)
                self._log(f"❌ 启动 GPT 网页失败: {err[:100]}")
                # 根据错误内容推荐解决方案
                show_help = ("Chrome instance exited" in err or
                             "session not created" in err)
                if show_help:
                    self.root.after(0, lambda: self._ask_retry_with_help(err))
                else:
                    self.root.after(0, lambda: messagebox.showerror("启动失败", err))
        threading.Thread(target=_start, daemon=True).start()

    def _ask_retry_with_help(self, err):
        """启动失败后的引导对话框"""
        dlg = tk.Toplevel(self.root)
        dlg.title("Chrome 启动失败,需要处理一下")
        dlg.geometry("620x400")
        dlg.transient(self.root)

        ttk.Label(dlg, text="⚠️ Chrome 启动失败",
                  font=("Microsoft YaHei", 14, "bold"),
                  foreground="#cc3333").pack(pady=10)

        info = ttk.Label(dlg,
            text="最大可能是 Chrome 已经在运行了 —— 同一个 profile 不能被用两次。\n\n"
                 "请选择一种解决方式:",
            justify="left", font=("Microsoft YaHei", 10))
        info.pack(padx=20, pady=6, anchor="w")

        # 错误详情折叠
        err_box = tk.Text(dlg, height=5, wrap="word", font=("Consolas", 9),
                          foreground="#aa0000")
        err_box.insert("1.0", err[:400])
        err_box.configure(state="disabled")
        err_box.pack(fill="x", padx=20, pady=4)

        btn_frame = ttk.Frame(dlg)
        btn_frame.pack(pady=16)

        def choose_debug():
            dlg.destroy()
            self._launch_debug_chrome()

        def choose_temp():
            dlg.destroy()
            self.gpt_mode_var.set("temp  (临时实例,无登录)")
            self._open_gpt_web()

        ttk.Button(btn_frame,
                   text="✅ 推荐:启动调试 Chrome → attach\n(需要重新登录一次)",
                   command=choose_debug, width=40).grid(row=0, column=0, padx=4, pady=4)
        ttk.Button(btn_frame,
                   text="⚡ 临时 Chrome\n(每次要登录,但不会冲突)",
                   command=choose_temp, width=40).grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(btn_frame, text="❓ 查看详细排查指南",
                   command=lambda: (dlg.destroy(), self._show_chrome_help()),
                   width=40).grid(row=1, column=0, padx=4, pady=4)
        ttk.Button(btn_frame, text="取消",
                   command=dlg.destroy,
                   width=40).grid(row=1, column=1, padx=4, pady=4)

    def _show_gpt_panel(self):
        """GPT 网页控制小面板"""
        if hasattr(self, "_gpt_panel") and self._gpt_panel.winfo_exists():
            self._gpt_panel.lift()
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("🌐 GPT 网页助手")
        dlg.geometry("860x720")
        dlg.transient(self.root)
        self._gpt_panel = dlg

        # ---- 顶部:输入框 + 匹配预览 ----
        input_frame = ttk.LabelFrame(dlg, text="📝 输入内容(发送前会根据文本自动匹配素材库)", padding=4)
        input_frame.pack(fill="both", padx=8, pady=(8, 4))

        prompt_box = scrolledtext.ScrolledText(input_frame, height=6, wrap="word",
                                               font=("Microsoft YaHei", 10))
        prompt_box.pack(fill="both", expand=True, pady=2)

        # 匹配预览栏
        match_frame = ttk.Frame(input_frame)
        match_frame.pack(fill="x", pady=(4, 0))
        ttk.Label(match_frame, text="🎯 匹配素材:",
                  font=("Microsoft YaHei", 9, "bold")).pack(side="left")
        match_label = ttk.Label(match_frame, text="(输入内容后点「🔍 匹配」)",
                                foreground="#888", font=("Microsoft YaHei", 9))
        match_label.pack(side="left", padx=6)

        # 存放当前匹配到的路径(用户可以手动增删)
        self._gpt_panel_matched = []  # [(keyword, path)]

        def do_match(show_msg=True):
            text = prompt_box.get("1.0", "end").strip()
            if not text:
                match_label.config(text="(输入框为空)", foreground="#888")
                self._gpt_panel_matched = []
                return
            # 自动扫一次(如果没扫过)
            if not self.asset_lib._index:
                d = self.asset_dir_var.get().strip()
                if d and Path(d).exists():
                    self.asset_lib.set_root(d)
            found = self.asset_lib.match(text)
            self._gpt_panel_matched = found
            if found:
                names = ", ".join(k for k, _ in found)
                match_label.config(
                    text=f"✅ {len(found)} 张:{names}",
                    foreground="#228822")
            else:
                match_label.config(text="❌ 未匹配到任何素材",
                                   foreground="#aa4444")
            if show_msg and not found and self.asset_lib._index:
                msg = "没有匹配到。可能:\n" + \
                      "• 素材库里没有对应文件\n" + \
                      "• 文件名对不上(建议在「📁 素材库」里看看)\n" + \
                      "• 需要配别名(如「渊哥」→「林默」)"
                messagebox.showinfo("匹配结果", msg, parent=dlg)

        def add_manual_image():
            """手动追加一张图到待上传列表"""
            ps = filedialog.askopenfilenames(
                title="选择要上传的图片",
                filetypes=[("图片", "*.png *.jpg *.jpeg *.webp *.bmp"), ("所有", "*.*")],
                parent=dlg)
            for p in ps:
                self._gpt_panel_matched.append(("手动", p))
            if ps:
                cur = match_label.cget("text")
                cnt = len(self._gpt_panel_matched)
                names = ", ".join(Path(p).name for _, p in self._gpt_panel_matched[-len(ps):])
                match_label.config(text=f"📎 {cnt} 张 (新增: {names})",
                                   foreground="#228822")

        def clear_matched():
            self._gpt_panel_matched = []
            match_label.config(text="(已清空)", foreground="#888")

        # 输入框变化时自动刷新匹配
        def _on_prompt_change(*_):
            if self.auto_upload_var.get():
                do_match(show_msg=False)
        prompt_box.bind("<KeyRelease>", _on_prompt_change)

        mbar = ttk.Frame(input_frame)
        mbar.pack(fill="x", pady=(4, 0))
        ttk.Button(mbar, text="🔍 匹配素材库", command=do_match).pack(side="left", padx=2)
        ttk.Button(mbar, text="➕ 手动加图", command=add_manual_image).pack(side="left", padx=2)
        ttk.Button(mbar, text="🗑 清空已选", command=clear_matched).pack(side="left", padx=2)

        auto_up_cb = ttk.Checkbutton(
            mbar, text="发送时自动上传匹配到的图",
            variable=self.auto_upload_var)
        auto_up_cb.pack(side="left", padx=(12, 2))

        # ---- 中部:手动提示词库 ----
        lib_frame = ttk.LabelFrame(dlg, text="📚 常用提示词(双击插入到输入框)", padding=4)
        lib_frame.pack(fill="x", padx=8, pady=4)

        lib_inner = ttk.Frame(lib_frame)
        lib_inner.pack(fill="x")

        # 列表 + 按钮
        lib_list = tk.Listbox(lib_inner, height=4, font=("Microsoft YaHei", 9))
        lib_list.pack(side="left", fill="x", expand=True, padx=(0, 4))

        lib_btn_bar = ttk.Frame(lib_inner)
        lib_btn_bar.pack(side="right", fill="y")
        ttk.Button(lib_btn_bar, text="➕", width=3,
                   command=lambda: self._add_prompt_preset(lib_list)).pack(pady=1)
        ttk.Button(lib_btn_bar, text="✏️", width=3,
                   command=lambda: self._edit_prompt_preset(lib_list)).pack(pady=1)
        ttk.Button(lib_btn_bar, text="❌", width=3,
                   command=lambda: self._del_prompt_preset(lib_list)).pack(pady=1)
        ttk.Button(lib_btn_bar, text="📂", width=3,
                   command=self._load_prompt_presets_file).pack(pady=1)

        def load_presets():
            lib_list.delete(0, "end")
            for p in self._prompt_presets:
                preview = p.get("title", "") + " — " + p.get("text", "")[:50]
                lib_list.insert("end", preview)
        load_presets()
        self._load_presets_cb = load_presets  # 外部刷新用

        def use_preset(_event=None):
            sel = lib_list.curselection()
            if not sel:
                return
            p = self._prompt_presets[sel[0]]
            mode = messagebox.askyesnocancel(
                "插入方式",
                f"提示词:{p.get('title','')}\n\n"
                f"「是」= 替换输入框   「否」= 追加到末尾   「取消」= 不操作",
                parent=dlg)
            if mode is None:
                return
            if mode:
                prompt_box.delete("1.0", "end")
                prompt_box.insert("1.0", p.get("text", ""))
            else:
                prompt_box.insert("end", "\n" + p.get("text", ""))
            if self.auto_upload_var.get():
                do_match(show_msg=False)
        lib_list.bind("<Double-1>", use_preset)

        # ---- 回复区 ----
        reply_frame = ttk.LabelFrame(dlg, text="💬 GPT 最新回复", padding=4)
        reply_frame.pack(fill="both", expand=True, padx=8, pady=4)
        reply_box = scrolledtext.ScrolledText(reply_frame, height=10, wrap="word",
                                              font=("Microsoft YaHei", 10))
        reply_box.pack(fill="both", expand=True)

        status_var = tk.StringVar(value="准备就绪")
        ttk.Label(dlg, textvariable=status_var, foreground="#2277aa").pack(fill="x", padx=8)

        btn_bar = ttk.Frame(dlg)
        btn_bar.pack(fill="x", padx=8, pady=8)

        def do_upload_only():
            """只上传,不发送"""
            if not self._gpt_panel_matched:
                # 尝试先匹配
                do_match(show_msg=False)
            if not self._gpt_panel_matched:
                messagebox.showinfo("提示",
                    "没有可上传的图。请:\n"
                    "• 输入文本后点「🔍 匹配素材库」\n"
                    "• 或点「➕ 手动加图」", parent=dlg)
                return
            paths = [p for _, p in self._gpt_panel_matched]
            status_var.set(f"📎 上传 {len(paths)} 张图中...")
            for b in (send_btn, upload_btn, read_btn, img_btn):
                b.config(state="disabled")

            def _worker():
                try:
                    self.gpt_ctrl.upload_files(paths)
                    self.root.after(0, lambda: status_var.set(
                        f"✅ 已上传 {len(paths)} 张图,可以继续输入后发送"))
                except Exception as e:
                    err = str(e)
                    self.root.after(0, lambda: status_var.set(f"❌ 上传失败: {err[:80]}"))
                    self.root.after(0, lambda: messagebox.showerror("上传失败", err, parent=dlg))
                finally:
                    self.root.after(0, lambda: [
                        b.config(state="normal") for b in (send_btn, upload_btn, read_btn, img_btn)
                    ])
            threading.Thread(target=_worker, daemon=True).start()

        def do_send():
            if not self.gpt_ctrl or not self.gpt_ctrl.is_alive():
                messagebox.showerror("错误", "浏览器未运行,请重新打开 GPT", parent=dlg)
                return
            text = prompt_box.get("1.0", "end").strip()
            if not text:
                return

            # 自动上传匹配图
            upload_paths = []
            if self.auto_upload_var.get():
                # 如果还没匹配过就即时匹配
                if not self._gpt_panel_matched:
                    do_match(show_msg=False)
                upload_paths = [p for _, p in self._gpt_panel_matched]

            status_var.set("📤 准备发送...")
            for b in (send_btn, upload_btn, read_btn, img_btn):
                b.config(state="disabled")

            def _worker():
                try:
                    # 先上传(如果有)
                    if upload_paths:
                        self.root.after(0, lambda: status_var.set(
                            f"📎 上传 {len(upload_paths)} 张参考图..."))
                        self.gpt_ctrl.upload_files(upload_paths)
                        time.sleep(1.5)  # 给网页一点时间处理
                    self.root.after(0, lambda: status_var.set("📤 发送文本并等待回复..."))
                    r = self.gpt_ctrl.send(text, wait_reply=True, timeout=300)
                    self.root.after(0, lambda: (
                        reply_box.delete("1.0", "end"),
                        reply_box.insert("1.0", r or ""),
                        status_var.set(f"✅ 已收到回复({len(r or '')} 字)"),
                    ))
                    # 清空已匹配(发完就重置)
                    self._gpt_panel_matched = []
                    self.root.after(0, lambda: match_label.config(
                        text="(发送完成,列表已重置)", foreground="#888"))
                except Exception as e:
                    err = str(e)
                    self.root.after(0, lambda: status_var.set(f"❌ {err[:80]}"))
                finally:
                    self.root.after(0, lambda: [
                        b.config(state="normal") for b in (send_btn, upload_btn, read_btn, img_btn)
                    ])
            threading.Thread(target=_worker, daemon=True).start()

        def do_read():
            if not self.gpt_ctrl or not self.gpt_ctrl.is_alive():
                return
            txt = self.gpt_ctrl.get_last_reply()
            reply_box.delete("1.0", "end")
            reply_box.insert("1.0", txt or "(无回复)")
            status_var.set(f"📥 已读取({len(txt or '')} 字)")

        def do_download_images():
            if not self.gpt_ctrl or not self.gpt_ctrl.is_alive():
                return
            save_dir = Path(self.output_var.get()).parent / "gpt_images"
            files = self.gpt_ctrl.download_last_images(str(save_dir))
            if files:
                status_var.set(f"🖼 已下载 {len(files)} 张图到 {save_dir}")
                self._log(f"🖼 从 GPT 下载 {len(files)} 张图片")
                if messagebox.askyesno("完成",
                    f"已下载 {len(files)} 张图片到:\n{save_dir}\n\n是否打开文件夹?", parent=dlg):
                    self._open_file(str(save_dir))
            else:
                status_var.set("⚠️ 未找到图片")

        def use_as_novel():
            txt = reply_box.get("1.0", "end").strip()
            if not txt:
                messagebox.showinfo("提示", "回复为空", parent=dlg)
                return
            dlg.destroy()
            self._open_novel_dialog()

        send_btn = ttk.Button(btn_bar, text="🚀 一键 上传+发送", command=do_send)
        send_btn.pack(side="left", padx=2)
        upload_btn = ttk.Button(btn_bar, text="📎 只上传", command=do_upload_only)
        upload_btn.pack(side="left", padx=2)
        read_btn = ttk.Button(btn_bar, text="📥 读取回复", command=do_read)
        read_btn.pack(side="left", padx=2)
        img_btn = ttk.Button(btn_bar, text="🖼 下载图片", command=do_download_images)
        img_btn.pack(side="left", padx=2)
        ttk.Button(btn_bar, text="📚 作为小说→改分镜",
                   command=use_as_novel).pack(side="left", padx=2)
        ttk.Button(btn_bar, text="关闭", command=dlg.destroy).pack(side="right", padx=2)

        def on_close():
            dlg.destroy()
        dlg.protocol("WM_DELETE_WINDOW", on_close)

    # ---------- 运行 ----------
    def _test_conn(self):
        try:
            _http_get_json(self.host_var.get(), "/system_stats")
            messagebox.showinfo("成功", f"✅ 已连接 {self.host_var.get()}")
            self._log(f"✅ 连接成功")
        except Exception as e:
            messagebox.showerror("连接失败", f"❌ {e}\n\n请检查 ComfyUI 是否启动")
            self._log(f"❌ 连接失败: {e}")

    def _open_output(self):
        p = Path(self.output_var.get())
        p.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(str(p))
        elif sys.platform == "darwin":
            os.system(f'open "{p}"')
        else:
            os.system(f'xdg-open "{p}"')

    def _start_batch(self):
        # 校验
        if not self.workflow:
            messagebox.showerror("错误", "请先选择并加载工作流 JSON")
            return
        if not self.scenes:
            messagebox.showerror("错误", "任务列表为空")
            return
        if not (self.start_node_var.get() and self.end_node_var.get() and self.prompt_node_var.get()):
            messagebox.showerror("错误", "请先完成节点配置(点「扫描节点」)")
            return
        # 检查每个场景文件
        missing = [s["name"] for s in self.scenes
                   if not Path(s["start"]).exists() or not Path(s["end"]).exists()]
        if missing:
            if not messagebox.askyesno("警告", f"以下场景图片文件缺失:\n{', '.join(missing[:5])}...\n\n仍要继续?"):
                return

        self._save_config()
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.stop_flag.clear()
        self.progress["maximum"] = len(self.scenes)
        self.progress["value"] = 0

        self.worker = threading.Thread(target=self._batch_worker, daemon=True)
        self.worker.start()

    def _stop_batch(self):
        self.stop_flag.set()
        self._log("⏹ 收到停止信号,将在当前任务后停止")

    def _batch_worker(self):
        host = self.host_var.get()
        out_dir = self.output_var.get()
        sn = self.start_node_var.get()
        en = self.end_node_var.get()
        pn = self.prompt_node_var.get()
        pf = self.prompt_field_var.get()

        ok = 0
        total = len(self.scenes)
        for i, s in enumerate(self.scenes):
            if self.stop_flag.is_set():
                self._log("⏹ 已停止")
                break
            self._log(f"\n🎬 [{i+1}/{total}] {s['name']}")
            self._update_status(i, "处理中...")

            try:
                self._log(f"   📤 上传首帧: {Path(s['start']).name}")
                start_name = upload_image(host, s["start"])
                self._log(f"   📤 上传尾帧: {Path(s['end']).name}")
                end_name = upload_image(host, s["end"])

                # 自动注入色板
                final_prompt = s["prompt"]
                cid = s.get("color", "")
                if cid and self.auto_inject_color_var.get():
                    final_prompt = self.color_anchors.inject(final_prompt, cid)
                    self._log(f"   🎨 已注入色板:{self.color_anchors.get_name(cid)}")

                wf = patch_workflow(self.workflow, sn, en, pn, pf,
                                    start_name, end_name, final_prompt,
                                    width=self.width_var.get(),
                                    height=self.height_var.get(),
                                    length=self.length_var.get())
                pid = queue_prompt(host, wf)
                self._log(f"   📮 已排队 prompt_id={pid[:8]}...")

                h = wait_done(host, pid, log_cb=self._log)
                videos = find_output_videos(h)
                if not videos:
                    self._log("   ⚠️ 无视频输出")
                    self._update_status(i, "❌ 无输出")
                    continue

                last_path = None
                for v in videos:
                    ext = Path(v["filename"]).suffix or ".mp4"
                    target_name = f"{s['name']}{ext}"
                    path = download_output(host, v, out_dir, rename_to=target_name)
                    self._log(f"   ✅ 保存: {path}")
                    last_path = str(path)
                if last_path:
                    self.scenes[i]["video_path"] = last_path
                self._update_status(i, "✅ 完成")
                ok += 1
            except Exception as e:
                self._log(f"   ❌ 失败: {e}")
                self._update_status(i, "❌ 失败")

            self.progress["value"] = i + 1
            self.progress_label.config(text=f"{i+1} / {total}")

        self._log(f"\n🎉 完成! 成功 {ok}/{total}")
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self._save_config()

    # ---------- 批量 GPT 生图 ----------
    def _start_batch_gpt_images(self):
        if not self.scenes:
            messagebox.showerror("错误", "任务列表为空")
            return
        if not self.gpt_ctrl or not self.gpt_ctrl.is_alive():
            messagebox.showerror("错误",
                "GPT 网页未挂载,请先点「🌐 打开 GPT」并确保登录。")
            return
        # v0.10:目标保存目录 — 优先用 gpt_save_dir_var 里记忆的路径,填了就不弹窗
        save_dir = self.gpt_save_dir_var.get().strip()
        if save_dir:
            try:
                Path(save_dir).mkdir(parents=True, exist_ok=True)
                self._log(f"📥 使用记忆的 GPT 图保存目录:{save_dir}")
            except Exception as e:
                messagebox.showerror("错误", f"GPT 图保存目录无法创建:\n{save_dir}\n\n{e}")
                return
        else:
            # 留空才弹窗(旧行为兜底)
            default_dir = str(SCRIPT_DIR / "gpt_images")
            save_dir = filedialog.askdirectory(
                title="选择 GPT 图保存目录(填了 AI 助手栏的「📥 GPT 图目录」就不用每次选了)",
                initialdir=default_dir)
            if not save_dir:
                return
            self.gpt_save_dir_var.set(save_dir)
            self._log(f"📥 已记忆 GPT 图保存目录,下次不再弹窗:{save_dir}")
        # 询问是否只处理缺图的场景
        missing_count = sum(1 for s in self.scenes
                            if not s.get("start") or not s.get("end"))
        only_missing = False
        if missing_count > 0 and missing_count < len(self.scenes):
            r = messagebox.askyesnocancel(
                "范围",
                f"当前有 {missing_count} 个场景缺少首帧或尾帧。\n\n"
                f"「是」= 只为这 {missing_count} 个场景画图\n"
                f"「否」= 给全部 {len(self.scenes)} 个场景都画(覆盖现有)\n"
                f"「取消」= 不做")
            if r is None:
                return
            only_missing = r

        self.stop_flag.clear()
        self.gpt_pause_flag.clear()
        self.gpt_batch_running = True
        self._update_gpt_batch_buttons()
        # v0.9: 设置进度条
        self.progress["maximum"] = len(self.scenes)
        self.progress["value"] = 0
        self.progress_label.config(text=f"0 / {len(self.scenes)}")

        self.worker = threading.Thread(
            target=self._batch_gpt_images,
            args=(save_dir, only_missing),
            daemon=True)
        self.worker.start()

    # ----- 常量:人物关键词(v0.8 把它提成类常量,首帧/尾帧模板共用)-----
    _PEOPLE_KEYWORDS = (
        "林默", "林渊", "苏郁", "眼镜反派", "刀疤青年", "妈妈",
        "主角", "渊哥", "男子", "女子", "男人", "女人",
        "青年", "中年", "老人", "少年", "少女",
        "学生", "角色", "柜员", "混混", "打手", "服务员",
        "男孩", "女孩", "女性", "男性",
        "手部", "手指", "拳头", "手握", "手持",
        "侧脸", "侧影", "背影", "人影", "身影", "身躯",
    )

    def _build_start_frame_prompt(self, raw, has_people):
        """v0.10:改为用可配置模板(self._tmpl_start_empty / _tmpl_start_people)。
        两次调用架构的第一次请求 — 只要一张首帧图。
        模板可在 AI 助手栏「⬜ 空镜模板」里编辑。
        """
        tail = self._tmpl_start_people if has_people else self._tmpl_start_empty
        return raw + "\n\n" + tail

    def _build_end_frame_prompt(self, raw, has_people):
        """v0.10:改为用可配置模板(self._tmpl_end_empty / _tmpl_end_people)。
        这里是 PPT 感的病根所在 — 新模板要求首尾帧必须有明确差异,
        而不是「同一机位同一构图只有细微变化」。
        模板可在 AI 助手栏「⬜ 空镜模板」里编辑。
        """
        tail = self._tmpl_end_people if has_people else self._tmpl_end_empty
        return raw + "\n\n" + tail

    def _request_single_gpt_image(self, gpt_text, timeout=300, stable_seconds=5):
        """发一次请求 → 等 1 张新图 → 返回新图 URL 列表(可能 >1,由调用者挑)。

        返回 (saved_urls, before_snapshot) 元组:
          - saved_urls: 新增图 URL(至少 1 张,否则返回 [])
          - before_snapshot: 发送前对话区已有的 URL 快照(便于下一次调用对比)
        """
        # 记录发送前基线
        try:
            before_urls = self.gpt_ctrl.get_last_images()
        except Exception:
            before_urls = []
        self._log(f"     📊 发送前对话区已有 {len(before_urls)} 张图")

        # 发送
        self.gpt_ctrl.send(gpt_text, wait_reply=False)
        self._log(f"     ⏳ 等待 GPT 生成...")

        # 等 1 张新图即可(因为我们每次只要 1 张)
        urls = self.gpt_ctrl.wait_for_images(
            min_count=1, timeout=timeout, stable_seconds=stable_seconds,
            before_urls=before_urls)
        # 尽量多拿:如果 GPT 偶尔还是冒出 2 张,保留更多让调用者挑
        try:
            later = self.gpt_ctrl.get_new_images(before_urls)
            if len(later) > len(urls):
                urls = later
        except Exception:
            pass
        return urls, before_urls

    def _batch_gpt_images(self, save_dir, only_missing):
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        # 确保素材库索引已建
        if not self.asset_lib._index:
            d = self.asset_dir_var.get().strip()
            if d and Path(d).exists():
                try:
                    self.asset_lib.set_root(d)
                except Exception:
                    pass

        total = len(self.scenes)
        done = 0
        self._log(f"\n🖼 开始批量 GPT 生图 v0.9 两次调用模式"
                  f"(共 {total} 个场景,目标目录:{save_dir})")

        for i, s in enumerate(self.scenes):
            if self.stop_flag.is_set():
                self._log("⏹ 已停止")
                break
            # v0.9: 暂停检查
            while self.gpt_pause_flag.is_set():
                if self.stop_flag.is_set():
                    break
                time.sleep(0.5)
            if self.stop_flag.is_set():
                self._log("⏹ 已停止")
                break

            if only_missing and s.get("start") and s.get("end"):
                continue

            self._log(f"\n🎨 [{i+1}/{total}] {s['name']}")
            try:
                # ─── 1. 组装基础 prompt ───
                raw = (s.get("gpt_prompt") or "").strip() or (s.get("prompt") or "").strip()
                if not raw:
                    self._log("   ⚠️ 无 prompt,跳过")
                    continue

                # 注入色板前缀
                cid = s.get("color", "")
                if cid and self.auto_inject_color_var.get():
                    raw = self.color_anchors.inject(raw, cid)
                    self._log(f"   🎨 已注入色板:{self.color_anchors.get_name(cid)}")

                has_people = any(kw in raw for kw in self._PEOPLE_KEYWORDS)
                self._log(f"   🧭 prompt 模式:{'人物镜头' if has_people else '纯环境空镜'}")

                # ─── 2. 素材库参考图上传(只在首帧前上传一次,尾帧请求直接复用上下文)───
                matched = self.asset_lib.match(raw) if self.asset_lib._index else []
                ref_paths = [p for _, p in matched]
                if ref_paths and self.auto_upload_var.get():
                    self._log(f"   📎 匹配到 {len(ref_paths)} 张参考图:"
                              f"{', '.join(k for k, _ in matched)}")
                    try:
                        self.gpt_ctrl.upload_files(ref_paths)
                        time.sleep(1.5)
                    except Exception as e:
                        self._log(f"   ⚠️ 参考图上传失败(继续发送):{e}")

                sub = Path(save_dir) / f"{i+1:02d}_{s['name']}"

                # ─── 3. 第一次请求:生成首帧 ───
                self._log(f"   📤 [阶段 1/2] 请求首帧图...")
                start_prompt = self._build_start_frame_prompt(raw, has_people)
                start_urls, _ = self._request_single_gpt_image(
                    start_prompt, timeout=300, stable_seconds=5)
                if not start_urls:
                    self._log("   ❌ 首帧超时未拿到(检查 GPT / 镜像站 DOM)")
                    continue
                self._log(f"   📥 首帧拿到 {len(start_urls)} 张")

                # 下载首帧(取第一张新图)
                start_saved = self.gpt_ctrl.download_last_images(
                    str(sub), urls=start_urls[:1])
                if not start_saved:
                    self._log("   ❌ 首帧图下载失败(检查浏览器 fetch 日志)")
                    continue
                start_path = start_saved[0]
                self._log(f"   ✅ 首帧已保存: {start_path}")

                # ─── 4. 稍等,让 GPT 会话状态稳定 ───
                time.sleep(2)
                if self.stop_flag.is_set():
                    self._log("⏹ 已停止(首帧完成后)")
                    if not only_missing or not s.get("start"):
                        s["start"] = start_path
                    self.scenes[i] = s
                    self.root.after(0, self._refresh_tree)
                    break

                # v0.9: 暂停检查(首帧完成后)
                while self.gpt_pause_flag.is_set():
                    if self.stop_flag.is_set():
                        break
                    time.sleep(0.5)

                # ─── 5. 第二次请求:基于首帧生成尾帧 ───
                self._log(f"   📤 [阶段 2/2] 请求尾帧图(基于首帧延续一帧)...")
                end_prompt = self._build_end_frame_prompt(raw, has_people)
                end_urls, _ = self._request_single_gpt_image(
                    end_prompt, timeout=300, stable_seconds=5)
                if not end_urls:
                    # 尾帧失败不是致命 — 首帧已经成功
                    self._log("   ⚠️ 尾帧超时,回退为用首帧作为尾帧(可手动替换)")
                    end_path = start_path
                else:
                    self._log(f"   📥 尾帧拿到 {len(end_urls)} 张")
                    end_saved = self.gpt_ctrl.download_last_images(
                        str(sub), urls=end_urls[:1])
                    if not end_saved:
                        self._log("   ⚠️ 尾帧下载失败,回退为用首帧作为尾帧")
                        end_path = start_path
                    else:
                        end_path = end_saved[0]
                        self._log(f"   ✅ 尾帧已保存: {end_path}")

                # ─── 6. 回填 start/end ───
                if only_missing:
                    if not s.get("start"):
                        s["start"] = start_path
                    if not s.get("end"):
                        s["end"] = end_path
                else:
                    s["start"] = start_path
                    s["end"] = end_path
                self.scenes[i] = s

                # 刷新 UI
                self.root.after(0, self._refresh_tree)
                done += 1

                # v0.9: 更新进度条
                self.progress["value"] = i + 1
                self.progress_label.config(text=f"{i+1} / {total}")

                # v0.11: 每个场景完成后自动新开 GPT 对话,隔离上下文避免画风漂移
                # 最后一个场景不用新开(省一次点击)
                if self.auto_new_chat_var.get() and i < total - 1:
                    self._log(f"   🔄 [自动] 开新对话(隔离上下文)")
                    try:
                        self.gpt_ctrl.new_chat(wait_ready=True, timeout=10)
                    except Exception as e:
                        self._log(f"   ⚠️ 新开对话失败(继续用旧对话):{e}")

                # 礼貌性间隔,避免被 GPT 限速
                time.sleep(3)

            except Exception as e:
                self._log(f"   ❌ 失败: {e}")

        self._log(f"\n🎉 批量 GPT 生图完成!成功 {done} 个")
        self.gpt_batch_running = False
        self.root.after(0, self._update_gpt_batch_buttons)
        self._save_config()


def main():
    # 如果装了 tkinterdnd2,用它的根窗口以启用原生拖拽
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass
    app = ComfyBatchGUI(root)

    def on_close():
        app._save_config()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)

    # 没装拖拽库时,友好提示一次
    if not HAS_DND:
        def hint():
            app._log("💡 提示:安装 tkinterdnd2 可启用拖拽功能 — pip install tkinterdnd2")
        root.after(500, hint)

    root.mainloop()


if __name__ == "__main__":
    main()
