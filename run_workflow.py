import asyncio
import sys

# LangGraph 워크플로우 구동 엔트리포인트
from src.workflows.personalization_workflow import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Launcher] 사용자에 의해 에이전트 워크플로우가 중단되었습니다.")
        sys.exit(0)
