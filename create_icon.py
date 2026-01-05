#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
아이콘 생성 스크립트
간단한 'M' 문자 아이콘을 생성합니다.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_markdown_icon():
    """Markdown 뷰어용 아이콘 생성"""

    # 여러 크기의 아이콘 생성
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        # 새 이미지 생성 (투명 배경)
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 배경 원 그리기 (다크 블루)
        margin = size // 10
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=(30, 30, 46, 255),  # 다크 테마 배경색
            outline=(137, 180, 250, 255),  # 파란색 테두리
            width=max(1, size // 32)
        )

        # 'M' 문자 그리기
        font_size = int(size * 0.6)
        try:
            # 시스템 폰트 사용 시도
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # 기본 폰트 사용
            font = ImageFont.load_default()

        # 텍스트 위치 계산 (중앙 정렬)
        text = "M"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (size - text_width) // 2 - bbox[0]
        y = (size - text_height) // 2 - bbox[1]

        # 텍스트 그리기 (밝은 파란색)
        draw.text((x, y), text, fill=(137, 180, 250, 255), font=font)

        images.append(img)

    # ICO 파일로 저장
    icon_path = os.path.join(os.path.dirname(__file__), 'md_viewer.ico')
    images[0].save(
        icon_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images]
    )

    print(f"[OK] Icon created: {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_markdown_icon()
