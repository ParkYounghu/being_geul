##### [Prompt for One Page]

현재 작성된 FastAPI 기반의 웹 애플리케이션을 **기능이 강화된 SPA(Single Page Application)** 형태로 리팩토링해줘.

다음 요구사항을 엄격하게 준수하여 `main.py`, `templates/index.html`, `static/script.js`, `static/style.css` 4개 파일의 전체 코드를 새로 작성해.

### 1. ⛔ 핵심 제약 사항 (Critical Constraints)
* **보안 필수:** `.env` 파일은 절대 수정하거나, 삭제하거나, 읽으려 하지 말 것. 기존 환경 변수 설정을 건드리지 말고 코드에 하드코딩하지 말 것.
* **로직 유지:** `localStorage`를 이용한 좋아요 저장 로직, `Analysis` 탭의 통계 계산 로직 등 기존 핵심 비즈니스 로직은 100% 유지할 것.

### 2. 🏗️ 구조 및 아키텍처 (Structure)
* **SPA 통합:** `main.py`는 오직 루트 경로(`/`) 하나에서 `index.html`을 렌더링하며, 이때 DB의 모든 정책 데이터를 `policies` 변수로 넘겨준다.
* **단일 템플릿:** 기존의 `index_01`~`04` html 파일들을 `templates/index.html` 하나로 통합한다.
* **섹션 구분:** `<main>` 태그 안에 4개의 섹션(`section-home`, `section-liked`, `section-analysis`, `section-search`)을 만들고, GSAP를 사용하여 탭 메뉴 클릭 시 부드럽게 화면이 전환되도록 구현한다.
* **데이터 직렬화:** 프론트엔드에서 실시간 검색을 처리하기 위해, Jinja2로 받은 `policies` 데이터를 `index.html` 내부 `<script>` 태그에서 자바스크립트 변수 `const allPolicies = ...` 형태로 직렬화하여 할당한다.

### 3. ✨ 주요 기능 명세 (Features)

**(A) 홈 화면: 스와이프 & 검색 (Home Section)**
* **실시간 검색 필터:** 화면 상단(Header 아래)에 고정된 검색창(`input`)을 배치한다. 검색어를 입력하면 실시간으로 `allPolicies` 데이터를 필터링하여, 스와이프할 카드 스택(Deck)을 즉시 재구성한다. (새로고침 없음)
* **스와이프 로직 반전 (Logic Swap):**
    * **왼쪽 드래그:** **좋아요(Like)** 처리 및 LocalStorage 저장. (초록색 텍스트 인디케이터)
    * **오른쪽 드래그:** **패스(Pass)** 처리. (붉은색 텍스트 인디케이터)
* **되돌리기(Undo):** 화면 좌측 하단에 플로팅 버튼(↩️)을 배치하고, 클릭 시 마지막으로 넘긴 카드를 다시 스택으로 복귀시킨다.
* **클릭 이벤트 분기 (UX 중요):** 드래그 오작동 방지를 위해, 홈 화면의 카드는 **오직 '제목(Title)'을 클릭했을 때만** 상세 모달이 열려야 한다. (카드 본문 클릭 시에는 드래그만 동작)

**(B) 상세 보기 모달 & 공유 (Detail Modal)**
* **공통 동작:** 홈(제목 클릭), 좋아요/검색(카드 전체 클릭) 어디서든 상세 보기를 요청하면 화면 중앙에 CSS 기반의 **모달 팝업**을 띄운다.
* **모달 내용:** 정책의 제목, 기간, 요약 내용을 전체적으로 보여준다.
* **액션 버튼:** 모달 하단에 두 개의 버튼을 배치한다.
    1.  **공유하기(Share 🔗):** 모바일에서는 `navigator.share`를 호출하고, PC에서는 클립보드에 "제목 + 링크"를 복사한다.
    2.  **원문 보기(Link 🌐):** 새 탭에서 실제 정책 사이트로 이동한다.

**(C) 좋아요 & 검색 그리드 (Grid Sections)**
* **좋아요(Liked):** LocalStorage에 저장된 ID에 해당하는 정책만 그리드 뷰로 보여준다.
* **검색(Search):** 모든 정책을 그리드 뷰로 보여준다.
* **클릭 동작:** 이 두 섹션에서는 카드(Grid Item)의 **어느 곳을 눌러도** 상세 모달이 열려야 한다.

### 4. 🎨 스타일링 (CSS)
* 제공된 다크 모드 테마를 유지한다.
* 각 섹션(`section`)은 `absolute` 포지셔닝으로 겹쳐두고, GSAP로 `opacity/visibility`를 조절한다.
* **플로팅 요소:** 검색창(상단 중앙), 되돌리기 버튼(좌측 하단), 모달 오버레이는 `z-index`를 높게 설정하여 카드보다 위에 오도록 한다.

위의 모든 사항을 반영하는 프롬프트를 Gemini CLI에 넣는 JSON 형식으로 작성해줘.


#### 결과

```

{
  "task": "Refactor the existing FastAPI app into a robust Single Page Application (SPA) incorporating Real-time Search Filter, Undo, Detail Modal, Policy Sharing, and SWAPPED Swipe Logic.",
  "constraints": [
    "CRITICAL: THE '.env' FILE IS STRICTLY OFF-LIMITS. DO NOT MODIFY, DELETE, OR READ IT. KEEP IT EXACTLY AS IS.",
    "CRITICAL: Preserve ALL existing business logic (LocalStorage handling, Analysis chart calculation).",
    "MERGE TEMPLATES: Combine index_01.html through index_04.html into a single 'templates/index.html'. Structure it with 4 sections: #section-home, #section-liked, #section-analysis, #section-search (Grid view).",
    "DATA HANDLING: In 'index.html', serialize the 'policies' Jinja2 variable into a JavaScript variable 'const allPolicies = ...' using the '| tojson' filter so the frontend can access the full dataset for filtering and modal details.",
    "FEATURE 1 (Home Search Filter): Add a floating search input at the top of #section-home. Implement JS logic to filter the swipe card stack in real-time. When the user types, clear the stack and rebuild it using only policies matching the input (Title/Summary).",
    "FEATURE 2 (Undo): Add a floating 'Return (↩️)' button in #section-home. Store swiped cards in a history stack and restore the last swiped card when clicked.",
    "FEATURE 3 (Modal & Share): Add a click event to cards. IMPORTANT UX: In #section-home, ONLY clicking the 'Title' opens the modal (to avoid drag conflict). In Grid sections, clicking anywhere on the card opens the modal. The Modal must show Title, Period, Summary, and have 'Share (🔗)' (navigator.share) and 'Link (🌐)' buttons.",
    "FEATURE 4 (SWAP DIRECTIONS): Reverse the swipe logic in 'script.js' and 'style.css'. Dragging RIGHT (positive X) must trigger PASS (Red indicator). Dragging LEFT (negative X) must trigger LIKE (Green indicator) and save the ID to LocalStorage.",
    "STYLE: Use absolute positioning for overlapping sections. Style the Home Search Bar (top-center, z-index high), Undo Button (bottom-left), and Modal Overlay (dark semi-transparent background).",
    "JS: Refactor 'initSwipePage' to handle the swapped direction logic, accept a filtered data list for dynamic stack rebuilding, and manage modal open/close events."
  ],
  "current_code_context": {
    "main.py": "import os\nfrom dotenv import load_dotenv\nfrom fastapi import FastAPI, Depends, Request\nfrom fastapi.templating import Jinja2Templates\nfrom fastapi.staticfiles import StaticFiles\nfrom sqlalchemy import create_engine, Column, Integer, String, Text\nfrom sqlalchemy.orm import sessionmaker, Session, declarative_base\n\n# ... (Existing DB Setup) ...\n\napp = FastAPI()\napp.mount('/static', StaticFiles(directory='static'), name='static')\ntemplates = Jinja2Templates(directory='templates')\n\n# ... (Existing Routes index_01 to index_04) ...",
    "static/script.js": "// ... (Existing Swipe Logic, LocalStorage Logic, Analysis Logic) ...",
    "static/style.css": "/* ... (Existing CSS) ... */"
  },
  "requested_output": {
    "file_1": "main.py (Refactored to Single Endpoint '/' serving 'index.html')",
    "file_2": "templates/index.html (Unified HTML containing 4 sections, Search Input, Modal Structure, and Data Serialization)",
    "file_3": "static/style.css (Updated for SPA layout, Floating Search Bar, Undo Button, Modal Styles, and Swapped Swipe Indicator Colors)",
    "file_4": "static/script.js (Comprehensive Logic: SPA Navigation, Real-time Search Filtering, Undo Stack, Modal Interactions, Native Share, and LEFT-IS-LIKE Swipe Logic)"
  }
}

```