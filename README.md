# Personalization Agent

미국 주식 자동매매를 위한 AI 기반 개인화 에이전트입니다. LLM을 활용하여 시장 상황, 뉴스 분석, 사용자 투자 성향을 종합적으로 판단하고 최적의 투자 시나리오를 결정합니다.

## 주요 기능

- **멀티 소스 데이터 통합**: 시장 분석, 뉴스 분석, 사용자 프로필 데이터를 종합 분석
- **LLM 기반 시나리오 결정**: 9개 투자 시나리오 중 최적 전략 자동 선택
- **A2A 프로토콜**: Agent-to-Agent 통신으로 다른 에이전트와 협업
- **MCP 서버 연동**: 사용자 프로필 데이터베이스 접근
- **로컬 LLM 실행**: MLX를 활용한 Apple Silicon 최적화

## 시스템 요구사항

### 필수 요구사항
- **OS**: macOS (Apple Silicon - M1/M2/M3/M4)
- **Python**: 3.12.10
- **메모리**:
  - 최소 8GB RAM
  - 권장 16GB+ RAM

### 지원하는 LLM 모델
- MLX 최적화 모델 (HuggingFace의 `mlx-community` 모델들)
- 예시:
  - `mlx-community/gpt-oss-20b-MXFP4-Q8`
  - `mlx-community/Llama-3.2-3B-Instruct-4bit`
  - `mlx-community/Mistral-7B-Instruct-v0.3-4bit`

> **주의**: MLX는 Apple Silicon 전용입니다. Intel Mac이나 Windows/Linux에서는 작동하지 않습니다.

## 실행 방법

### 기본 실행
```bash
python personalization_agent_mvp.py
```

### 다른 모델 사용하기
코드의 `llm` 초기화 부분을 수정:

```python
# personalization_agent_mvp.py 파일 하단
llm = SimpleLLM(model_name="mlx-community/gpt-oss-20b-MXFP4-Q8")
```

모델명을 원하는 MLX 모델로 변경 후 실행하세요.

## 실행 예시

실행하면 4개의 테스트 케이스가 순차적으로 실행됩니다:

```
[LLM] 모델 로딩 중...
✅ 모델 로드 완료

### 테스트 1: 상승장 + 공격형 사용자 ###
[1] 시장 분석 데이터 수신 중...
[2] 뉴스 분석 데이터 수신 중...
[3] 사용자 프로필 조회 중...
[MCP] 사용자 조회:...

[검증] 입력 데이터 검증 중...
✅ 검증 통과

[프롬프트] 생성 중...

[LLM] 추론 실행 중...
[LLM] 응답 수신 완료 (길이: 247자)

[LLM Raw Response] 'We need to choose scenario. Market analysis: all bull. Risk medium. Liquidity tight_and_rising. News positive. User aggressive. So scenario bull_aggressive. Provide response.<|end|><|start|>assistant<|channel|>final<|message|>시나리오: bull_aggressive'

[파싱] LLM 응답 파싱 중...
[디버그] <|message|> 이후: 시나리오: bull_aggressive
✅ 시나리오 파싱 성공: bull_aggressive
✅ 선택된 모델: gpt-oss-20b-v1

[출력] {
  "scenario": "bull_aggressive",
  "selected_model": "gpt-oss-20b-v1"
}
```

## 코드 구조

```
personalization_agent_mvp.py
├── A2AProtocol              # Agent-to-Agent 통신 시뮬레이터
├── MCPServer                # 사용자 프로필 DB 시뮬레이터
├── SimpleLLM                # MLX 기반 LLM 래퍼
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

## 9개 투자 시나리오

시장 상황(3) × 투자 성향(3) = 9개 시나리오

| 시장 상황 | 공격형 (Aggressive) | 중립형 (Neutral) | 안정형 (Stable) |
|----------|-------------------|-----------------|----------------|
| 상승장 (Bull) | bull_aggressive | bull_neutral | bull_stable |
| 보합장 (Sideways) | sideways_aggressive | sideways_neutral | sideways_stable |
| 하락장 (Bear) | bear_aggressive | bear_neutral | bear_stable |

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

### 3. 사용자 프로필 (MCP)
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

### 모델 매핑 변경
`PersonalizationAgent` 클래스의 `model_mapping` 딕셔너리를 수정:

```python
self.model_mapping = {
    "bull_aggressive": "your_model_id_1",
    "bull_neutral": "your_model_id_2",
    # ...
}
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

## 주의사항

1. **첫 실행 시간**: 모델 다운로드로 인해 첫 실행 시 시간이 오래 걸립니다
2. **메모리 사용량**: 모델 크기에 따라 4GB~12GB RAM 사용
3. **Apple Silicon 전용**: Intel Mac이나 다른 OS에서는 작동하지 않습니다
4. **인터넷 연결**: 모델 다운로드 시 인터넷 필요