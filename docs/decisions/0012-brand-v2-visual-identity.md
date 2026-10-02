# ADR 0012: KPubData Watch는 KPubData Studio Brand v2를 canonical visual identity로 채택한다

## 상태

채택됨(Accepted) — 2026-10-02 (결정 로그 D-021 · D-022 · D-023 · D-024, #68)

## 요약 (English summary)

> KPubData Watch adopts KPubData Studio's Brand v2 visual identity (logo
> geometry, brand palette, status-color semantics, typography, density,
> light/dark theme hierarchy, accessibility rules) as canonical, rather than
> designing its own. Only Watch's information architecture and layout — Status
> Page vs Provider Grouped vs Issues First, card vs table, filter placement —
> stay experimental (ADR 0005). Brand color and status color remain separate
> systems; Fresh Mint is never Healthy. Studio's `docs/brand/VISUAL_IDENTITY.md`
> and `src/globals.css` are the source of truth, and Watch does not restate
> values it can instead reference.

## 문제

`docs/UI.md`는 "색상 세부 규칙"을 Card vs Table, Dashboard 형태 등과 같은 층위의
"고정하지 않을 것"에 두고 있었다. 하지만 KPubData Studio는 이미 Brand v2(#628)로
palette · 로고 · typography · 상태 색 체계를 확정했다. Watch가 색을 독자적으로
실험하면 같은 제품군(KPubData · Builder · Studio · Watch)이 서로 다른 제품처럼
보이고, 이후 공통 컴포넌트·토큰을 재사용하기 어려워진다(#68).

동시에 Watch의 실제 실험 대상 — Status/Provider/Issues 중 어떤 정보구조가
10/50/150 Dataset에서 가장 잘 작동하는가(#33) — 는 그대로 유지해야 한다. 두
실험(visual identity, information architecture)을 구분하지 않으면 UI Lab 비교
결과가 색·타이포 차이로 오염된다.

## 결정

- **D-021** KPubData Watch는 KPubData Studio Brand v2와 동일한 visual identity를
  사용한다 — 같은 minimal geometric K 심볼과 lockup 위계, 같은 brand
  palette(`--brand-primary` `#2563EB` · `--data-accent` `#06B6D4` ·
  `--brand-secondary` `#14B8A6`), 같은 중립 표면(Canvas `#F7F8F3` · Surface
  `#FFFFFF` · Border `#E5E7E2` · Ink `#172033`), 같은 상태 토큰 체계
  (`--status-success/warning/failure/unknown`), 같은 typography(20/28 page
  title 등)와 density(36px row, 12px gap, 8px radius)를 쓴다. Canonical source는
  Studio `docs/brand/DESIGN_CONCEPT.md`, `docs/brand/VISUAL_IDENTITY.md`,
  `src/globals.css`이고, 값이 Watch 문서와 다르면 Studio가 정본이다.
- **D-022** UI Lab(ADR 0005)에서 실험하는 것은 information architecture와
  layout(Status Page / Provider Grouped / Issues First, card vs table, filter
  배치 등)이며, brand palette / 로고 / typography / status semantics는 실험하지
  않는다 — `docs/UI.md`의 UI Evaluation Criteria에 11–15를 추가해 이 경계를
  리뷰에서 확인한다.
- **D-023** Light theme를 canonical visual baseline으로 쓴다. Screenshot ·
  README · 시각 리뷰의 기준은 light이고, Dark mode는 같은 정보 위계·색의
  역할·상태 대응을 유지하는 대체 사용자 테마다(Studio DESIGN_CONCEPT §10).
  Dark 상태 토큰 값도 Studio `src/globals.css`의 `:root[data-theme="dark"]`
  값을 그대로 쓴다 — Watch가 새로 값을 정하지 않는다.
- **D-024** Brand color와 status color를 분리한다. Fresh Mint(`--brand-secondary`)
  를 Healthy 표현에 쓰지 않고, Brand Blue(`--brand-primary`)·Data Cyan
  (`--data-accent`)도 상태를 뜻하지 않는다. Status는 오직
  `--status-success/warning/failure/unknown`로만 표현하고, 색은 항상 아이콘과
  단어를 동반한다(Status badge = color + icon + text).

Watch 고유의 "Change는 Health와 분리된 축" 표현("ⓘ Changed")에는 Studio가 정의한
informational/neutral 전용 status token이 없다는 것을 확인했다 — Studio
`src/globals.css`와 `VISUAL_IDENTITY.md` §3.2에는 success/warning/failure/unknown
(그리고 warning과 값을 공유하는 stale/partial)만 있다. 이 ADR은 그 자리에 새 색을
만들지 않고 Studio의 neutral surface token(`--foreground` · `--muted` ·
`--border` · `--muted-foreground`)을 쓰기로 하되, 이는 Studio가 공식화한 결정이
아니므로 열린 점으로 남긴다 — 자세한 내용은 `docs/UI.md` Visual Identity 절.

자세한 토큰 매핑, typography, density, accessibility 수치는 `docs/UI.md`
Visual Identity 절에 있다 — 이 ADR은 값을 반복하지 않는다.

## 결과

- `docs/UI.md`의 "고정하지 않을 것" 목록에서 "색상 세부 규칙"을 제거하고
  Visual Identity 절을 추가한다. UI Evaluation Criteria에 11–15를 추가한다.
- ADR 0005(UI Lab)는 그대로 유효하다 — 이 ADR은 UI Lab이 비교하는 대상의 범위를
  정보구조/layout으로 좁힐 뿐, UI를 확정하지 않는다는 원칙 자체를 바꾸지 않는다.
- ADR 0002(Change와 Incident 분리, 정보성 Change가 Health를 낮추지 않음)와 상충하지
  않는다 — 오히려 그 구분을 시각적으로 강제한다.
- 토큰 CSS 파일, logo/lockup 자산, 공유 UI 컴포넌트, Studio-Watch drift 검출은
  각각 별도 이슈(`feat(ui): add the shared KPubData Brand v2 token foundation`,
  `feat(brand): add the KPubData Watch Brand v2 logo and lockup assets`,
  `feat(ui): add Brand v2 status and surface primitives for Watch`,
  `test(ui): prevent Brand v2 token drift from KPubData Studio`)에서 구현한다 —
  이 ADR은 결정만 기록한다.
