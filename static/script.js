// --- Global State ---
let currentCardStack = [];
let lastSwiped = [];
let isLoggedIn = false;
let currentSection = 'landing-section';

// --- Genre to Color Mapping ---
const genreColors = {
    '금융': '#2E7D32',  // 짙은 녹색
    '주거': '#1565C0',  // 짙은 파랑
    '창업': '#F9A825',  // 짙은 노랑
    '인력': '#C62828',  // 짙은 빨강
    '기술': '#6A1B9A',  // 짙은 보라
    '기타': '#455A64',  // 짙은 회색
};

// --- DOMContentLoaded: Initializer ---
document.addEventListener('DOMContentLoaded', () => {
    // 1. 데이터 로드 확인
    if (typeof window.allPolicies !== 'undefined') {
        allPolicies = window.allPolicies;
        console.log("Data loaded:", allPolicies.length, "policies");
    } else {
        console.error("Policy data not found.");
    }

    // 2. 이벤트 리스너 설정
    setupEventListeners();

    // 3. 초기 화면 설정 (랜딩 페이지)
    switchSection('landing-section');
    
    // 4. GSAP 초기화 (선택적)
    if(typeof gsap !== 'undefined') {
        gsap.to(".page-section", { autoAlpha: 0, display: "none", duration: 0 });
        gsap.to("#landing-section", { autoAlpha: 1, display: "flex", duration: 0 });
    }
});

// --- Event Listeners Setup ---
function setupEventListeners() {
    // Landing Page Buttons
    document.getElementById('login-btn-landing').addEventListener('click', () => {
        // 랜딩에서 로그인 누르면 바로 로그인 모달 -> 로그인 성공 시 메인으로
        openModal('login-modal');
    });
    document.getElementById('signup-btn-landing').addEventListener('click', () => alert('회원가입 기능은 준비 중입니다.'));
    document.getElementById('browse-btn-landing').addEventListener('click', () => {
        // 비회원 둘러보기
        isLoggedIn = false;
        switchSection('main-section');
    });

    // Main Page Buttons
    document.getElementById('undo-btn').addEventListener('click', undoLastSwipe);
    document.getElementById('load-more-btn').addEventListener('click', loadMoreCards);
    document.getElementById('main-search-input').addEventListener('input', handleSearch);

    // Login Modal Buttons
    document.getElementById('login-btn-modal').addEventListener('click', () => {
        closeModal('login-modal');
        login(); // 로그인 처리 및 메인으로 이동
    });
    document.getElementById('signup-btn-modal').addEventListener('click', () => alert('회원가입 기능은 준비 중입니다.'));
    
    // Detail Modal Buttons
    const detailModal = document.getElementById('detail-modal');
    if (detailModal) {
        detailModal.querySelector('.close-modal').addEventListener('click', () => closeModal('detail-modal'));
    }
    const loginModal = document.getElementById('login-modal');
    if (loginModal) {
        // 로그인 모달 배경 클릭 시 닫기 (선택사항)
        loginModal.addEventListener('click', (e) => {
           if(e.target === loginModal) closeModal('login-modal');
        });
    }
}

// --- Page/Section Management ---
function switchSection(sectionId) {
    // GSAP를 사용한 부드러운 전환
    const outgoing = document.querySelector('.page-section.active');
    const incoming = document.getElementById(sectionId);

    if (outgoing && outgoing !== incoming) {
        gsap.to(outgoing, { 
            duration: 0.3, 
            autoAlpha: 0, 
            display: "none",
            onComplete: () => outgoing.classList.remove('active')
        });
    }

    // 상태 업데이트 및 화면 렌더링
    currentSection = sectionId;
    
    // 렌더링 로직
    if (sectionId === 'main-section') {
        renderMainPage();
    } else if (sectionId === 'mypage-section') {
        renderMyPage();
    } else if (sectionId === 'landing-section') {
        // 랜딩으로 돌아갈 때 초기화 할 것들
    }

    // Incoming 섹션 표시
    if (incoming) {
        incoming.classList.add('active');
        // 랜딩 페이지는 flex, 나머지는 block (CSS 상속)
        const displayType = sectionId === 'landing-section' ? 'flex' : 'block';
        gsap.to(incoming, { duration: 0.3, autoAlpha: 1, display: displayType });
    }
}

// --- Login / Logout Logic ---
function login() {
    isLoggedIn = true;
    switchSection('main-section'); // 로그인 후 메인으로
}

function logout() {
    isLoggedIn = false;
    // 로그아웃 시 랜딩으로 보낼지, 메인에 남길지 결정. 여기선 메인 리렌더링
    alert('로그아웃 되었습니다.');
    updateMainHeader();
    switchSection('landing-section'); // 랜딩으로 복귀
}

function updateMainHeader() {
    const container = document.querySelector('.top-right-buttons');
    container.innerHTML = ''; // 초기화

    if (isLoggedIn) {
        // 로그인 상태: 마이페이지, 로그아웃
        const myPageBtn = document.createElement('button');
        myPageBtn.innerText = "마이페이지";
        myPageBtn.onclick = () => switchSection('mypage-section');

        const logoutBtn = document.createElement('button');
        logoutBtn.innerText = "로그아웃";
        logoutBtn.onclick = logout;

        container.appendChild(myPageBtn);
        container.appendChild(logoutBtn);
    } else {
        // 비로그인 상태: 로그인, 회원가입
        const loginBtn = document.createElement('button');
        loginBtn.innerText = "로그인";
        loginBtn.onclick = () => openModal('login-modal'); // 로그인 모달 띄우기

        const signupBtn = document.createElement('button');
        signupBtn.innerText = "회원가입";
        signupBtn.onclick = () => alert('준비 중');

        container.appendChild(loginBtn);
        container.appendChild(signupBtn);
    }
}

// --- Main Swipe Page Logic ---
function renderMainPage() {
    updateMainHeader();
    
    // 카드가 없으면 초기에 로드
    if (currentCardStack.length === 0) {
        loadMoreCards();
    } else {
        renderCardStack();
    }
}

function getRandomPolicies(count) {
    const shuffled = [...allPolicies].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
}

function loadMoreCards() {
    const newCards = getRandomPolicies(10);
    currentCardStack = [...currentCardStack, ...newCards];
    renderCardStack();
    
    // Load More 버튼 숨기기 (카드가 추가되었으므로)
    document.getElementById('load-more-btn').style.display = 'none';
}

function renderCardStack() {
    const container = document.getElementById('card-container');
    container.innerHTML = '';
    
    // 역순으로 렌더링해야 첫 번째 카드가 맨 위에 옴 (DOM 구조상)
    // 하지만 여기서는 절대위치(absolute)를 쓰므로 z-index 관리가 필요
    // currentCardStack의 [0]번이 맨 위로 보이게 하려면, DOM에는 마지막에 추가하거나 z-index를 높여야 함
    
    // 렌더링용 배열 (뒤집어서 추가, [0]번이 가장 나중에 append되어 맨 위로)
    const renderList = [...currentCardStack].reverse();

    renderList.forEach((policy, index) => {
        const card = createCardElement(policy);
        // 스택 효과: 뒤에 있는 카드들은 조금 작게
        /*
        if (index < renderList.length - 1) {
            card.style.transform = 'scale(0.95) translateY(10px)';
            card.style.opacity = '0.5';
        }
        */
        container.appendChild(card);
    });

    if (currentCardStack.length === 0) {
        document.getElementById('load-more-btn').style.display = 'block';
    } else {
        document.getElementById('load-more-btn').style.display = 'none';
    }
}

function createCardElement(policy) {
    const card = document.createElement('div');
    card.className = 'card';
    card.dataset.id = policy.id;
    
    // Genre별 배경색 적용
    const bgColor = genreColors[policy.genre] || genreColors['기타'];
    card.style.background = `linear-gradient(135deg, ${bgColor} 0%, #1a1a1a 120%)`;

    // 요청하신 카드 내부 구조 (3:4 비율 내 배치)
    card.innerHTML = `
        <div class="card-content" onclick="openDetailModal('${policy.id}')">
            <div class="card-summary">${policy.summary}</div>
            <div class="card-title">${policy.title}</div>
            <div class="card-illustration">🖼️</div> <div class="card-period">${policy.period}</div>
        </div>
        
        <div class="floating-buttons" onclick="event.stopPropagation()">
            <button onclick="window.open('${policy.link}', '_blank')">원문</button>
            <button onclick="sharePolicy('${policy.title}', '${policy.link}')">공유</button>
            <button onclick="alert('알림 설정 완료!')">알림</button>
        </div>
    `;
    
    initCardEvents(card);
    return card;
}

function undoLastSwipe() {
    if (lastSwiped.length > 0) {
        const lastPolicy = lastSwiped.pop();
        currentCardStack.unshift(lastPolicy); // 맨 앞에 다시 추가
        renderCardStack();
    } else {
        alert('되돌릴 카드가 없습니다.');
    }
}

// 스와이프 이벤트 로직
function initCardEvents(card) {
    let startX = 0;
    let isDragging = false;
    
    const onStart = (e) => {
        isDragging = true;
        startX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
        card.style.transition = 'none'; 
    };

    const onMove = (e) => {
        if (!isDragging) return;
        
        const currentX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
        const offsetX = currentX - startX;
        
        // 카드 회전 및 이동
        card.style.transform = `translateX(${offsetX}px) rotate(${offsetX / 20}deg)`;

        // 인디케이터 표시
        const likeInd = document.getElementById('like-indicator');
        const passInd = document.getElementById('pass-indicator');
        const opacity = Math.min(Math.abs(offsetX) / 100, 1);
        
        if (offsetX > 0) { // 오른쪽 (Like)
            if(likeInd) likeInd.style.opacity = opacity;
            if(passInd) passInd.style.opacity = 0;
        } else { // 왼쪽 (Pass)
            if(passInd) passInd.style.opacity = opacity;
            if(likeInd) likeInd.style.opacity = 0;
        }
    };

    const onEnd = (e) => {
        if (!isDragging) return;
        isDragging = false;
        
        const endX = e.type === 'touchend' ? e.changedTouches[0].clientX : e.clientX;
        const offsetX = endX - startX;
        const threshold = window.innerWidth / 4; 

        if (Math.abs(offsetX) > threshold) {
            const isLike = offsetX > 0; 
            const direction = offsetX > 0 ? 1 : -1;
            
            card.style.transition = 'transform 0.5s ease';
            card.style.transform = `translateX(${direction * window.innerWidth}px) rotate(${direction * 30}deg)`;
            
            // 데이터 처리
            const policyId = card.dataset.id;
            const policyData = allPolicies.find(p => p.id == policyId);
            
            lastSwiped.push(policyData); // Undo를 위해 저장

            if (isLike) {
                saveLikedItem(policyId);
            }
            
            // UI 업데이트 (애니메이션 후 제거)
            setTimeout(() => {
                currentCardStack.shift(); // 스택의 첫 번째(현재 카드) 제거
                renderCardStack();
                resetIndicators();
                
                // 로그인 유도 트리거 (랜덤) - 로그인 안했을 때
                if (!isLoggedIn && Math.random() < 0.3) {
                     // 30% 확률로 로그인 모달 띄우기 (UX 방해 안되게 조절 가능)
                     // openModal('login-modal'); 
                }
            }, 300);

        } else {
            // 원위치 복귀
            card.style.transition = 'transform 0.3s ease';
            card.style.transform = 'translateX(0) rotate(0)';
            resetIndicators();
        }
    };

    card.addEventListener('mousedown', onStart);
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onEnd);
    
    card.addEventListener('touchstart', onStart);
    document.addEventListener('touchmove', onMove, { passive: false });
    document.addEventListener('touchend', onEnd);
}

function resetIndicators() {
    const likeInd = document.getElementById('like-indicator');
    const passInd = document.getElementById('pass-indicator');
    if(likeInd) likeInd.style.opacity = 0;
    if(passInd) passInd.style.opacity = 0;
}

// --- My Page Logic ---
function renderMyPage() {
    // 1. 차트 그리기
    setTimeout(renderHexagonChart, 100); // DOM 렌더링 시간 확보
    // 2. 필터 버튼 생성
    renderGenreFilters();
    // 3. 리스트 생성 (전체)
    renderPlacardList();
    // 4. 홈버튼 (헤더 좌측 상단 등에 추가 가능, 현재는 없음)
}

function renderHexagonChart() {
    const canvas = document.getElementById('hexagon-chart');
    if (!canvas) return;
    
    // Canvas 크기 반응형 조정 (부모 크기에 맞춤)
    const container = canvas.parentElement;
    canvas.width = container.offsetWidth;
    canvas.height = container.offsetHeight;

    const ctx = canvas.getContext('2d');
    const size = Math.min(canvas.width, canvas.height) / 2 - 20; // 여백 20
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    const likedItems = getLikedItems();
    const genreCounts = {};
    const genres = Object.keys(genreColors); // 정의된 장르 목록 사용
    
    genres.forEach(g => genreCounts[g] = 0);

    likedItems.forEach(id => {
        const policy = allPolicies.find(p => p.id == id);
        // 정책 데이터에 있는 genre가 정의된 genreColors에 없으면 '기타'로 처리
        if (policy) {
            let g = policy.genre || '기타';
            if (!genres.includes(g)) g = '기타';
            genreCounts[g]++;
        }
    });

    const maxVal = Math.max(...Object.values(genreCounts), 5); // 최소값 5로 설정하여 그래프 모양 유지
    const angleStep = (Math.PI * 2) / genres.length;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. 그리드 그리기 (3단계)
    ctx.strokeStyle = '#666';
    ctx.lineWidth = 1;
    for (let level = 1; level <= 3; level++) {
        const currentSize = (size / 3) * level;
        ctx.beginPath();
        for (let i = 0; i < genres.length; i++) {
            const angle = angleStep * i - Math.PI / 2;
            const x = centerX + currentSize * Math.cos(angle);
            const y = centerY + currentSize * Math.sin(angle);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.stroke();
    }

    // 2. 데이터 폴리곤 그리기
    ctx.beginPath();
    genres.forEach((genre, i) => {
        const value = genreCounts[genre] / maxVal; // 0.0 ~ 1.0
        const angle = angleStep * i - Math.PI / 2;
        const x = centerX + size * value * Math.cos(angle);
        const y = centerY + size * value * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.fillStyle = 'rgba(76, 175, 80, 0.6)';
    ctx.fill();
    ctx.strokeStyle = '#4CAF50';
    ctx.lineWidth = 3;
    ctx.stroke();

    // 3. 텍스트 라벨
    ctx.fillStyle = '#fff';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    genres.forEach((genre, i) => {
        const angle = angleStep * i - Math.PI / 2;
        const x = centerX + (size + 15) * Math.cos(angle); // 그래프 밖으로 살짝 뺌
        const y = centerY + (size + 15) * Math.sin(angle);
        ctx.fillText(genre, x, y);
    });
}

function renderGenreFilters() {
    const container = document.querySelector('.genre-filters');
    container.innerHTML = '';
    
    const genres = Object.keys(genreColors);
    
    // '전체' 버튼
    const allBtn = document.createElement('button');
    allBtn.innerText = "전체";
    allBtn.style.backgroundColor = "#555";
    allBtn.onclick = () => renderPlacardList(null);
    container.appendChild(allBtn);

    genres.forEach(genre => {
        const button = document.createElement('button');
        button.innerText = genre;
        button.style.backgroundColor = genreColors[genre];
        button.addEventListener('click', () => renderPlacardList(genre));
        container.appendChild(button);
    });
}

function renderPlacardList(filterGenre = null) {
    const container = document.getElementById('mypage-results');
    container.innerHTML = '';
    
    const likedIds = getLikedItems();
    let likedPolicies = allPolicies.filter(p => likedIds.includes(String(p.id)));

    if (filterGenre) {
        likedPolicies = likedPolicies.filter(p => p.genre === filterGenre);
    }

    if (likedPolicies.length === 0) {
        container.innerHTML = "<p style='text-align:center; color:#888;'>보관된 정책이 없습니다.</p>";
        return;
    }

    likedPolicies.forEach(policy => {
        const placard = document.createElement('div');
        placard.className = 'placard-card';
        placard.onclick = () => openDetailModal(policy.id); // 상세 보기 연결
        placard.innerHTML = `
            <div>
                <h3>${policy.title}</h3>
                <p>${policy.summary ? policy.summary.substring(0, 40) : ''}...</p>
            </div>
            <span>${policy.genre || '기타'}</span>
        `;
        container.appendChild(placard);
    });
}

// --- Search Handler ---
function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    
    if (!searchTerm) {
        // 검색어 없으면 랜덤 복귀 (혹은 원래 스택 유지)
        return;
    }

    const filteredPolicies = allPolicies.filter(policy => 
        policy.title.toLowerCase().includes(searchTerm) || 
        (policy.summary && policy.summary.toLowerCase().includes(searchTerm))
    );
    
    // 검색 결과로 스택 교체
    currentCardStack = filteredPolicies.slice(0, 10);
    renderCardStack();
}

// --- Modal Utilities ---
function openModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

function openDetailModal(idOrIdString) {
    const policy = allPolicies.find(p => p.id == idOrIdString);
    if (!policy) return;

    document.getElementById('modal-title').innerText = policy.title;
    document.getElementById('modal-period').innerText = `기간: ${policy.period}`;
    document.getElementById('modal-summary').innerText = policy.summary || '내용 없음';
    
    document.getElementById('modal-link-btn').href = policy.link || '#';
    document.getElementById('modal-share-btn').onclick = () => sharePolicy(policy.title, policy.link);
    
    openModal('detail-modal');
}

function sharePolicy(title, link) {
    if (navigator.share) {
        navigator.share({ title: '빙글 정책 추천', text: title, url: link });
    } else {
        alert(`공유하기:\n${title}\n${link}`);
    }
}

// --- Local Storage ---
function getLikedItems() {
    return JSON.parse(localStorage.getItem('likedPolicies') || '[]');
}

function saveLikedItem(id) {
    const items = getLikedItems();
    if (!items.includes(String(id))) {
        items.push(String(id));
        localStorage.setItem('likedPolicies', JSON.stringify(items));
    }
}