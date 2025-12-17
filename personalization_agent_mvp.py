# 개인화 에이전트 MVP - LLM 기반 시나리오 결정

import json
from datetime import datetime
from mlx_lm import load, generate


# ========================================
# 1. A2A 프로토콜 (시뮬레이터)
# ========================================

class A2AProtocol:
    """
    Agent-to-Agent 통신 시뮬레이터
    실제로는 HTTP API, gRPC, 메시지 큐 등으로 구현
    """
    
    def __init__(self):
        # 각 에이전트별 메시지 저장소
        self.messages = {}
    
    def send(self, from_agent, to_agent, data):
        """메시지 전송"""
        if to_agent not in self.messages:
            self.messages[to_agent] = []
        
        message = {
            "from": from_agent,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.messages[to_agent].append(message)
        print(f"[A2A] {from_agent} → {to_agent}")
    
    def receive(self, agent_id):
        """최신 메시지 수신"""
        messages = self.messages.get(agent_id, [])
        if messages:
            return messages[-1]["data"]  # 가장 최근 메시지
        return None


# ========================================
# 2. MCP 서버 (시뮬레이터)
# ========================================

class MCPServer:
    """
    사용자 프로필 DB 접근
    """
    
    def __init__(self):
        # 테스트용 사용자 데이터
        self.users = {
            "user_001": {"risk_tolerance": "aggressive"},
            "user_002": {"risk_tolerance": "neutral"},
            "user_003": {"risk_tolerance": "stable"}
        }
    
    def get_user_profile(self, user_id):
        """사용자 프로필 조회"""
        profile = self.users.get(user_id)
        if profile:
            print(f"[MCP] 사용자 조회: {user_id} - {profile['risk_tolerance']}")
        return profile


# ========================================
# 3. LLM 시뮬레이터 (간단 버전)
# ========================================
'''
class SimpleLLM:
    """
    LLM 시뮬레이터 - 실제로는 ollama, openai 등 사용
    지금은 간단한 규칙 기반으로 시나리오 결정
    """
    
    def generate(self, prompt):
        """
        프롬프트 받아서 시나리오 결정
        실제 LLM 호출 대신 규칙 기반 판단
        """
        print(f"\n[LLM] 프롬프트 수신 (길이: {len(prompt)}자)")
        
        # 프롬프트에서 핵심 정보 추출
        market_state = self._extract_market_state(prompt)
        risk_tolerance = self._extract_risk_tolerance(prompt)
        
        # 시나리오 결정
        scenario = f"{market_state}_{risk_tolerance}"
        
        # LLM 응답 형식으로 반환
        response = f"시나리오: {scenario}"
        print(f"[LLM] 응답: {response}")
        
        return response
    
    def _extract_market_state(self, prompt):
        """프롬프트에서 시장 상태 추출"""
        # 간단한 키워드 기반 판단
        if "bull" in prompt.lower() or "상승" in prompt:
            return "bull"
        elif "bear" in prompt.lower() or "하락" in prompt:
            return "bear"
        else:
            return "sideways"
    
    def _extract_risk_tolerance(self, prompt):
        """프롬프트에서 사용자 성향 추출"""
        if "aggressive" in prompt.lower() or "공격" in prompt:
            return "aggressive"
        elif "stable" in prompt.lower() or "안정" in prompt:
            return "stable"
        else:
            return "neutral"
'''
class SimpleLLM:
    """
    실제 LLM 호출 (MLX 사용 - Apple Silicon 최적화)
    """
    
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """모델 로드 (최초 1회만)"""
        print(f"\n[LLM] 모델 로딩 중... (model: {self.model_name})")
        print("⏳ 첫 실행 시 시간이 걸릴 수 있습니다...")
        
        try:
            self.model, self.tokenizer = load(self.model_name)
            print("✅ 모델 로드 완료")
        except Exception as e:
            print(f"[LLM 로드 에러] {str(e)}")
            print("⚠️ 모델명을 확인하거나 'mlx_lm' 설치를 확인하세요")
            self.model = None
            self.tokenizer = None
    
    def generate(self, prompt):
        """
        프롬프트 받아서 LLM 응답 생성
        
        Args:
            prompt: LLM에게 전달할 프롬프트
        
        Returns:
            str: LLM 응답
        """
        print(f"\n[LLM] 추론 실행 중...")
        
        # 모델 로드 실패 시 기본값
        if self.model is None or self.tokenizer is None:
            print("[LLM 에러] 모델이 로드되지 않음")
            return "시나리오: sideways_neutral"
        
        try:
            # MLX로 생성
            formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

            response = generate(
                self.model,
                self.tokenizer,
                prompt=formatted_prompt,
                max_tokens=150,
                verbose=False
            )
            
            print(f"[LLM] 응답 수신 완료 (길이: {len(response)}자)")
            return response
            
        except Exception as e:
            print(f"[LLM 추론 에러] {str(e)}")
            return "시나리오: sideways_neutral"  # 에러 시 기본값

# ========================================
# 4. 개인화 에이전트 (메인)
# ========================================

class PersonalizationAgent:
    """
    개인화 에이전트 MVP
    LLM을 활용해 시나리오 결정 및 모델 선택
    """
    
    def __init__(self, a2a, mcp, llm):
        self.a2a = a2a  # A2A 프로토콜
        self.mcp = mcp  # MCP 서버
        self.llm = llm  # LLM
        
        # 시나리오 → 모델 매핑 (고정)
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
    
    def process(self, user_id):
        """
        메인 처리 함수
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            dict: {scenario, selected_model}
        """
        print(f"\n{'='*60}")
        print(f"개인화 에이전트 실행 (User: {user_id})")
        print(f"{'='*60}")
        
        try:
            # 1. 입력 데이터 수집
            market_data = self._get_market_data()
            news_data = self._get_news_data()
            user_data = self._get_user_data(user_id)
            
            # 2. 필수 필드 검증
            if not self._validate_inputs(market_data, news_data, user_data):
                return self._fallback_response()
            
            # 3. LLM 프롬프트 생성
            prompt = self._create_prompt(market_data, news_data, user_data)
            
            # 4. LLM 호출
            llm_response = self.llm.generate(prompt)

            # 디버그: LLM의 원문 응답 확인
            print("\n[LLM Raw Response]", repr(llm_response))

            # 5. 시나리오 파싱
            scenario = self._parse_scenario(llm_response)
            
            # 6. 모델 선택
            model = self._select_model(scenario)
            
            # 7. 출력 생성
            output = {
                "scenario": scenario,
                "selected_model": model
            }
            
            print(f"\n[출력] {json.dumps(output, indent=2, ensure_ascii=False)}")
            return output
            
        except Exception as e:
            # 에러 발생 시 기본값 반환
            print(f"[에러] {str(e)}")
            return self._fallback_response()
    
    def _get_market_data(self):
        """시장 분석 에이전트로부터 데이터 수신"""
        print("\n[1] 시장 분석 데이터 수신 중...")
        data = self.a2a.receive("personalization_agent_market")
        return data
    
    def _get_news_data(self):
        """뉴스 분석 에이전트로부터 데이터 수신"""
        print("[2] 뉴스 분석 데이터 수신 중...")
        data = self.a2a.receive("personalization_agent_news")
        return data
    
    def _get_user_data(self, user_id):
        """MCP로 사용자 프로필 조회"""
        print(f"[3] 사용자 프로필 조회 중... (user_id: {user_id})")
        data = self.mcp.get_user_profile(user_id)
        return data
    
    def _validate_inputs(self, market_data, news_data, user_data):
        """
        필수 필드 검증
        
        Returns:
            bool: 검증 통과 여부
        """
        print("\n[검증] 입력 데이터 검증 중...")
        
        # None 체크
        if not market_data or not news_data or not user_data:
            print("⚠️ 필수 데이터 누락")
            return False
        
        # 필수 필드 체크
        required_market = ["short_term", "mid_term", "long_term", "risk_level"]
        required_news = ["news_analysis"]
        required_user = ["risk_tolerance"]
        
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
    
    def _create_prompt(self, market_data, news_data, user_data):
        """
        LLM 프롬프트 생성
        
        Returns:
            str: LLM에게 전달할 프롬프트
        """
        print("\n[프롬프트] 생성 중...")
        
        # 핵심 정보 추출
        short_term = market_data.get("short_term")
        mid_term = market_data.get("mid_term")
        long_term = market_data.get("long_term")
        risk_level = market_data.get("risk_level")
        liquidity = market_data.get("liquidity", "unknown")
        
        sentiment = news_data["news_analysis"].get("sentiment_score", 0)
        impact = news_data["news_analysis"].get("market_impact", 5)
        summary = news_data["news_analysis"].get("summary", "정보 없음")
        
        risk_tolerance = user_data.get("risk_tolerance")
        
        # 프롬프트 작성
        prompt = f"""
                당신은 미국 주식 투자 전략 전문가입니다.
                아래 정보를 종합하여 적절한 투자 시나리오를 결정하세요.

                [시장 분석]
                - 단기 추세: {short_term}
                - 중기 추세: {mid_term}
                - 장기 추세: {long_term}
                - 위험 수준: {risk_level}
                - 유동성: {liquidity}

                [뉴스 분석]
                - 요약: {summary}
                - 감정 점수: {sentiment} (-1.0=부정 ~ +1.0=긍정)
                - 시장 영향: {impact} (1=낮음 ~ 10=높음)

                [사용자 정보]
                - 투자 성향: {risk_tolerance}

                다음 9개 시나리오 중 하나를 선택하세요:
                bull_aggressive, bull_neutral, bull_stable
                sideways_aggressive, sideways_neutral, sideways_stable
                bear_aggressive, bear_neutral, bear_stable

                응답 형식: "시나리오: [선택한_시나리오]"
                """
        
        return prompt
    
    def _parse_scenario(self, llm_response):
        """
        LLM 응답에서 시나리오 추출
        
        Args:
            llm_response: LLM 응답 문자열
        
        Returns:
            str: 시나리오 (예: "bull_aggressive")
        """
        print("\n[파싱] LLM 응답 파싱 중...")

        # <|message|> 이후 부분만 사용
        if "<|message|>" in llm_response:
            llm_response = llm_response.split("<|message|>")[1]
            print(f"[디버그] <|message|> 이후: {llm_response[:100]}")
        
        # "시나리오: bull_aggressive" 형식에서 추출
        if "시나리오:" in llm_response:
            scenario = llm_response.split("시나리오:")[1].strip()
            
            # 9개 시나리오 중 하나인지 확인
            valid_scenarios = [
                "bull_aggressive", "bull_neutral", "bull_stable",
                "sideways_aggressive", "sideways_neutral", "sideways_stable",
                "bear_aggressive", "bear_neutral", "bear_stable"
            ]
            
            if scenario in valid_scenarios:
                print(f"✅ 시나리오 파싱 성공: {scenario}")
                return scenario
        
        # 파싱 실패 시 기본값
        print("⚠️ 시나리오 파싱 실패 - 기본값 사용")
        return "sideways_neutral"
    
    def _select_model(self, scenario):
        """
        시나리오에 해당하는 모델 선택
        
        Args:
            scenario: 시나리오 문자열
        
        Returns:
            str: 모델 ID
        """
        print(f"\n[모델 선택] 시나리오: {scenario}")
        
        model = self.model_mapping.get(scenario, "fallback_model")
        print(f"✅ 선택된 모델: {model}")
        
        return model
    
    def _fallback_response(self):
        """
        에러 발생 시 기본값 반환
        
        Returns:
            dict: 기본 응답
        """
        print("\n[Fallback] 기본값 반환")
        return {
            "scenario": "sideways_neutral",
            "selected_model": "fallback_model"
        }


# ========================================
# 5. 시뮬레이션 에이전트들
# ========================================

class MarketAnalysisAgent:
    """시장 분석 에이전트 (시뮬레이션)"""
    
    def __init__(self, a2a):
        self.a2a = a2a
    
    def send_analysis(self, data):
        """시장 분석 결과 전송"""
        self.a2a.send("market_analysis_agent", "personalization_agent_market", data)


class NewsAnalysisAgent:
    """뉴스 분석 에이전트 (시뮬레이션)"""
    
    def __init__(self, a2a):
        self.a2a = a2a
    
    def send_analysis(self, data):
        """뉴스 분석 결과 전송"""
        self.a2a.send("news_analysis_agent", "personalization_agent_news", data)


# ========================================
# 6. 메인 실행
# ========================================

if __name__ == "__main__":
    print("="*60)
    print("개인화 에이전트 MVP 시작")
    print("="*60)
    
    # 시스템 초기화
    a2a = A2AProtocol()
    mcp = MCPServer()
    llm = SimpleLLM(model_name="mlx-community/gpt-oss-20b-MXFP4-Q8")
    
    # 에이전트 생성
    market_agent = MarketAnalysisAgent(a2a)
    news_agent = NewsAnalysisAgent(a2a)
    personalization_agent = PersonalizationAgent(a2a, mcp, llm)
    
    
    # ========================================
    # 테스트 1: 상승장 + 공격형
    # ========================================
    print("\n\n### 테스트 1: 상승장 + 공격형 사용자 ###\n")
    
    # 시장 분석 데이터 전송
    market_data_1 = {
        "date": "2024-01-29",
        "short_term": "bull",
        "mid_term": "bull",
        "long_term": "bull",
        "risk_level": "medium",
        "risk_score": 2,
        "liquidity": "tight_and_rising",
        "details": {
            "sp500": 4927.93,
            "vix": 13.6
        }
    }
    market_agent.send_analysis(market_data_1)
    
    # 뉴스 분석 데이터 전송
    news_data_1 = {
        "news_analysis": {
            "summary": "AI 기술 호평으로 긍정적 전망",
            "sentiment_score": 0.7,
            "market_impact": 8
        }
    }
    news_agent.send_analysis(news_data_1)
    
    # 개인화 에이전트 실행
    result_1 = personalization_agent.process("user_001")
    
    
    # ========================================
    # 테스트 2: 하락장 + 안정형
    # ========================================
    print("\n\n### 테스트 2: 하락장 + 안정형 사용자 ###\n")
    
    # 시장 분석 데이터 전송
    market_data_2 = {
        "short_term": "bear",
        "mid_term": "bear",
        "long_term": "sideways",
        "risk_level": "high",
        "risk_score": 4,
        "liquidity": "tight_but_easing"
    }
    market_agent.send_analysis(market_data_2)
    
    # 뉴스 분석 데이터 전송
    news_data_2 = {
        "news_analysis": {
            "summary": "공급망 차질 우려 확대",
            "sentiment_score": -0.5,
            "market_impact": 9
        }
    }
    news_agent.send_analysis(news_data_2)
    
    # 개인화 에이전트 실행
    result_2 = personalization_agent.process("user_003")
    
    # ========================================
    # 테스트 3: 하락장 + 안정형 but 좋은 뉴스
    # ========================================
    print("\n\n### 테스트 3: 하락장 + 안정형 사용자 but 좋은 뉴스 ###\n")
    
    # 시장 분석 데이터 전송
    market_data_3 = {
        "short_term": "bear",
        "mid_term": "bear",
        "long_term": "sideways",
        "risk_level": "high",
        "risk_score": 4,
        "liquidity": "tight_but_easing"
    }
    market_agent.send_analysis(market_data_3)
    
    # 뉴스 분석 데이터 전송
    news_data_3 = {
        "news_analysis": {
            "summary": "AI 기술 호평으로 긍정적 전망",
            "sentiment_score": 0.7,
            "market_impact": 8
        }
    }
    news_agent.send_analysis(news_data_3)
    
    # 개인화 에이전트 실행
    result_3 = personalization_agent.process("user_003")
    
    # ========================================
    # 테스트 4: 에러 케이스 (필수 필드 누락)
    # ========================================
    print("\n\n### 테스트 4: 에러 처리 (필수 필드 누락) ###\n")
    
    # 불완전한 데이터 전송
    market_data_4 = {
        "short_term": "bull"
        # mid_term, long_term 누락!
    }
    market_agent.send_analysis(market_data_4)
    
    news_data_4 = {
        "news_analysis": {
            "summary": "테스트"
            # sentiment_score 누락!
        }
    }
    news_agent.send_analysis(news_data_4)
    
    # 개인화 에이전트 실행 (fallback 응답 예상)
    result_4 = personalization_agent.process("user_002")
    
    
    print("\n" + "="*60)
    print("개인화 에이전트 MVP 종료")
    print("="*60)
