#!/usr/bin/env python3
"""
图片生成模型调用工具
使用Gemini API生成图片
"""

import requests
import json
import sys
import time
import threading

# API配置
API_URL = "https://wcnb.ai/v1beta/models/gemini-3-pro-image-preview:generateContent"
API_KEY = "你的API_KEY（请替换为自己的Key）"
BEARER_TOKEN = ""  # 如果需要，可以在这里填写Bearer token

# 进度动画控制
progress_running = False


def show_progress():
    """显示进度动画"""
    global progress_running
    animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    idx = 0
    start_time = time.time()

    while progress_running:
        elapsed = int(time.time() - start_time)
        sys.stdout.write(f"\r{animation[idx % len(animation)]} 正在生成图片... 已等待 {elapsed} 秒")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)

    sys.stdout.write("\r" + " " * 60 + "\r")  # 清除进度行
    sys.stdout.flush()


def generate_image(prompt, reference_images=None):
    """
    调用API生成图片

    Args:
        prompt: 用户输入的提示词
        reference_images: 参考图片路径列表（可选），用于角色一致性等场景

    Returns:
        响应的JSON数据
    """
    import base64
    import os

    global progress_running

    # 构建完整的URL
    url = f"{API_URL}?key={API_KEY}"

    # 设置请求头
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    # 构建 parts 列表
    parts = []

    # 如果有参考图片，先加入图片部分
    if reference_images:
        for img_path in reference_images:
            if os.path.exists(img_path):
                with open(img_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                # 根据扩展名判断 MIME 类型
                ext = img_path.rsplit('.', 1)[-1].lower()
                mime_map = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'webp': 'image/webp', 'gif': 'image/gif'}
                mime_type = mime_map.get(ext, 'image/jpeg')
                parts.append({
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": img_data
                    }
                })
                print(f"  📎 已附加参考图: {os.path.basename(img_path)}")

    # 加入文字提示词
    parts.append({"text": prompt})

    # 构建请求体
    payload = {
        "contents": [
            {
                "parts": parts
            }
        ]
    }

    try:
        # 启动进度动画
        progress_running = True
        progress_thread = threading.Thread(target=show_progress, daemon=True)
        progress_thread.start()

        # 发送POST请求，增加超时时间到180秒
        response = requests.post(url, headers=headers, json=payload, timeout=180)

        # 停止进度动画
        progress_running = False
        progress_thread.join(timeout=1)

        print("✓ 请求完成")

        # 检查响应状态
        response.raise_for_status()

        return response.json()

    except requests.exceptions.Timeout:
        progress_running = False
        print("\n✗ 请求超时（超过180秒），请稍后重试")
        return None
    except requests.exceptions.RequestException as e:
        progress_running = False
        print(f"\n✗ 请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"响应内容: {e.response.text}")
        return None


def extract_and_save_images(response_data, output_dir="."):
    """
    从API响应中提取图片数据并保存

    Args:
        response_data: API返回的JSON数据
        output_dir: 输出目录

    Returns:
        保存的图片文件路径列表
    """
    import base64
    import os
    from datetime import datetime

    saved_files = []

    try:
        if not response_data:
            return saved_files

        # 检查 candidates -> content -> parts -> inlineData
        if 'candidates' in response_data:
            for idx, candidate in enumerate(response_data['candidates']):
                if 'content' in candidate:
                    content = candidate['content']
                    if 'parts' in content:
                        for part_idx, part in enumerate(content['parts']):
                            # 检查是否有内联图片数据
                            if 'inlineData' in part:
                                inline_data = part['inlineData']
                                mime_type = inline_data.get('mimeType', 'image/png')
                                base64_data = inline_data.get('data', '')

                                if base64_data:
                                    # 根据MIME类型确定文件扩展名
                                    ext = mime_type.split('/')[-1]
                                    if ext not in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                                        ext = 'png'

                                    # 生成文件名
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    filename = f"generated_image_{timestamp}_{idx}_{part_idx}.{ext}"
                                    filepath = os.path.join(output_dir, filename)

                                    # 解码并保存图片
                                    image_bytes = base64.b64decode(base64_data)
                                    with open(filepath, 'wb') as f:
                                        f.write(image_bytes)

                                    saved_files.append(filepath)

    except Exception as e:
        print(f"提取和保存图片时出错: {e}")
        import traceback
        traceback.print_exc()

    return saved_files


def main():
    """
    主程序
    用法:
      交互模式:  python3 image_generator.py
      命令行模式: python3 image_generator.py "提示词" [--output-dir 输出目录] [--slide-name 幻灯片名称]
    """
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Gemini 图片生成工具")
    parser.add_argument("prompt", nargs="?", default=None, help="图片生成提示词")
    parser.add_argument("--output-dir", "-o", default=".", help="图片输出目录")
    parser.add_argument("--slide-name", "-s", default=None, help="幻灯片名称（用于文件命名）")
    parser.add_argument("--reference-image", "-r", action="append", default=None,
                        help="参考图片路径（可多次使用以传入多张参考图）")
    args = parser.parse_args()

    print("=" * 50)
    print("图片生成模型调用工具")
    print("模型: gemini-3-pro-image-preview")
    print("=" * 50)
    print()

    try:
        # 命令行参数优先，否则交互式输入
        prompt = args.prompt
        if not prompt:
            prompt = input("请输入图片生成提示词: ").strip()

        if not prompt:
            print("提示词不能为空！")
            sys.exit(1)

        # 确保输出目录存在
        os.makedirs(args.output_dir, exist_ok=True)

        print(f"\n提示词: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        print(f"输出目录: {os.path.abspath(args.output_dir)}")
        if args.reference_image:
            print(f"参考图片: {len(args.reference_image)} 张")
        print("开始生成图片...\n")

        # 调用API生成图片
        response_data = generate_image(prompt, reference_images=args.reference_image)

        if response_data:
            # 提取并保存图片
            saved_files = extract_and_save_images(response_data, output_dir=args.output_dir)

            if saved_files and args.slide_name:
                # 如果指定了幻灯片名称，重命名文件
                renamed_files = []
                for i, filepath in enumerate(saved_files):
                    ext = os.path.splitext(filepath)[1]
                    new_name = f"{args.slide_name}{ext}" if len(saved_files) == 1 else f"{args.slide_name}_{i+1}{ext}"
                    new_path = os.path.join(args.output_dir, new_name)
                    os.rename(filepath, new_path)
                    renamed_files.append(new_path)
                saved_files = renamed_files

            if saved_files:
                print("\n✓ 成功生成图片！")
                print(f"\n已保存 {len(saved_files)} 张图片:")
                for i, filepath in enumerate(saved_files, 1):
                    abs_path = os.path.abspath(filepath)
                    file_size = os.path.getsize(filepath) / 1024  # KB
                    print(f"  {i}. {abs_path} ({file_size:.1f} KB)")
            else:
                print("\n⚠ 未找到图片数据")
                print("提示: 请检查API响应格式")
        else:
            print("\n✗ 图片生成失败")
            sys.exit(1)

    except KeyboardInterrupt:
        global progress_running
        progress_running = False
        print("\n\n程序已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
