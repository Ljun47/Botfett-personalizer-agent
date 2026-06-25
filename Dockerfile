# 1. Base Image 선택 (경량화된 Python 3.10-slim 사용)
FROM python:3.10-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 시스템 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 소스 코드 복사
COPY . .

# 6. 환경 변수 기본값 설정
ENV PORT=8000

# 7. 기본 실행 명령 (docker-compose에서 각 컨테이너 역할에 맞게 오버라이드할 수 있음)
CMD ["python", "run_db.py"]
