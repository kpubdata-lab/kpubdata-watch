# UI

> 이 문서는 KPubData Watch MVP PRD(v1.0 Draft, 2026-09-30)의 §33, §34, §35, §36, §37, §38, §39, §40, §41, §42, §43, §44, §45, §46, §47, §48, §49, §50, §51, §52, §53, §54, §55 를 목적별로 나눈 것이다. 전체 대응표는 [문서 안내](index.md#prd) 에 있다.

## UI Strategy

<small>PRD §33</small>

UI는 MVP 개발과 동시에 **실험 가능하게 유지한다.**

중요한 원칙:

> Backend Domain Model과 UI Layout을 결합하지 않는다.

같은 원칙이 visual identity에도 적용된다([ADR 0012](decisions/0012-brand-v2-visual-identity.md), #68):

> **Visual identity = Fixed. Information architecture = Experimental.**

KPubData Watch는 제품군의 다른 제품(Studio)과 **같은 brand/color/typography/status
표현**을 쓴다. 실험 대상은 색이나 로고가 아니라 Dataset을 어떻게 배치하고 묶어
보여주는가다. 정확한 규칙은 아래 [Visual Identity](#visual-identity) 를 본다.

고정할 것:

```text
Dataset
Observation
Detection
Change
Incident
Health
History

Visual identity (logo · brand color · status color · typography · light/dark theme · accessibility 기준)
```

고정하지 않을 것:

```text
Card vs Table

Provider accordion 여부

Active Issues 위치

30/90 day status bar 형태

Dashboard 형태

Chart 종류
```

## Visual Identity

<small>ADR 0012 (#68)</small>

KPubData Watch의 visual identity는 KPubData Studio Brand v2를 따른다.

Canonical source:

- KPubData Studio [`docs/brand/DESIGN_CONCEPT.md`](https://github.com/yeongseon/kpubdata-studio/blob/main/docs/brand/DESIGN_CONCEPT.md) — 왜 이렇게 디자인하는가
- KPubData Studio [`docs/brand/VISUAL_IDENTITY.md`](https://github.com/yeongseon/kpubdata-studio/blob/main/docs/brand/VISUAL_IDENTITY.md) — 정확히 무엇을 쓰는가 (HEX · token · 크기 · 금지 목록)
- KPubData Studio [`src/globals.css`](https://github.com/yeongseon/kpubdata-studio/blob/main/src/globals.css) — 실제 token 값 (light · dark)

Studio 문서와 이 절이 값으로 다르면 **Studio 가 정본**이다. 이 절은 값을 복제하지
않고 Watch에 필요한 만큼만 옮겨 적는다 — 전체 규칙과 이유는 위 세 문서를 본다.

UI Lab은 information architecture를 실험하지만
logo, palette, typography, status semantics,
light/dark theme 및 accessibility 기준은 실험 대상이 아니다.

### 로고 · lockup

KPubData · Builder · Studio · Watch는 같은 minimal geometric K 심볼 하나를 쓴다
(Studio VISUAL_IDENTITY §2). Lockup은 `KPubData`가 주 wordmark(진하고 크다)이고
`Watch`는 작고 가벼운 중립색 suffix다 — brand color(Blue · Cyan · Mint)를
suffix에 쓰지 않는다. 화면에 제품명은 사이드바/상단 로고 한 번만 쓰고, 그 외
위치(topbar 등)는 현재 위치(breadcrumb)나 페이지 제목을 쓴다.

금지: Watch 전용 eye/radar/pulse 심볼, health 아이콘을 제품 로고로 쓰는 것, 새
gradient 로고, brand color suffix, K geometry 임의 변경.

자산 출처는 `kpubdata-studio/assets/logo/kpubdata-brand-assets/` 다. Watch가
필요한 변형은 `symbol.svg`, `lockup-watch-light.svg`, `lockup-watch-dark.svg`,
`favicon.svg` 이고, 승인된 K geometry에서 suffix 글자만 다르게 만든다 (새 심볼
설계 없음) — 자산 작업은 별도 이슈(`feat(brand): add the KPubData Watch Brand v2
logo and lockup assets`)에서 한다.

### Brand color ≠ status color

Brand color(상호작용 신호)와 status color(Health 신호)는 다른 체계다(Studio
VISUAL_IDENTITY §3.1–§3.2). **Fresh Mint는 Healthy가 아니다** — Fresh Mint ·
Brand Blue · Data Cyan 중 어느 것도 상태를 뜻하지 않는다.

| Brand token | 값 (light) | 역할 | 상태로 쓰지 않는다 |
|---|---|---|---|
| `--brand-primary` (Brand Blue) | `#2563EB` | CTA · 선택된 내비게이션 · 링크 · focus | Healthy 표시 |
| `--data-accent` (Data Cyan) | `#06B6D4` | 차트/데이터 강조 | 상태 표시 전반 |
| `--brand-secondary` (Fresh Mint) | `#14B8A6` | 보조 accent · 작은 디테일 | **success/Healthy** |

### Health → status token 매핑

| Watch Health | status token | light fg | light subtle bg | light border |
|---|---|---|---|---|
| Healthy | `--status-success` | `#15803D` | `#DCFCE7` | `#86EFAC` |
| Degraded | `--status-warning` | `#B45309` | `#FEF3C7` | `#FCD34D` |
| Critical | `--status-failure` | `#B91C1C` | `#FEE2E2` | `#FCA5A5` |
| Unknown | `--status-unknown` | `#52525B` | `#F4F4F5` | `#D4D4D8` |

Dark 값은 Studio `src/globals.css`의 `:root[data-theme="dark"]` 그대로 쓴다 —
Watch가 새로 값을 정하지 않는다:

| Watch Health | status token | dark fg | dark subtle bg | dark border |
|---|---|---|---|---|
| Healthy | `--status-success` | `#4ADE80` | `#052E16` | `#166534` |
| Degraded | `--status-warning` | `#FBBF24` | `#422006` | `#92400E` |
| Critical | `--status-failure` | `#F87171` | `#450A0A` | `#991B1B` |
| Unknown | `--status-unknown` | `#A1A1AA` | `#27272A` | `#3F3F46` |

### Change는 Health와 분리된 축

Change는 Health가 아니다(PRD D-008, ADR 0002). `+ optional_field` 같은 정보성
변경은 Health를 Healthy로 유지한 채 "ⓘ Changed" 로만 표시한다 — success /
warning / failure 색을 쓰지 않는다.

**Open point:** Studio에는 "informational/neutral status" 전용 token
(`--status-info` 등)이 없다(Studio `src/globals.css`, `VISUAL_IDENTITY.md` §3.2
확인 — success/warning/failure/unknown[/stale/partial] 뿐이다). 그래서 Watch는
새 색을 만들지 않고 Studio의 **neutral surface token**(`--foreground` 텍스트,
`--muted` 배경, `--border` 테두리, 보조 텍스트는 `--muted-foreground`)으로
"ⓘ Changed"를 표현한다 — 색이 아니라 "ⓘ" 아이콘과 "Changed" 단어가 의미를 싣는다.
이 매핑은 Studio가 공식 정의한 것이 아니므로, 토큰 foundation 이슈에서 Watch만의
결정으로 명시하고 재검토 대상으로 남긴다.

금지(Studio VISUAL_IDENTITY §3.2와 동일): 모든 schema change를 warning으로
표시, field 추가를 degraded로 표시, 파랑을 healthy로, mint를 healthy로.

### Typography

Studio `VISUAL_IDENTITY.md` §4 그대로:

| 용도 | 값 |
|---|---|
| Page title | 600 20/28 |
| Section title | 600 14/20 |
| Body | 400 14/20 |
| Table | 400 13/18 (숫자 `tabular-nums`, 오른쪽 정렬) |
| Metadata | 400 12/16 |
| 식별자/코드 (dataset_id, probe_id, incident_id, schema_hash, timestamp) | 400 13/18 monospace |

금지: 36–48px marketing hero heading, 과장된 KPI 숫자. Public Status는 랜딩
페이지가 아니라 data/status workspace다.

### Density

Studio `VISUAL_IDENTITY.md` §5 그대로: 표 행 높이 36px, 카드 간격 약 12px,
모서리 반경 약 8px, 그림자는 없거나 아주 옅게, 표면 구분은 그림자가 아니라
border로 한다. "Dense but calm" — 10/50/150 Dataset 어느 규모에서도 유지돼야
한다(UI Lab Fixtures, PRD §37).

### Light canonical / Dark alternative

Light가 canonical visual baseline이다 — screenshot, README, 시각 리뷰의 기준은
light다. Dark는 지원하는 대체 테마이고, **의미 체계(색의 역할·상태 대응·정보
위계)는 light와 같고 값만 바뀐다.** 순수 검정(`#000000`)이나 채도 높은 navy를
쓰지 않는다. Surface 값은 Studio `src/globals.css` 그대로 가져온다:

| 토큰 | light | dark |
|---|---|---|
| `--background` | `#F7F8F3` | `#15171A` |
| `--card` | `#FFFFFF` | `#1C1F23` |
| `--muted` | `#F1F3EF` | `#23272C` |
| `--border` | `#E5E7E2` | `#2E3238` |
| `--foreground` | `#172033` | `#E8EAED` |
| `--muted-foreground` | `#5E6E84` | `#9AA3AE` |

### Status badge = color + icon + text

색상만으로 상태를 전달하지 않는다(이미 [Color Semantics](#color-semantics) 의
원칙). Status badge는 항상 색 + 아이콘(`●`/`▲`/`✕`/`?`/`ⓘ`) + 단어(`Healthy` ·
`Degraded` · `Critical` · `Unknown` · `Changed`)를 함께 쓴다.

### Contract diff — neutral surface

[Contract Diff UX](#contract-diff-ux) 의 Added/Removed/Changed 목록은 중립
표면(`--card`/`--muted`, `--border`) 위에 작은 accent만 쓴다 — Diff 전체를
warning 색으로 칠하지 않는다. Change가 Health를 낮추지 않는 것과 같은 이유다.

### Accessibility

- 대비: 텍스트 **4.5:1**, 큰 텍스트·비텍스트(아이콘, focus ring, 차트 마크)
  **3:1** (WCAG 2.1 AA). Health → status token 매핑의 네 색 모두 light·dark
  각각 subtle 배경과 `--card` 위에서 4.5:1 이상을 만족한다 — 계산 결과는 이
  PR 본문의 검토 결과에 남긴다.
- `prefers-reduced-motion: reduce` 에서 애니메이션·전환을 끈다 (Studio
  `src/globals.css` 패턴을 따른다).
- 390px 폭에서 페이지 전체 가로 스크롤이 없어야 한다. 넓은 표는 카드 안에서만
  스크롤한다.

### Public Status 헤더 naming

제품명은 shell에 한 번만 쓴다: `[K] KPubData Watch`. 페이지 제목은 그 아래
"Public Data Health" 다 ([Public Status Page](#public-status-page) 참고) — 헤더에
제품명을 반복하지 않는다(Studio VISUAL_IDENTITY §2.3 "제품명 반복 금지").

### Health summary는 거대한 KPI 카드가 아니다

[Public Status Page](#public-status-page) 의 Health 요약(`96 Healthy · 2
Degraded · 1 Critical · 1 Unknown`)은 한 줄 inline 요약이거나 작고 테두리
중심인 카드로 보여준다 — 마케팅 대시보드의 거대한 숫자 KPI 카드를 쓰지 않는다
(Typography 절의 "과장된 KPI 숫자 금지"와 같은 원칙).

### UI Lab 규칙

[UI Experiment A/B/C](#ui-experiment-a-status-page) 는 Status Page / Provider
Grouped / Issues First 를 계속 비교하지만, 세 prototype 모두 **같은 Brand v2
theme**(typography, status color, spacing, component style)를 쓴다. 비교
대상은 오직 layout이다 — 색 테마, 로고, 폰트 위계, 상태 팔레트, light/dark
브랜드 표현, 컴포넌트 시각 스타일은 비교하지 않는다(#33).

### Token 구현 방향 (참고)

Watch는 Jinja/server-rendered UI다(`docs/architecture/README.md` Technology
Recommendation). 같은 semantic token 이름을 쓰되 값은 CSS로 스냅샷한다 —
파일 위치는 architecture의 Repository Structure(`src/kpubdata_watch/web/static/`)
를 따른다. **계획 문서가 제안한 top-level `assets/theme/`는 Watch의 실제
구조와 맞지 않는다** — 정확한 경로는
`src/kpubdata_watch/web/static/theme/kpubdata-v2.css` 다. 토큰 파일 자체와
Studio-Watch drift를 검출하는 테스트는 별도 이슈(`feat(ui): add the shared
KPubData Brand v2 token foundation`, `test(ui): prevent Brand v2 token drift
from KPubData Studio`)에서 구현한다 — 이 문서는 값과 매핑만 정한다.

## UI Architecture

<small>PRD §34</small>

```text
Database
   ↓
Domain
   ↓
Read Model
   ↓
Public API
   ↓
┌───────────────┬────────────────┬───────────────┐
│ Status UI     │ Provider UI    │ Issues UI     │
└───────────────┴────────────────┴───────────────┘
```

UI가 DB Table을 직접 해석하지 않는다.

## UI Read Model

<small>PRD §35</small>

예:

```json
{
  "dataset_id": "visitkorea-tourism",

  "name": "한국관광공사 관광정보",
  "provider": "한국관광공사",

  "health": "healthy",

  "checks": {
    "availability": "pass",
    "freshness": "pass",
    "contract": "pass",
    "quality": "pass"
  },

  "active_issue": null,

  "latest_change": {
    "type": "contract",
    "severity": "info",
    "occurred_at": "2026-09-29T14:20:00+09:00"
  },

  "last_checked_at": "2026-09-30T21:10:00+09:00"
}
```

같은 Read Model로 여러 UI를 시험한다.

## UI Lab

<small>PRD §36</small>

Production UI와 별도로 UI 실험 공간을 둔다.

```text
ui-lab/
```

UI Lab은 언제든 버릴 수 있어야 한다.

Watch Engine은 UI Lab에 의존하면 안 된다.

## UI Lab Fixtures

<small>PRD §37</small>

반드시 다음 Fixture를 만든다.

```text
10-datasets.json
50-datasets.json
150-datasets.json

all-healthy.json

mixed-health.json

active-incidents.json

contract-changes.json

freshness-delay.json

provider-outage.json

unknown-monitoring.json
```

이를 통해 Dataset 규모가 커져도 UI가 유지되는지 검증한다.

## UI Experiment A — Status Page

<small>PRD §38</small>

```text
KPubData Watch

Public Data Health

47 Healthy
2 Degraded
1 Unknown

────────────────────────

한국관광공사 관광정보
Healthy

서울 버스정보
Degraded
Freshness delayed

...
```

장점:

```text
직관적
익숙함
MVP 구현 쉬움
```

## UI Experiment B — Provider Group

<small>PRD §39</small>

```text
한국관광공사
8 Healthy

국토교통부
15 Healthy · 1 Degraded

  아파트 실거래가
  Healthy

  공동주택 기본정보
  Healthy

  지하안전정보
  Degraded
```

Dataset이 50~150개 이상으로 증가했을 때 검증한다.

## UI Experiment C — Issue First

<small>PRD §40</small>

```text
Active Issues

CRITICAL
국토교통부 ○○ API
Breaking contract change

WARNING
서울 버스정보
Freshness delayed 42m

────────────────────────

All Datasets
...
```

운영자/개발자에게는 이 구조가 더 효율적일 수 있다.

## UI Evaluation Criteria

<small>PRD §41</small>

각 UI Prototype을 다음 기준으로 비교한다.

```text
1. 5초 안에 문제가 있는 Dataset을 찾을 수 있는가?

2. 10 Dataset에서도 자연스러운가?

3. 50 Dataset에서도 탐색 가능한가?

4. 150 Dataset에서도 화면이 무너지지 않는가?

5. Provider별 문제를 인지하기 쉬운가?

6. Healthy Dataset 때문에 문제 Dataset이 묻히지 않는가?

7. Health와 Change를 혼동하지 않는가?

8. UNKNOWN을 장애로 오인하지 않는가?

9. 모바일에서도 핵심 상태 확인이 가능한가?

10. 판정 근거로 자연스럽게 Drill-down할 수 있는가?

11. Studio와 같은 제품군으로 보이는가?

12. 로고를 제외해도 Brand v2의 bright / clear / data-first / professional 성격이 유지되는가?

13. Brand color와 status color를 혼동하지 않는가?

14. Light theme가 dark monitoring console보다 canonical하게 보이는가?

15. 150 Dataset에서도 Brand v2 density가 유지되는가?
```

11–15는 [Visual Identity](#visual-identity)(#68)에서 추가했다 — layout 기준(1–10)과
달리 visual identity가 정말로 고정됐는지를 검증한다.

UI 선택은 구현 편의가 아니라 이 기준으로 결정한다.

## Public Status Information Architecture

<small>PRD §42</small>

MVP Production UI 최소 구조:

```text
/
Public Status

/datasets/{dataset_id}
Dataset Detail

/incidents/{incident_id}
Incident Detail

/changes/{change_id}
Change Detail
```

UI Lab은 별도:

```text
/lab/status
/lab/provider
/lab/issues
```

Production deployment에서는 UI Lab 비활성화 가능해야 한다.

## Public Status Page

<small>PRD §43</small>

첫 화면 목표:

> **현재 문제가 있는 Dataset을 빠르게 찾는다.**

상단은 단일 "All systems operational"보다 Distribution을 우선한다.

예:

```text
Public Data Health

100 monitored datasets

96 Healthy
 2 Degraded
 1 Critical
 1 Unknown
```

이렇게 해야 한 Dataset 문제 때문에:

```text
"한국 공공데이터가 장애입니다."
```

처럼 과도하게 표현하는 것을 피할 수 있다.

## Search / Filtering

<small>PRD §44</small>

Dataset 수가 증가할 것을 고려해 Read API부터 지원 가능하게 설계한다.

향후 UI Filter:

```text
Search

Provider

Health

Check

Category
```

예:

```text
Provider = 국토교통부

Health = Degraded

Check = Freshness

Category = 부동산
```

MVP 10 Dataset에서는 UI에 전부 노출하지 않아도 된다.

## Provider Grouping

<small>PRD §45</small>

기본 Group 후보는 Provider다.

```text
Provider
   ↓
Dataset
```

Category:

```text
부동산
관광
교통
통계
환경
금융
```

은 기본 Group보다는 Filter 용도로 사용한다.

Provider 상태 자체를 하나의 색으로 단순화하지 않는다.

예:

```text
국토교통부

28 Healthy
1 Degraded
1 Unknown
```

Provider 전체 장애가 확인된 경우에만 Provider Incident를 별도로 검토한다.

## Dataset List Density

<small>PRD §46</small>

정상 Dataset에서는 세부 Check를 모두 노출하지 않는다.

권장:

```text
한국관광공사 관광정보

Healthy

Checked 3m ago
```

문제가 있는 경우에만 이유를 노출한다.

```text
서울 버스정보

Degraded

Freshness delayed 42m

Checked 2m ago
```

Change만 있는 경우:

```text
조달청 물품목록정보

Healthy

ⓘ Contract changed

Checked 5m ago
```

원칙:

> **Healthy일 때는 단순하게, 문제가 있을 때만 자세하게.**

## Dataset Detail

<small>PRD §47</small>

목표:

> 왜 이 Dataset이 현재 Health 상태인지 설명한다.

예:

```text
한국관광공사
국문 관광정보 API

HEALTHY

Last checked
21:12:43 KST

Last successful
21:12:43 KST

────────────────────────

Checks

Availability
PASS

Freshness
PASS

Contract
PASS

Quality
PASS

────────────────────────

Recent Changes

Sep 29 14:20
Contract changed
+ productEngName

────────────────────────

Recent Incidents

None
```

## Why Was This Detected?

<small>PRD §48</small>

모든 Warning/Critical 결과에는 이 UI를 제공한다.

예:

```text
Freshness delayed

Why was this detected?

Expected
09:00 ± 30 min

Observed
latest data = 07:58

Checked
09:37

Difference
1h 39m

Rule
Expected update window exceeded
```

KPubData Watch UI의 핵심 원칙이다.

## Contract Diff UX

<small>PRD §49</small>

기본 화면:

```text
Contract Change

Added

+ productEngName    string
+ manufacturerCode string


Removed

- addr2             string


Changed

~ price
  integer → string
```

기본은 Human-readable Diff다.

추가:

```text
View raw schema
View raw diff
```

형태로 기술 근거를 제공한다.

원칙:

```text
Human-readable first
Raw evidence second
```

## History UX

<small>PRD §50</small>

Dataset Detail에는 시간 흐름을 제공한다.

예:

```text
Sep 30 21:12
Healthy

Sep 30 20:12
Healthy

Sep 30 19:12
Healthy

Sep 29 14:20
Contract changed

Sep 27 09:37
Freshness delayed

Sep 27 10:21
Recovered
```

Watch의 장기 자산은 단순 현재 상태가 아니라 History다.

## Charts

<small>PRD §51</small>

Chart는 최소화한다.

MVP에서 다음과 같은 Dashboard는 만들지 않는다.

```text
Requests
Latency
Volume
Errors
Availability
Freshness
Null Ratio
...
```

대신 의미를 우선한다.

예:

```text
Volume

10,124 records

Expected range
9,850–10,420

PASS
```

추후 필요 시 Sparkline을 추가할 수 있다.

## Visual Design Principles

<small>PRD §52</small>

UI 톤:

```text
Status Page
+
Developer Infrastructure
+
Data Observability
```

피해야 하는 방향:

```text
화려한 BI Dashboard
Marketing-heavy SaaS Landing
복잡한 Azure Portal식 화면
```

기본:

```text
Light background
Simple border
Minimal shadow

8–12px radius

8px spacing grid

System/Pretendard-like sans serif

Technical values
monospace optional
```

## Color Semantics

<small>PRD §53</small>

색상만으로 상태를 표현하지 않는다.

텍스트 + 아이콘 + 색상을 함께 사용한다.

의미:

```text
Healthy
Green

Degraded
Yellow / Amber

Critical
Red

Unknown
Gray

Informational Change
Blue / Neutral
```

접근성을 위해:

```text
● Healthy

▲ Degraded

✕ Critical

? Unknown

ⓘ Change
```

등의 시각적 단서를 함께 제공한다.

## Time UX

<small>PRD §54</small>

상대시간과 정확한 시간을 함께 제공한다.

기본:

```text
3 min ago
```

상세/Tooltip:

```text
2026-09-30 21:12:43 KST
```

Incident/History에서는 정확한 시간을 기본으로 표시한다.

## Official Notice

<small>PRD §55</small>

MVP P0에서는 자동 공지 Crawling을 요구하지 않는다.

초기:

```text
Operator manually attaches official notice URL
```

Incident:

```text
Observed
09:37

Official Notice
10:12
```

처럼 보여줄 수 있다.

향후:

```text
Notice crawler
      ↓
Candidate matching
      ↓
Operator confirmation
      ↓
Explain
```

으로 확장한다.
