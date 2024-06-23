from PIL import Image, ImageDraw, ImageFont
import json
import os


def create_manga(json_file, output_file):
    # JSONファイルを読み込む
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 漫画全体のサイズを設定
    width = 1179
    title_height = 233
    panel_height = 538
    total_height = title_height + panel_height * 4

    # 新しい画像を作成
    manga = Image.new('RGB', (width, total_height), color='white')
    draw = ImageDraw.Draw(manga)

    # タイトルを描画
    title_font = ImageFont.truetype(
        "/System/Library/Fonts/AppleSDGothicNeo.ttc", 40)
    draw.text((width//2, title_height//2),
              data[0]["title"], font=title_font, fill="black", anchor="mm")

    # 各コマを描画
    for i, panel in enumerate(data):
        y_offset = title_height + i * panel_height

        # 背景を描画 (ここでは単色を使用)
        draw.rectangle([0, y_offset, width, y_offset +
                       panel_height], fill="lightgray")

        # キャラクターを配置
        for j, char in enumerate(panel['characters']):
            char_image = Image.open(
                f"characters/{char['character']}_{char['emotion']}.png")
            char_width = width // 4
            char_height = int(
                char_width * char_image.height / char_image.width)
            char_image = char_image.resize((char_width, char_height))

            x_pos = 0 if j == 0 else width - char_width
            y_pos = y_offset + (panel_height - char_height) // 2
            manga.paste(char_image, (x_pos, y_pos), char_image.convert('RGBA'))

        # 吹き出しとセリフを描画
        for char in panel['characters']:
            if char['speech_bubble']:
                bubble_width = width // 2
                bubble_height = panel_height // 3
                bubble_x = width // 4 if char['character'] == 'ch1' else width // 4 * \
                    3 - bubble_width
                bubble_y = y_offset + panel_height // 3

                # 吹き出しの背景
                draw.ellipse([bubble_x, bubble_y, bubble_x + bubble_width,
                             bubble_y + bubble_height], fill="white", outline="black")

                # セリフ
                font = ImageFont.truetype("path/to/font.ttf", 20)
                text_bbox = draw.multiline_textbbox(
                    (0, 0), char['speech_bubble']['text'], font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = bubble_x + (bubble_width - text_width) // 2
                text_y = bubble_y + (bubble_height - text_height) // 2
                draw.multiline_text(
                    (text_x, text_y), char['speech_bubble']['text'], font=font, fill="black")

    # 画像を保存
    manga.save(output_file)


# 使用例
create_manga(
    'manga_scenarios/都知事選同一ポスター多数_選管に苦情１０００件超 制度の隙_識者_規制を_ - 北日本新聞社 web.json', 'output_manga.png')
