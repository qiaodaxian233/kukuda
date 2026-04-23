#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI Wan 2.2 首尾帧批量生成器
================================================================
使用步骤:
  1. 打开 ComfyUI,加载你的工作流 JSON
  2. 菜单:Settings → 勾选 "Enable Dev mode Options"
  3. 点击 "Save (API Format)",得到 workflow_api.json,放在本脚本同目录
  4. 先运行一次 `python comfy_wan22_batch.py --inspect`
     脚本会打印所有可编辑节点的 ID 和类型,
     根据输出把下面 NODE_START_IMAGE / NODE_END_IMAGE / NODE_PROMPT
     填成正确的节点 ID
  5. 编辑 scenes.csv (同目录),格式:
       scene_name,start_image,end_image,prompt
       01_雨夜巷尾,imgs/s01_start.png,imgs/s01_end.png,镜头缓慢推近 雨丝斜飘
  6. 运行 `python comfy_wan22_batch.py`
  7. 视频将保存到 ./videos_output
================================================================
"""

import json
import os
import sys
import csv
import time
import uuid
import shutil
import argparse
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

# ============== 配置区(按需修改)==============
COMFY_HOST       = "127.0.0.1:8188"          # ComfyUI 服务地址
WORKFLOW_API     = "workflow_api.json"        # API 格式工作流 JSON 路径
SCENES_CSV       = "scenes.csv"               # 批量场景配置
OUTPUT_DIR       = "./videos_output"          # 视频下载目录
CLIENT_ID        = str(uuid.uuid4())          # 客户端标识
POLL_INTERVAL    = 3                          # 轮询间隔(秒)
TIMEOUT_SECS     = 3600                       # 单任务最长等待时间

# —— 节点 ID(运行 --inspect 后按实际填入)——
NODE_START_IMAGE = "97"     # 首帧 LoadImage 节点 ID
NODE_END_IMAGE   = "184"    # 尾帧 LoadImage 节点 ID
NODE_PROMPT      = "129"    # 提示词节点 ID
PROMPT_FIELD     = "text"   # 提示词字段名(通常是 text / prompt / positive)
# ================================================


# ---------- 基础 HTTP 工具 ----------
def _http_post(path, data, is_json=True):
    url = f"http://{COMFY_HOST}{path}"
    body = json.dumps(data).encode("utf-8") if is_json else data
    headers = {"Content-Type": "application/json"} if is_json else {}
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def _http_get_json(path):
    url = f"http://{COMFY_HOST}{path}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read())


def _http_get_bytes(path):
    url = f"http://{COMFY_HOST}{path}"
    with urllib.request.urlopen(url, timeout=300) as resp:
        return resp.read()


# ---------- ComfyUI API 封装 ----------
def upload_image(local_path):
    """上传图片到 ComfyUI 的 input 目录,返回 ComfyUI 认识的文件名"""
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
        f"true\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")

    req = urllib.request.Request(
        f"http://{COMFY_HOST}/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
    return result.get("name", filename)


def queue_prompt(workflow_api):
    """提交工作流到 ComfyUI,返回 prompt_id"""
    payload = {"prompt": workflow_api, "client_id": CLIENT_ID}
    r = _http_post("/prompt", payload)
    if "prompt_id" not in r:
        raise RuntimeError(f"提交失败: {r}")
    return r["prompt_id"]


def wait_done(prompt_id):
    """轮询 /history,等待任务完成,返回 history 数据"""
    start = time.time()
    while True:
        if time.time() - start > TIMEOUT_SECS:
            raise TimeoutError(f"任务 {prompt_id} 超时")
        try:
            h = _http_get_json(f"/history/{prompt_id}")
        except urllib.error.HTTPError:
            h = {}
        if prompt_id in h:
            return h[prompt_id]
        time.sleep(POLL_INTERVAL)


def find_output_videos(history):
    """从 history 结果里抠出所有视频文件描述"""
    videos = []
    outputs = history.get("outputs", {})
    for node_id, out in outputs.items():
        for key in ("gifs", "videos", "files", "images"):
            for item in out.get(key, []) or []:
                name = item.get("filename", "")
                if name.lower().endswith((".mp4", ".webm", ".mkv", ".gif", ".mov")):
                    videos.append(item)
    return videos


def download_output(item, save_dir, rename_to=None):
    """根据 history 里的 item 下载视频到本地"""
    q = urllib.parse.urlencode({
        "filename": item["filename"],
        "subfolder": item.get("subfolder", ""),
        "type":      item.get("type", "output"),
    })
    data = _http_get_bytes(f"/view?{q}")
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    target = Path(save_dir) / (rename_to or item["filename"])
    with open(target, "wb") as f:
        f.write(data)
    return target


# ---------- 工作流改写 ----------
def load_workflow():
    p = Path(WORKFLOW_API)
    if not p.exists():
        sys.exit(f"❌ 找不到 {WORKFLOW_API}。请在 ComfyUI 里用 'Save (API Format)' 导出。")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def inspect_workflow():
    """打印所有节点,帮助用户定位节点 ID"""
    wf = load_workflow()
    print("\n========== 可编辑节点清单 ==========")
    for nid, node in wf.items():
        ctype = node.get("class_type", "?")
        inputs = node.get("inputs", {})
        preview = {k: (str(v)[:50] if not isinstance(v, list) else "<link>") for k, v in inputs.items()}
        print(f"\n🔹 节点 ID = {nid}   类型 = {ctype}")
        for k, v in preview.items():
            print(f"     {k}: {v}")
    print("\n========== 建议配置 ==========")
    load_imgs = [(nid, n) for nid, n in wf.items() if n.get("class_type") == "LoadImage"]
    texts    = [(nid, n) for nid, n in wf.items()
                if n.get("class_type") in ("CLIPTextEncode", "ShowText", "Text", "String")
                or "text" in n.get("inputs", {}) or "prompt" in n.get("inputs", {})]
    if load_imgs:
        print(f"LoadImage 节点:{[nid for nid, _ in load_imgs]}")
    if texts:
        print(f"疑似文本/提示词节点:{[nid for nid, _ in texts]}")
    print()


def patch_workflow(wf, start_img_name, end_img_name, prompt_text):
    """修改一份 workflow 副本"""
    wf = json.loads(json.dumps(wf))  # deep copy

    # 首帧
    if NODE_START_IMAGE in wf:
        wf[NODE_START_IMAGE]["inputs"]["image"] = start_img_name
    else:
        sys.exit(f"❌ 未在 workflow 中找到首帧节点 {NODE_START_IMAGE}")

    # 尾帧
    if NODE_END_IMAGE in wf:
        wf[NODE_END_IMAGE]["inputs"]["image"] = end_img_name
    else:
        sys.exit(f"❌ 未在 workflow 中找到尾帧节点 {NODE_END_IMAGE}")

    # 提示词
    if NODE_PROMPT in wf:
        if PROMPT_FIELD not in wf[NODE_PROMPT]["inputs"]:
            keys = list(wf[NODE_PROMPT]["inputs"].keys())
            sys.exit(f"❌ 提示词节点 {NODE_PROMPT} 无字段 '{PROMPT_FIELD}'。可用字段: {keys}")
        wf[NODE_PROMPT]["inputs"][PROMPT_FIELD] = prompt_text
    else:
        sys.exit(f"❌ 未在 workflow 中找到提示词节点 {NODE_PROMPT}")

    return wf


# ---------- 场景读取 ----------
def read_scenes():
    p = Path(SCENES_CSV)
    if not p.exists():
        sample = Path(SCENES_CSV)
        with open(sample, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["scene_name", "start_image", "end_image", "prompt"])
            w.writerow(["01_示例", "imgs/s01_start.png", "imgs/s01_end.png", "镜头推近 雨丝飘落"])
        sys.exit(f"✅ 已生成示例 {SCENES_CSV},请编辑后重新运行。")

    scenes = []
    with open(p, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("scene_name"):
                continue
            scenes.append({
                "name":  row["scene_name"].strip(),
                "start": row["start_image"].strip(),
                "end":   row["end_image"].strip(),
                "prompt": row["prompt"].strip(),
            })
    return scenes


# ---------- 主流程 ----------
def run_one(wf_template, scene, idx, total):
    tag = f"[{idx}/{total}] {scene['name']}"
    print(f"\n🎬 {tag}")
    print(f"   首帧: {scene['start']}")
    print(f"   尾帧: {scene['end']}")
    print(f"   提示: {scene['prompt'][:60]}")

    # 上传图片
    try:
        start_name = upload_image(scene["start"])
        end_name   = upload_image(scene["end"])
    except Exception as e:
        print(f"   ❌ 上传失败: {e}")
        return False

    # 改写工作流
    wf = patch_workflow(wf_template, start_name, end_name, scene["prompt"])

    # 提交
    try:
        pid = queue_prompt(wf)
        print(f"   📤 已提交,prompt_id={pid}")
    except Exception as e:
        print(f"   ❌ 提交失败: {e}")
        return False

    # 等待
    try:
        h = wait_done(pid)
    except Exception as e:
        print(f"   ❌ 等待失败: {e}")
        return False

    # 下载
    videos = find_output_videos(h)
    if not videos:
        print("   ⚠️  未发现视频输出,检查 ComfyUI output 目录")
        return False

    for v in videos:
        ext = Path(v["filename"]).suffix or ".mp4"
        target_name = f"{scene['name']}{ext}"
        try:
            path = download_output(v, OUTPUT_DIR, rename_to=target_name)
            print(f"   ✅ 已保存: {path}")
        except Exception as e:
            print(f"   ❌ 下载失败: {e}")
            return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inspect", action="store_true", help="打印工作流节点清单,帮助定位节点 ID")
    parser.add_argument("--host", default=None, help="覆盖 ComfyUI 地址,例如 127.0.0.1:8188")
    args = parser.parse_args()

    global COMFY_HOST
    if args.host:
        COMFY_HOST = args.host

    if args.inspect:
        inspect_workflow()
        return

    # 健康检查
    try:
        _http_get_json("/system_stats")
    except Exception as e:
        sys.exit(f"❌ 无法连接 ComfyUI ({COMFY_HOST}): {e}")

    wf_template = load_workflow()
    scenes = read_scenes()
    if not scenes:
        sys.exit("❌ scenes.csv 为空")

    print(f"\n📋 共 {len(scenes)} 个任务,开始排队...")
    ok_cnt = 0
    for i, s in enumerate(scenes, 1):
        if run_one(wf_template, s, i, len(scenes)):
            ok_cnt += 1

    print(f"\n🎉 全部完成: 成功 {ok_cnt}/{len(scenes)}  输出目录 → {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
