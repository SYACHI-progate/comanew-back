import requests
import json
from datetime import date


def get_japan_news():
    # APIキーとエンドポイントURLの設定
    API_KEY = "1bbfb0b431284f2386c3640e0284853c"
    URL = "https://newsapi.org/v2/top-headlines"

    # パラメータの設定
    params = {
        "country": "jp",  # 日本のニュース
        "apiKey": API_KEY,
        "from": date.today().isoformat(),  # 今日の日付
    }

    # リクエストの送信
    response = requests.get(URL, params=params)

    # レスポンスの確認
    if response.status_code == 200:
        news_data = response.json()
        return json.dumps(news_data, ensure_ascii=False, indent=2)
    else:
        error_message = {
            "error": "エラーが発生しました",
            "status_code": response.status_code,
            "message": response.text
        }
        return json.dumps(error_message, ensure_ascii=False, indent=2)


# 関数の実行と結果の出力
print(get_japan_news())
