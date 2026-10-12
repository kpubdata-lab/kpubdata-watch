# ADR 0015: 화면마다 레이아웃을 정한다 — Overview 는 상태 요약 + Issues First, Datasets 는 평면 목록 + Provider 필터, Detail 은 Timeline 먼저

## 상태

채택됨(Accepted) — 2026-10-12 (#33). 오너 결정(yeongseon, 2026-10-12).

## 요약 (English summary)

> Status Page, Provider Grouped and Issues First are not mutually exclusive, so the
> layout is decided per screen. Overview: a short status summary followed by the
> issues-first sections (the Status Page plus Issues First combination). Datasets:
> keep the shipped flat searchable list and add a Provider filter. Detail: timeline
> first. The prototypes in `ui-lab/` (PR #127) stay as they are, for later
> comparison. Brand v2 is unchanged (ADR 0014); this ADR decides information
> architecture only.

## 문제

#33 은 50~150 Dataset 에서 어떤 레이아웃이 가장 효과적인가를 묻는다. 범위를 좁힌 뒤
(2026-10-03) 세 후보(Status Page, Provider Grouped, Issues First)는 서로 배타적이지 않고,
화면마다 주된 질문이 다르다는 결론이 나왔다.

| 화면 | 주된 질문 |
|---|---|
| Overview | 지금 무엇이 문제인가? |
| Datasets | 어떤 Dataset 을 관측하고 있는가? |
| Detail | 이 Dataset 은 왜 이 상태인가? |

비교 재료는 `ui-lab/status-page/`, `ui-lab/provider-grouped/`, `ui-lab/issues-first/` 와 10 / 50 /
150 Dataset fixture(`ui-lab/fixtures/`)로 마련됐다(PR #127). 선택은 오너의 몫이었고, 오너가 아래와 같이
결정했다.

## 결정

1. **Overview** — 상태 요약(전체 건강 분포) 다음에 문제를 먼저 보여준다: Active Issues, Recent
   Changes, 그 아래 Dataset 별 체크 매트릭스(심각도 순). 즉 Status Page 의 요약과 Issues First 의
   순서를 합친다. 화면 구조(현재 스냅샷 + 체크 매트릭스)는 ADR 0013 그대로다.
2. **Datasets** — 이미 배포된 평평한 검색 목록(`/datasets/`, #102)을 유지하고 **Provider 필터**를 둔다.
   필터는 라벨이 붙은 기본 `select` 라서 키보드와 스크린리더로 쓸 수 있고, 각 선택지에 Provider 의
   Dataset 수를 함께 적어 150개에서도 어디에 몇 개가 있는지 보인다. 그룹으로 묶은 목록은 채택하지 않는다.
3. **Detail** — Timeline 을 먼저 보여준다. 그 Dataset 의 Incident 와 Change 를 한 줄기로 합쳐 최신순으로
   두고, 그 아래에 Current Issue, Health Checks, 최근 30일을 둔다.
4. **UI Lab 프로토타입은 그대로 둔다.** 비교 자료로 남기며 삭제하거나 수정하지 않는다.
5. **시각 정체성은 바꾸지 않는다.** 토큰과 컴포넌트는 Brand v2 만 쓰고
   `scripts/check_brand_tokens.py` 가 계속 검사한다.

## 근거와 한계

- 근거는 오너의 판단과 대형 Status Page 사례 조사(#33 본문)다. 과제별 소요 시간 측정은 하지 않았다.
  측정이 필요해지면 이 ADR 을 대체하는 새 ADR 로 다시 정한다.
- Provider 별로 묶은 목록은 비교 대상이었지만 채택하지 않았다. Provider 는 필터로 접근한다.

## 결과

- Overview: 순서를 10 / 50 / 150 fixture 로 시험한다(`tests/unit/web/test_layout_decision.py`).
- Datasets: Provider 선택지에 개수를 붙이고, 선택지가 모든 행의 Provider 를 덮고 개수의 합이 전체와
  같은지 시험한다.
- Detail: "Recent Incidents" 와 "Recent Changes" 두 패널은 "Timeline" 하나로 합쳐진다.
- `docs/UI.md` 가 이 결정에 맞게 갱신된다.
