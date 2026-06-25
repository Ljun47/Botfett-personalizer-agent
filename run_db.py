import uvicorn

# FastAPI 외부 DB 서버 기동 엔트리포인트
if __name__ == "__main__":
    print("[Launcher] FastAPI DB Server 기동 중 (Port 8000)...")
    uvicorn.run("src.api.server_db:app", host="127.0.0.1", port=8000, reload=True)
