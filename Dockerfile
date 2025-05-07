# 베이스 이미지: Python + 필요한 패키지 설치용
FROM python:3.10-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 생성
WORKDIR /app

# 필요 파일 복사
COPY . /app

# 패키지 설치
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Streamlit 설정 (포트 및 config 비활성화)
EXPOSE 8501
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Streamlit 앱 실행
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]