import os
import json
import asyncio
from typing import TypedDict, Optional, Dict, Any
import httpx
import openai
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

load_dotenv()

# ========================================
# 1. APILLM (OpenAI API 호출 및 비용 추적)
# ========================================
class APILLM:
    """
    OpenAI API 기반 LLM 래퍼
    """
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        
        openai.api_key = self.api_key
        
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        
        self.input_price = 1.75   # 1M 토큰당 가격
        self.output_price = 14.00  # 1M 토큰당 가격
        
        print(f"\n[OpenAI LLM] 모델: {self.model_name}")
        print("✅ API 키 로드 완료")
        
    def generate(self, prompt: str) -> str:
        print(f"\n[OpenAI] API 호출 중...")
        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert in US stock market investment strategies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)
            
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_cost += cost
            
            print(f"[토큰] 입력: {input_tokens:,} / 출력: {output_tokens:,}")
            print(f"[비용] 이번 호출: ${cost:.6f}")
            print(f"[누적] 총 비용: ${self.total_cost:.6f}")
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"[API 호출 에러] {str(e)}")
            return "Scenario: sideways_neutral"
            
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens * self.input_price + output_tokens * self.output_price) / 1_000_000
        
    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"[최종 요약] OpenAI - {self.model_name}")
        print(f"{'='*60}")
        print(f"총 입력 토큰:  {self.total_input_tokens:,}")
        print(f"총 출력 토큰:  {self.total_output_tokens:,}")
        print(f"총 토큰:       {self.total_input_tokens + self.total_output_tokens:,}")
        print(f"총 비용:       ${self.total_cost:.6f}")
        print(f"{'='*60}\n")


# ========================================
# 2. PersonalizationAgent (의사결정 헬퍼)
# ========================================
class PersonalizationAgent:
    """
    개인화 에이전트 클래스 (의사결정 로직 담당)
    """
    def __init__(self, llm: APILLM):
        self.llm = llm
        self.model_mapping = {
            "bull_aggressive": "gpt-oss-20b-v1",
            "bull_neutral": "gpt-oss-20b-v2",
            "bull_stable": "gpt-oss-20b-v3",
            "sideways_aggressive": "gpt-oss-20b-v4",
            "sideways_neutral": "gpt-oss-20b-v5",
            "sideways_stable": "gpt-oss-20b-v6",
            "bear_aggressive": "gpt-oss-20b-v7",
            "bear_neutral": "gpt-oss-20b-v8",
            "bear_stable": "gpt-oss-20b-v9"
        }
        
    def validate_inputs(self, market_data: Dict[str, Any], news_data: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
        print("\n[검증] 입력 데이터 검증 중...")
        if not market_data or not news_data or not user_data:
            print("⚠️ 필수 데이터 누락")
            return False
            
        required_market = ["short_term", "mid_term", "long_term", "risk_level"]
        for field in required_market:
            if field not in market_data:
                print(f"⚠️ 시장 데이터 필드 누락: {field}")
                return False
                
        if "news_analysis" not in news_data:
            print("⚠️ 뉴스 분석 데이터 누락")
            return False
            
        if "sentiment_score" not in news_data["news_analysis"]:
            print("⚠️ sentiment_score 누락")
            return False
            
        if "risk_tolerance" not in user_data:
            print("⚠️ 사용자 성향 누락")
            return False
            
        print("✅ 검증 통과")
        return True

    def create_prompt(self, market_data: Dict[str, Any], news_data: Dict[str, Any], user_data: Dict[str, Any]) -> str:
        print("\n[프롬프트] 생성 중...")
        short_term = market_data.get("short_term")
        mid_term = market_data.get("mid_term")
        long_term = market_data.get("long_term")
        risk_level = market_data.get("risk_level")
        liquidity = market_data.get("liquidity", "unknown")
        
        sentiment = news_data["news_analysis"].get("sentiment_score", 0)
        impact = news_data["news_analysis"].get("market_impact", 5)
        summary = news_data["news_analysis"].get("summary", "No information available")
        
        risk_tolerance = user_data.get("risk_tolerance")
        
        prompt = f"""You are a US stock market investment strategy expert. Based on the information below, determine the most appropriate investment scenario.

[Market Analysis]
- Short-term trend: {short_term}
- Mid-term trend: {mid_term}
- Long-term trend: {long_term}
- Risk level: {risk_level}
- Liquidity: {liquidity}

[News Analysis]
- Summary: {summary}
- Sentiment score: {sentiment} (range: -1.0=negative to +1.0=positive)
- Market impact: {impact} (scale: 1=low to 10=high)

[User Profile]
- Risk tolerance: {risk_tolerance}

Select ONE scenario from the following 9 options:
bull_aggressive, bull_neutral, bull_stable
sideways_aggressive, sideways_neutral, sideways_stable
bear_aggressive, bear_neutral, bear_stable

Response format: "Scenario: [selected_scenario]"
"""
        return prompt

    def parse_scenario(self, llm_response: str) -> str:
        print("\n[파싱] LLM 응답 파싱 중...")
        if "<|message|>" in llm_response:
            llm_response = llm_response.split("<|message|>")[1]
            
        if "Scenario:" in llm_response or "scenario:" in llm_response:
            scenario_text = llm_response.lower()
            scenario = scenario_text.split("scenario:")[1].strip().split()[0].strip()
            
            valid_scenarios = [
                "bull_aggressive", "bull_neutral", "bull_stable",
                "sideways_aggressive", "sideways_neutral", "sideways_stable",
                "bear_aggressive", "bear_neutral", "bear_stable"
            ]
            if scenario in valid_scenarios:
                print(f"✅ 시나리오 파싱 성공: {scenario}")
                return scenario
                
        print("⚠️ 시나리오 파싱 실패 - 기본값 사용")
        return "sideways_neutral"

    def select_model(self, scenario: str) -> str:
        print(f"\n[모델 선택] 시나리오: {scenario}")
        model = self.model_mapping.get(scenario, "fallback_model")
        print(f"✅ 선택된 모델: {model}")
        return model


# ========================================
# 3. LangGraph 워크플로우 정의
# ========================================
class AgentState(TypedDict):
    user_id: str
    market_data: Optional[Dict[str, Any]]
    news_data: Optional[Dict[str, Any]]
    user_profile: Optional[Dict[str, Any]]
    scenario: Optional[str]
    selected_model: Optional[str]

async def market_analysis_node(state: AgentState) -> Dict[str, Any]:
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
    user_id = state.get("user_id", "user_001")
    print(f"[DB Node] 외부 DB API 연동 조회 시작... (user_id: {user_id})")
    base_url = os.getenv("USER_DB_URL", "http://127.0.0.1:8000/api/users")
    url = f"{base_url}/{user_id}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                user_profile = response.json()
                print(f"✅ DB Node 완료 (유저 프로필 조회 성공: {user_profile['risk_tolerance']})")
                return {"user_profile": user_profile}
            else:
                print(f"⚠️ DB API 응답 에러 (HTTP {response.status_code})")
                return {"user_profile": {"risk_tolerance": "neutral"}}
        except Exception as e:
            print(f"⚠️ DB API 연결 실패: {str(e)} (기본값 'neutral'을 설정합니다.)")
            return {"user_profile": {"risk_tolerance": "neutral"}}

async def personalization_decision_node(state: AgentState) -> Dict[str, Any]:
    print("\n[Personalizer Node] 의사결정 엔진 구동...")
    
    market = state.get("market_data")
    news = state.get("news_data")
    user = state.get("user_profile")
    
    llm = APILLM(model_name="gpt-4o-mini")
    agent = PersonalizationAgent(llm=llm)
    
    if not agent.validate_inputs(market, news, user):
        print("⚠️ 입력값 검증 실패. 기본값 반환")
        return {
            "scenario": "sideways_neutral",
            "selected_model": "fallback_model"
        }
        
    prompt = agent.create_prompt(market, news, user)
    llm_response = llm.generate(prompt)
    
    scenario = agent.parse_scenario(llm_response)
    model = agent.select_model(scenario)
    
    # 요약 출력
    llm.print_summary()
    
    print("✅ Personalizer Node 완료")
    return {
        "scenario": scenario,
        "selected_model": model
    }

def build_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("market_agent", market_analysis_node)
    workflow.add_node("news_agent", news_analysis_node)
    workflow.add_node("user_db_agent", user_db_node)
    workflow.add_node("personalization_agent", personalization_decision_node)
    
    workflow.add_edge(START, "market_agent")
    workflow.add_edge(START, "news_agent")
    workflow.add_edge(START, "user_db_agent")
    
    workflow.add_edge("market_agent", "personalization_agent")
    workflow.add_edge("news_agent", "personalization_agent")
    workflow.add_edge("user_db_agent", "personalization_agent")
    
    workflow.add_edge("personalization_agent", END)
    
    return workflow.compile()

async def main():
    print("="*60)
    print("LangGraph 기반 Multi-Agent 개인화 워크플로우 시작")
    print("="*60)
    
    app = build_workflow()
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
        
        final_state = await app.ainvoke(initial_state)
        
        print(f"\n[최종 상태 결과 - {u_id}]")
        print(json.dumps(final_state, indent=2, ensure_ascii=False))
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
