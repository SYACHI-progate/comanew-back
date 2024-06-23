import boto3
import json
import requests
from datetime import date
import os
from botocore.exceptions import ClientError
from PIL import Image, ImageDraw, ImageFont
import io
import base64


def get_japan_news():
    API_KEY = "1bbfb0b431284f2386c3640e0284853c"
    URL = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "jp",
        "apiKey": API_KEY,
        "from": date.today().isoformat(),
    }
    response = requests.get(URL, params=params)
    if response.status_code == 200:
        news_data = response.json()
        return news_data
    else:
        error_message = {
            "error": "エラーが発生しました",
            "status_code": response.status_code,
            "message": response.text
        }
        return error_message


def ask_claude(prompt: str) -> str:
    bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            },
            {
                "role": "assistant",
                "content": "{"
            }
        ]
    }
    try:
        response = bedrock.invoke_model(
            body=json.dumps(request_body),
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text']
        return "{" + answer
    except ClientError as e:
        print(f"エラー: {e}")
        return f"エラーが発生しました: {str(e)}"


def generate_manga_scenario(news: dict) -> str:
    prompt = f"""
    以下のニュースを読んで、4コマ漫画のシナリオを JSON 形式で作成してください。
    以下の形式に従ってください：

    {{
        "title": "{news['title']}",
        "url": "{news['url']}",
        "thumbnail_url": "{news.get('urlToImage', '')}",
        "panels": [
            {{
                "id": コマ番号,
                "background_prompt": "背景を生成するためのプロンプト",
                "characters": [
                    {{
                        "character": "キャラクター名",
                        "emotion": "キャラの感情",
                        "speech_bubble": {{
                            "text": "セリフ",
                            "shape_type": "talk" または "thought"
                        }}
                    }},
                    {{
                        "character": "キャラクター名",
                        "emotion": "キャラの感情",
                        "speech_bubble": {{
                            "text": "セリフ",
                            "shape_type": "talk" または "thought"
                        }}
                    }}
                ]
            }}
        ]
    }}

    ニュース：
    タイトル: {news['title']}
    概要: {news.get('description', '説明なし')}

    JSON を出力する際に以下の点に注意してください：
    1. この4コマは二人のキャラクターがニュースについて解説して話すものです。
    2. キャラクターの名前は "ch1" と "ch2" を使用してください。
    3. 各コマには2人のキャラクターを含めてください。
    4. キャラクターの感情やセリフは、ニュースの内容に合わせて適切に変化させてください。
    5. セリフがない場合は、speech_bubble を null にしてください。
    6. セリフは日本語で書いてください。
    7. 感情は喜怒哀楽のどれかとします。 
    """

    response = ask_claude(prompt)
    return response


def create_folder_and_save_json(manga_scenario, title, folder_name="manga_scenarios"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    file_name = "".join(
        [c if c.isalnum() or c in [' ', '-', '_'] else '_' for c in title])
    file_name = file_name[:50] + ".json"

    file_path = os.path.join(folder_name, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json.loads(manga_scenario), f, ensure_ascii=False, indent=2)

    print(f"保存されました: {file_path}")
    return file_path


def generate_image(prompt: str) -> Image.Image:
    bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
    request_body = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 10,
        "steps": 50,
        "seed": 42,
    }
    try:
        response = bedrock.invoke_model(
            body=json.dumps(request_body),
            modelId="stability.stable-diffusion-xl-v1",
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response['body'].read())
        image_data = response_body["artifacts"][0]["base64"]
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
        return image
    except ClientError as e:
        print(f"画像生成エラー: {e}")
        return None


def create_manga(json_file, output_folder):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    title = data['title']
    thumbnail_url = data['thumbnail_url']
    panels = data['panels']

    # サムネイル画像のダウンロード
    if thumbnail_url:
        try:
            response = requests.get(thumbnail_url)
            if response.status_code == 200:
                thumbnail = Image.open(io.BytesIO(response.content))
                thumbnail.save(os.path.join(
                    output_folder, f"{title}_thumbnail.png"))
            else:
                print(f"サムネイル画像のダウンロードに失敗しました: {response.status_code}")
        except Exception as e:
            print(f"サムネイル画像の処理中にエラーが発生しました: {e}")

    # 4コマ漫画の生成
    width = 1179
    title_height = 233
    panel_height = 538
    total_height = title_height + panel_height * 4

    manga = Image.new('RGB', (width, total_height), color='white')
    draw = ImageDraw.Draw(manga)

    # タイトルを描画
    title_font = ImageFont.truetype(
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 40)
    draw.text((width//2, title_height//2), title,
              font=title_font, fill="black", anchor="mm")

    for i, panel in enumerate(panels):
        y_offset = title_height + i * panel_height

        # 背景を生成
        background = generate_image(panel['background_prompt'])
        if background:
            background = background.resize((width, panel_height))
            manga.paste(background, (0, y_offset))

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
                font = ImageFont.truetype(
                    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 20)
                text_bbox = draw.multiline_textbbox(
                    (0, 0), char['speech_bubble']['text'], font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = bubble_x + (bubble_width - text_width) // 2
                text_y = bubble_y + (bubble_height - text_height) // 2
                draw.multiline_text(
                    (text_x, text_y), char['speech_bubble']['text'], font=font, fill="black")

    # 4コマ漫画を保存
    manga.save(os.path.join(output_folder, f"{title}_manga.png"))


if __name__ == "__main__":
    news_data = get_japan_news()
    if "articles" in news_data and len(news_data["articles"]) > 0:
        for i, article in enumerate(news_data["articles"]):
            print(f"\n処理中のニュース ({i+1}/{len(news_data['articles'])}):")
            print(f"タイトル: {article['title']}")
            print(f"URL: {article['url']}")
            print(f"画像URL: {article.get('urlToImage', 'なし')}")
            print("\n4コマ漫画のシナリオを生成中...\n")

            manga_scenario = generate_manga_scenario(article)
            print("生成された JSON データ:")
            print(manga_scenario)

            try:
                parsed_json = json.loads(manga_scenario)
                print("JSONの解析に成功しました。")

                # タイトルの取得
                title = parsed_json.get("title", "無題の4コマ漫画")

                json_file_path = create_folder_and_save_json(
                    manga_scenario, title)

                # 4コマ漫画とサムネイルの生成
                output_folder = os.path.dirname(json_file_path)
                create_manga(json_file_path, output_folder)

                print(f"4コマ漫画とサムネイルを生成しました: {output_folder}")

            except json.JSONDecodeError as e:
                print(f"JSONの解析に失敗しました: {e}")
                print("生成されたテキストを確認し、必要に応じて調整してください。")
    else:
        print("ニュースの取得に失敗しました。")
        print(json.dumps(news_data, ensure_ascii=False, indent=2))
