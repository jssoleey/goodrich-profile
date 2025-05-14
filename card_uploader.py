import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "goodrichplus"
REPO_NAME = "goodrichplus.github.io"
OG_IMAGE_URL = "https://github.com/goodrichplus/goodrichplus.github.io/blob/main/thumbnail.jpg?raw=true"

def generate_preview_html(session_id: str, redirect_url: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta property="og:title" content="굿리치 전자명함" />
  <meta property="og:description" content="굿리치 상담원의 전자명함을 확인해보세요!" />
  <meta property="og:image" content="{OG_IMAGE_URL}" />
  <meta property="og:url" content="https://{REPO_OWNER}.github.io/{session_id}.html" />
  <meta http-equiv="refresh" content="0.5;url={redirect_url}">
  <title>굿리치 전자명함</title>
</head>
<body>
  <p>명함 페이지로 이동 중입니다...</p>
</body>
</html>
"""

def upload_to_github(session_id: str, redirect_url: str):
    file_path = f"{session_id}.html"
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"

    html_content = generate_preview_html(session_id, redirect_url)
    encoded_content = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 파일 존재 여부 확인
    response = requests.get(api_url, headers=headers)
    is_update = response.status_code == 200

    payload = {
        "message": f"{'update' if is_update else 'create'} preview page for {session_id}",
        "content": encoded_content,
        "branch": "main"
    }

    if is_update:
        payload["sha"] = response.json()["sha"]

    result = requests.put(api_url, headers=headers, json=payload)

    print("📤 요청 주소:", api_url)
    print("📤 응답 코드:", result.status_code)
    print("📤 응답 내용:", result.text)

    if result.status_code in [200, 201]:
        preview_url = f"https://{REPO_OWNER}.github.io/{file_path}"
        return preview_url
    else:
        raise Exception(f"GitHub upload failed: {result.status_code} {result.text}")


# ✅ 예시 실행
if __name__ == "__main__":
    session_id = "84870ad3"
    redirect_url = f"https://goodrich-profile.onrender.com/view?session_id={session_id}"
    upload_to_github(session_id, redirect_url)
