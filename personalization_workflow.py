import os
import json
import asyncio
from typing import TypedDict, Optional, Dict, Any
import httpx
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

# 기존 personalization_agent_gpt.py에서 모듈들을 임포트
from personalization_agent_gpt import APILLM, PersonalizationAgent

load_dotenv()

# ---------------------------------------------------------------------------
# 1. 상태 객체(AgentState) 정의
# ---------------------------------------------------------------------------
class AgentState(TypedDict):
    user_id: str
    market_data: Optional[Dict[str, Any]]
    news_data: Optional[Dict[str, Any]]
    user_profile: Optional[Dict[str, Any]]
    scenario: Optional[str]
    selected_model: Optional[str]

# ---------------------------------------------------------------------------
# 2. 에이전트 노드(Nodes) 구현
# ---------------------------------------------------------------------------
async def market_analysis_node(state: AgentState) -> Dict[str, Any]:
    """시장 분석 데이터를 로드하고 상태에 적재 (JSON 규격 기반)"""
    print("\n[Market Node] 시장 분석 데이터 수집 중...")
    mock_market_data = {
        "date": "2024-01-29",
        "short_term": "bull",
        "mid_term": "bull",
        "long_term": "bull",
        "risk_level": "medium",
        "risk_score": 2,
        "liquidity": "tight_and_rising"
    }
    print("✅ Market Node 완료")
    return {"market_data": mock_market_data}

async def news_analysis_node(state: AgentState) -> Dict[str, Any]:
    """뉴스 분석 데이터를 로드하고 상태에 적재 (JSON 규격 기반)"""
    print("[News Node] 뉴스 분석 데이터 수집 중...")
    mock_news_data = {
        "news_analysis": {
            "summary": "AI 기술 호평으로 긍정적 전망",
            "sentiment_score": 0.7,
            "market_impact": 8
        }
    }
    print("✅ News Node 완료")
    return {"news_data": mock_news_data}

async def user_db_node(state: AgentState) -> Dict[str, Any]:
    """외부 FastAPI 서버(Port: 8000)를 통해 유저 프로필 비동기 조회"""
    user_id = state.get("user_id", "user_001")
    print(f"[DB Node] 외부 DB API 연동 조회 시작... (user_id: {user_id})")
    
    # uvicorn 로컬 호스트 주소
    url = f"http://127.0.0.1:8000/api/users/{user_id}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                user_profile = response.json()
                print(f"✅ DB Node 완료 (유저 프로필 조회 성공: {user_profile['risk_tolerance']})")
                return {"user_profile": user_profile}
            else:
                print(f"⚠️ DB API 응답 에러 (HTTP {response.status_code})")
                return {"user_profile": {"risk_tolerance": "neutral"}}  # Fallback
        except Exception as e:
            print(f"⚠️ DB API 연결 실패: {str(e)} (FastAPI 서버가 꺼져 있거나 연결에 실패하여 기본값 'neutral'을 설정합니다.)")
            return {"user_profile": {"risk_tolerance": "neutral"}}  # Fallback

async def personalization_decision_node(state: AgentState) -> Dict[str, Any]:
    """수집된 모든 데이터를 기반으로 LLM 호출 및 시나리오 결정"""
    print("\n[Personalizer Node] 의사결정 엔진 구동...")
    
    # 1. State(진료 차트)에서 수집된 정보 읽기
    market = state.get("market_data")
    news = state.get("news_data")
    user = state.get("user_profile")
    
    # 2. LLM 및 개인화 에이전트 인스턴스 생성
    # gpt-4o-mini를 기본 모델로 활용
    llm = APILLM(model_name="gpt-4o-mini")
    agent = PersonalizationAgent(a2a=None, mcp=None, llm=llm)
    
    # 3. 의사결정 실행
    prompt = agent._create_prompt(market, news, user)
    llm_response = llm.generate(prompt)
    
    scenario = agent._parse_scenario(llm_response)
    model = agent._select_model(scenario)
    
    print("✅ Personalizer Node 완료")
    return {
        "scenario": scenario,
        "selected_model": model
    }

# ---------------------------------------------------------------------------
# 3. LangGraph 워크플로우 구성 및 컴파일
# ---------------------------------------------------------------------------
def build_workflow():
    workflow = StateGraph(AgentState)
    
    # 노드 등록
    workflow.add_node("market_agent", market_analysis_node)
    workflow.add_node("news_agent", news_analysis_node)
    workflow.add_node("user_db_agent", user_db_node)
    workflow.add_node("personalization_agent", personalization_decision_node)
    
    # 병렬 진입점 설정 (START -> 세 노드로 분기)
    workflow.add_edge(START, "market_agent")
    workflow.add_edge(START, "news_agent")
    workflow.add_edge(START, "user_db_agent")
    
    # 병렬 수집 완료 후 의사결정 노드로 이동
    workflow.add_edge("market_agent", "personalization_agent")
    workflow.add_edge("news_agent", "personalization_agent")
    workflow.add_edge("user_db_agent", "personalization_agent")
    
    # 최종 종료
    workflow.add_edge("personalization_agent", END)
    
    return workflow.compile()

# ---------------------------------------------------------------------------
# 4. 테스트 구동 메인 루프
# ---------------------------------------------------------------------------
async def main():
    print("="*60)
    print("LangGraph 기반 Multi-Agent 개인화 워크플로우 시작")
    print("="*60)
    
    app = build_workflow()
    
    # 테스트 케이스 실행
    test_users = ["user_001", "user_002", "user_003"]
    
    for u_id in test_users:
        initial_state: AgentState = {
            "user_id": u_id,
            "market_data": None,
            "news_data": None,
            "user_profile": None,
            "scenario": None,
            "selected_model": None
        }
        
        # 워크플로우 비동기 실행
        final_state = await app.ainvoke(initial_state)
        
        print(f"\n[최종 상태 결과 - {u_id}]")
        print(json.dumps(final_state, indent=2, ensure_ascii=False))
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
