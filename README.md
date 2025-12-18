# Personalization Agent

미국 주식 자동매매를 위한 AI 기반 개인화 에이전트입니다. LLM을 활용하여 시장 상황, 뉴스 분석, 사용자 투자 성향을 종합적으로 판단하고 최적의 투자 시나리오를 결정합니다.

## 주요 기능

- **멀티 소스 데이터 통합**: 시장 분석, 뉴스 분석, 사용자 프로필 데이터를 종합 분석
- **LLM 기반 시나리오 결정**: 9개 투자 시나리오 중 최적 전략 자동 선택
- **A2A 프로토콜**: Agent-to-Agent 통신으로 다른 에이전트와 협업
- **유저 DB 조회**: 사용자 프로필 데이터베이스 접근

## 시스템 요구사항

### 필수 요구사항
- **Python**: 3.12.10
- **OpenAI API 키**: [OpenAI Platform](https://platform.openai.com/api-keys)에서 발급

### 지원하는 LLM 모델
- OpenAI GPT 시리즈
  - `gpt-5.2` (현재 사용 중)
  - `gpt-5-mini`
  - `gpt-5.2-pro`

## 설치 방법

### 1. 필요한 패키지 설치
```bash
pip install openai python-dotenv
```

### 2. 환경변수 설정 (API 키)

프로젝트 폴더에 `.env` 파일을 생성하고 OpenAI API 키를 입력하세요:

```bash
# .env 파일 생성
touch .env
```

`.env` 파일 내용:
```
OPENAI_API_KEY=your-actual-openai-api-key-here
```

- `your-actual-openai-api-key-here`를 실제 OpenAI API 키로 교체하세요(필요 시 제공)
- API 키는 [OpenAI Platform](https://platform.openai.com/api-keys)에서 발급받을 수 있습니다

## 실행 방법

### 기본 실행
```bash
python personalization_agent_mvp.py
```

### 실행 시 표시되는 정보
- 입력/출력 토큰 수
- 호출당 비용
- 누적 총 비용

### 다른 OpenAI 모델 사용하기
코드의 `llm` 초기화 부분을 수정:

```python
# personalization_agent_mvp.py 파일 하단
llm = APILLM(model_name="gpt-5.2")  # 또는 다른 OpenAI 모델
```

## 실행 예시

실행하면 4개의 테스트 케이스가 순차적으로 실행됩니다:

```
### 테스트 1: 상승장 + 공격형 사용자 ###

[OpenAI LLM] 모델: gpt-5.2
✅ API 키 로드 완료

[1] 시장 분석 데이터 수신 중...
[2] 뉴스 분석 데이터 수신 중...
[3] 사용자 프로필 조회 중...
✅ 검증 통과

[프롬프트] 생성 중...

[OpenAI] API 호출 중...
[토큰] 입력: 245 / 출력: 18
[비용] 이번 호출: $0.001585
[누적] 총 비용: $0.001585

[LLM Raw Response] '시나리오: bear_stable'

✅ 시나리오 파싱 성공: bull_aggressive
✅ 선택된 모델: gpt-oss-20b-v1

[출력] {
  "scenario": "bull_aggressive",
  "selected_model": "gpt-oss-20b-v1"
}

============================================================
[최종 요약] OpenAI - gpt-5.2
============================================================
총 입력 토큰:  980
총 출력 토큰:  72
총 토큰:       1,052
총 비용:       $0.006340
============================================================
```
### 9개 투자 시나리오

시장 상황(3) × 투자 성향(3) = 9개 시나리오

| 시장 상황 | 공격형 (Aggressive) | 중립형 (Neutral) | 안정형 (Stable) |
|----------|-------------------|-----------------|----------------|
| 상승장 (Bull) | bull_aggressive | bull_neutral | bull_stable |
| 보합장 (Sideways) | sideways_aggressive | sideways_neutral | sideways_stable |
| 하락장 (Bear) | bear_aggressive | bear_neutral | bear_stable |


## 코드 구조

```
personalization_agent_mvp.py
├── A2AProtocol              # Agent-to-Agent 통신 시뮬레이터
├── MCPServer                # 사용자 프로필 DB 시뮬레이터
├── APILLM                   # OpenAI API 기반 LLM 래퍼
│   ├── generate()           # LLM 호출 및 응답 생성
│   ├── _calculate_cost()    # 토큰 기반 비용 계산
│   └── print_summary()      # 최종 비용 요약
├── PersonalizationAgent     # 메인 개인화 에이전트
│   ├── process()            # 메인 실행 함수
│   ├── _get_market_data()   # 시장 데이터 수신
│   ├── _get_news_data()     # 뉴스 데이터 수신
│   ├── _get_user_data()     # 사용자 프로필 조회
│   ├── _validate_inputs()   # 입력 검증
│   ├── _create_prompt()     # LLM 프롬프트 생성
│   ├── _parse_scenario()    # LLM 응답 파싱
│   └── _select_model()      # 시나리오별 모델 매핑
├── MarketAnalysisAgent      # 시장 분석 에이전트 (시뮬레이션)
└── NewsAnalysisAgent        # 뉴스 분석 에이전트 (시뮬레이션)
```

## 입력 데이터 형식

### 1. 시장 분석 데이터 (A2A)
```json
{
  "date": "2024-01-29",
  "short_term": "bull",
  "mid_term": "bull",
  "long_term": "bull",
  "risk_level": "medium",
  "risk_score": 2,
  "liquidity": "tight_and_rising"
}
```

**가능한 값:**
- `short_term`, `mid_term`, `long_term`: `"bull"`, `"bear"`, `"sideways"`
- `risk_level`: `"low"`, `"medium"`, `"high"`, `"panic"`
- `risk_score`: 0-6
- `liquidity`: `"loose"`, `"neutral"`, `"tight_and_rising"`, `"tight_but_easing"`

### 2. 뉴스 분석 데이터 (A2A)
```json
{
  "news_analysis": {
    "summary": "AI 기술 호평으로 긍정적 전망",
    "sentiment_score": 0.7,
    "market_impact": 8
  }
}
```

**가능한 값:**
- `sentiment_score`: -1.0 (매우 부정) ~ +1.0 (매우 긍정)
- `market_impact`: 1 (낮음) ~ 10 (매우 높음)

### 3. 사용자 프로필
```json
{
  "user_id": "user_001",
  "risk_tolerance": "aggressive"
}
```

**가능한 값:**
- `risk_tolerance`: `"aggressive"`, `"neutral"`, `"stable"`

## 출력 데이터 형식

```json
{
  "scenario": "bull_aggressive",
  "selected_model": "gpt-oss-20b-v1"
}
```

## 커스터마이징

### API 키 변경
`.env` 파일에서 API 키를 수정하세요:
```
OPENAI_API_KEY=your-new-api-key
```

### 모델 변경
`PersonalizationAgent` 초기화 부분 수정:
```python
llm = APILLM(model_name="gpt-5.2")  # 다른 OpenAI 모델로 변경
```

### 가격 정보 업데이트
`APILLM` 클래스의 `__init__` 메서드에서 가격 수정:
```python
self.input_price = 5.00   # 입력 토큰당 가격 (USD per 1M tokens)
self.output_price = 20.00  # 출력 토큰당 가격
```

### 프롬프트 수정
`_create_prompt()` 메서드에서 LLM에게 전달할 프롬프트를 커스터마이징할 수 있습니다.

### 사용자 데이터 추가
`MCPServer` 클래스의 `users` 딕셔너리에 사용자를 추가:

```python
self.users = {
    "user_001": {"risk_tolerance": "aggressive"},
    "your_user_id": {"risk_tolerance": "neutral"}
}
```
