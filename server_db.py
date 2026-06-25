from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI(title="User Profile Database Server")

# 인메모리 유저 DB
USERS_DB = {
    "user_001": {"risk_tolerance": "aggressive"},
    "user_002": {"risk_tolerance": "neutral"},
    "user_003": {"risk_tolerance": "stable"}
}

@app.get("/api/users/{user_id}")
async def get_user_profile(user_id: str):
    if user_id not in USERS_DB:
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"[DB Server] 조회 요청 수신: {user_id} -> {USERS_DB[user_id]}")
    return {
        "user_id": user_id,
        "risk_tolerance": USERS_DB[user_id]["risk_tolerance"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
