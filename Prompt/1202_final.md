#### 최종결과물을 위한 통합 프롬프트

```

최종 완성본 생성용 통합 프롬프트
[역할] 너는 UI/UX 감각이 뛰어난 시니어 풀스택 개발자야. 현재 초기 단계인 FastAPI 기반 '정책 추천 웹 서비스'를 리팩토링하여, 완성도 높은 최종 코드를 작성해줘.

[작업 목표] 다음 5개 파일(main.py, index.html, mypage.html, style.css, script.js)을 아래의 상세 요구사항을 빠짐없이 반영하여 처음부터 끝까지 작성해줘.

[상세 요구사항]

1. 백엔드 (main.py)

FastAPI 설정: Jinja2Templates, StaticFiles 마운트.

DB 모델: BeingGeul (id, title, summary, period, link, genre).

라우터: / (index.html), /mypage.html (mypage.html) 렌더링.

API: /api/generate-nickname (POST) - 좋아요한 데이터를 받아 랜덤 닉네임 반환.

2. 프론트엔드 구조 (HTML)

공통: main-scroll-container를 사용하여 세로 스크롤 스냅(scroll-snap-type: y mandatory) 구현.

index.html (메인):

섹션 1 (랜딩): 로고, 이미지 플레이스홀더, 세련된 '로그인'(그라데이션)/'회원가입'(라인) 버튼, '둘러보기' 버튼 배치.

섹션 2 (카드): 카드 스택 영역.

섹션 3 (닉네임) & 4 (차트): 결과 표시 영역.

모달: 로그인 모달, 상세 모달(공유/알림/원문보기 버튼 포함).

mypage.html (마이페이지):

섹션 1 (헤더): 좌측 상단 '← 메인으로' 버튼, 육각형 차트.

섹션 2 (리스트):

헤더: [전체 선택] 체크박스, 제목, [선택 삭제], [삭제 취소] 버튼 배치.

리스트 컨테이너: #mypage-results.

3. 스타일링 (style.css) - 디자인 고도화

테마: 다크 모드(#1a1a1a) 배경.

메인 카드 (Main Page):

크기: 384px x 576px (기존 대비 120% 확대).

기간 배지: 텍스트 겹침 방지를 위해 카드 내부가 아닌 **카드 바깥 우측 상단(top: -45px)**에 반투명 배지 형태로 배치. (overflow: visible 필수)

배경: 불투명 #222 (뒤쪽 카드 비침 방지).

마이페이지 리스트 (My Page):

레이아웃: 리스트 컨테이너(max-width: 700px)를 가운데 정렬하여, 스크롤바가 화면 끝이 아닌 리스트 바로 옆에 붙도록 수정.

카드: 흰색 배경, 넉넉한 패딩, 그림자 효과. 좌측에 체크박스 추가.

장르 필터: 둥근 알약(Pill) 모양 버튼. (중요: CSS에서 background-color를 지정하지 말 것. JS에서 동적 할당함).

4. 기능 로직 (script.js)

카드 덱 시스템 (Deck Logic):

initMainPage에서 데이터를 단 한 번만 섞어서(shuffle) availablePolicies 대기열에 저장.

loadMoreCards는 이 대기열에서 10장씩 splice하여 가져옴 (중복 노출 원천 차단).

마이페이지 기능 강화:

다중 삭제: 체크박스 선택 후 '선택 삭제' 클릭 시 일괄 삭제 (deleteSelectedItems).

전체 선택: 헤더의 체크박스로 전체 선택/해제 (toggleAll).

삭제 취소: 삭제된 항목을 스택에 저장했다가 '취소' 버튼으로 복구 (restoreLastItem).

색상 복구: renderGenreFilters 함수에서 버튼 생성 시 반드시 btn.style.backgroundColor = getGenreColor(g)를 실행하여 색상 적용.

UX: 로그인 성공 시, 랜딩 페이지에서 메인 카드 섹션으로 부드럽게 스크롤 이동.

[출력 요청] 위 내용을 모두 포함한 5개 파일의 전체 코드를 코드 블록으로 순서대로 출력해줘.

```