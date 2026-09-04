# claude-buffett 문서 규칙

이 디렉터리는 `D:\\work\\claude-buffett\\docs\\`에 있는 프로젝트 관련 문서의 기준 위치입니다.

## 문서 작성 규칙

- 요구사항이 부족하거나 모호하면 구현 전에 질문을 모아 확인하고, 답변·근거·가정을 `*-analysis.md`에 기록합니다.
- 확정 설계는 `*-design.md`, 실행 순서는 `*-tasks.md`에 기록합니다.
- `*-tasks.md`의 모든 작업에는 `owner`, `model`, `effort`, `depends_on`, `parallel_group`, `verification`, `status`를 지정합니다.
- 독립 작업은 같은 오케스트레이터의 Codex 서브에이전트로 병렬 실행하고, 공유 파일·스키마를 변경하는 작업은 순차 실행합니다.
- 웹 페이지나 주요 UX/UI 변경은 `docs/ux-concepts/<slug>/concept-01..03`의 서로 다른 콘셉트 샘플을 먼저 제시하고 사용자 선택을 받은 뒤 구현합니다.
- UX/UI 작업에는 `impeccable`과 `design-taste-frontend` 스킬을 적용합니다.
- Vercel은 웹 프리뷰·호스팅 기본값이며, 동적 데이터·인증·스토리지는 Supabase를 우선 검토합니다. 실제 배포는 명시적 요청이 있을 때만 수행합니다.
- 시크릿·토큰·키·`.env` 값은 문서·로그·커밋에 기록하지 않습니다.

이 저장소의 기존 문서 인덱스와 생성 규칙이 있으면 그 규칙을 우선하며, 기존 파일을 덮어쓰지 않습니다.
