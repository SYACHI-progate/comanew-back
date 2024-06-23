import boto3
import json
from botocore.exceptions import ClientError


def ask_claude(question: str) -> str:
    # Bedrock クライアントを初期化（オレゴンリージョンを指定）
    bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')

    # リクエストボディを作成
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    }

    try:
        # Bedrock を通じて Claude 3 Sonnet に質問を送信
        response = bedrock.invoke_model(
            body=json.dumps(request_body),
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            accept="application/json",
            contentType="application/json"
        )

        # レスポンスを解析
        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text']

        return answer
    except ClientError as e:
        print(f"エラー: {e}")
        return f"エラーが発生しました: {str(e)}"


if __name__ == "__main__":
    question = input("Claude 3 Sonnet に質問してください: ")

    answer = ask_claude(question)
    print("\nClaude 3 Sonnet の回答:")
    print(answer)
