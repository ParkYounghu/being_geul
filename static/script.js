// --- Global State ---
// window.allPolicies는 HTML에서 로드됨
let currentCardStack = [];
let lastSwiped = [];
let isLoggedIn = false;
let currentSection = 'landing-section';

// --- Genre Colors ---
const genreColors = {
    '금융': '#2E7D32',
    '주거': '#1565C0',
    '창업': '#F9A825',
    '인력': '#C62828',
    '기술': '#6A1B9A',
    '기타': '#455A64',
};

const colorPalette = ['#E57373', '#81C784', '#64B5F6', '#FFD54F', '#9575CD', '#A1887F', '#B0BEC5'];
let colorIndex = 0;

function getGenreColor(genre) {
    if (genreColors[genre]) {
        return genreColors[genre];
    }
    // Assign a new color if not in the predefined map
    if (!genreColors[genre]) {
        genreColors[genre] = colorPalette[colorIndex % colorPalette.length];
        colorIndex++;
    }
    return genreColors[genre];
}

// --- Initializer ---
document.addEventListener('DOMContentLoaded', () => {
    if (typeof window.allPolicies !== 'undefined') {
        console.log("Data loaded:", window.allPolicies.length);
    } else {
        console.error("Policy data not found.");
        window.allPolicies = [];
    }
    
    setupEventListeners();
    setupKeyboardNavigation(); // [NEW] 키보드 이벤트
    switchSection('landing-section');
});

// --- Event Listeners ---
function setupEventListeners() {
    // 1. Landing Page
    document.getElementById('login-btn-landing').addEventListener('click', () => openModal('login-modal'));
    document.getElementById('signup-btn-landing').addEventListener('click', () => alert('회원가입 기능은 준비 중입니다.'));
    
    // [FIX] 둘러보기 버튼 기능 복구
    document.getElementById('browse-btn-landing').addEventListener('click', () => {
        isLoggedIn = false;
        switchSection('main-section');
    });

    // 2. Main Page
    document.getElementById('undo-btn').addEventListener('click', undoLastSwipe);
    document.getElementById('load-more-btn').addEventListener('click', loadMoreCards);
    document.getElementById('main-search-input').addEventListener('input', handleSearch);

    // 3. Login Modal Logic [NEW]
    document.getElementById('login-btn-modal').addEventListener('click', handleLogin);
    
    // 4. Side Buttons (Static) [NEW]
    // 초기화 시점에는 이벤트가 없지만, updateSideButtons에서 매번 갱신됨
}

function setupKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        // 메인 섹션이 활성화되어 있고, 모달이 닫혀있을 때만 작동
        if (currentSection === 'main-section' && document.querySelector('.modal-overlay.hidden')) {
            if (e.key === 'ArrowRight') { // SWAPPED
                swipeTopCard('left'); // PASS
            } else if (e.key === 'ArrowLeft') { // SWAPPED
                swipeTopCard('right'); // LIKE
            }
        }
    });
}

// --- Login Logic ---
function handleLogin() {
    const idField = document.getElementById('login-id');
    const pwField = document.getElementById('login-pw');
    
    if (idField.value === '123123' && pwField.value === '123123') {
        alert('로그인 성공!');
        isLoggedIn = true;
        closeModal('login-modal');
        switchSection('main-section');
    } else {
        alert('아이디 또는 비밀번호가 일치하지 않습니다.\n(Hint: 123123)');
    }
}

function logout() {
    isLoggedIn = false;
    alert('로그아웃 되었습니다.');
    updateMainHeader();
    switchSection('landing-section');
}

// --- Section & Header ---
function switchSection(sectionId) {
    const outgoing = document.querySelector('.page-section.active');
    const incoming = document.getElementById(sectionId);

    if (outgoing && outgoing !== incoming) {
        gsap.to(outgoing, { duration: 0.3, autoAlpha: 0, display: "none", onComplete: () => outgoing.classList.remove('active') });
    }
    
    currentSection = sectionId;
    
    if (sectionId === 'main-section') {
        renderMainPage();
    } else if (sectionId === 'mypage-section') {
        renderMyPage();
    }
    
    if (incoming) {
        incoming.classList.add('active');
        const displayType = sectionId === 'landing-section' ? 'flex' : 'block';
        gsap.to(incoming, { duration: 0.3, autoAlpha: 1, display: displayType });
    }
}

function updateMainHeader() {
    const container = document.querySelector('.top-right-buttons');
    container.innerHTML = '';
    
    if (isLoggedIn) {
        const myPageBtn = document.createElement('button');
        myPageBtn.innerText = "마이페이지";
        myPageBtn.onclick = () => switchSection('mypage-section');
        
        const logoutBtn = document.createElement('button');
        logoutBtn.innerText = "로그아웃";
        logoutBtn.onclick = logout;
        
        container.appendChild(myPageBtn);
        container.appendChild(logoutBtn);
    } else {
        const loginBtn = document.createElement('button');
        loginBtn.innerText = "로그인";
        loginBtn.onclick = () => openModal('login-modal');
        
        container.appendChild(loginBtn);
    }
}

// --- Main Page (Cards) ---
function renderMainPage() {
    updateMainHeader();
    if (currentCardStack.length === 0) loadMoreCards();
    else renderCardStack();
}

function getRandomPolicies(count) {
    const shuffled = [...window.allPolicies].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
}

function loadMoreCards() {
    const newCards = getRandomPolicies(10);
    currentCardStack = [...currentCardStack, ...newCards];
    renderCardStack();
    document.getElementById('load-more-btn').style.display = 'none';
}

function renderCardStack() {
    const container = document.getElementById('card-container');
    container.innerHTML = '';
    
    // 렌더링 (역순 배치)
    const renderList = [...currentCardStack].reverse();
    renderList.forEach((policy) => {
        const card = createCardElement(policy);
        container.appendChild(card);
    });

    // [NEW] 사이드 버튼 업데이트 (맨 위 카드 기준)
    if (currentCardStack.length > 0) {
        updateSideButtons(currentCardStack[0]);
    } else {
        document.getElementById('load-more-btn').style.display = 'block';
    }
}

function createCardElement(policy) {
    const card = document.createElement('div');
    card.className = 'card';
    card.dataset.id = policy.id;
    
    const bgColor = getGenreColor(policy.genre || '기타');
    card.style.background = `linear-gradient(135deg, ${bgColor} 0%, #1a1a1a 120%)`;

    card.innerHTML = `
        <div class="card-content">
            <div class="card-summary">${policy.summary || '내용 없음'}</div>
            <div class="card-title">${policy.title}</div>
            <div class="card-illustration">🖼️</div>
            <div class="card-period">${policy.period}</div>
        </div>
    `;
    
    // 카드 내용 클릭 시 상세 모달 (드래그와 구분은 initCardEvents에서 처리)
    initCardEvents(card);
    return card;
}

// [NEW] 사이드 버튼 업데이트 함수
function updateSideButtons(policy) {
    const btnView = document.getElementById('btn-view-original');
    const btnShare = document.getElementById('btn-share');
    const btnNotify = document.getElementById('btn-notify');
    
    if (!policy) return;

    btnView.onclick = () => window.open(policy.link, '_blank');
    btnShare.onclick = () => sharePolicy(policy.title, policy.link);
    btnNotify.onclick = () => alert(`'${policy.title}' 알림 설정됨!`);
}

// [FIX] 드래그 vs 클릭 구분 & 스와이프 로직
function initCardEvents(card) {
    let startX = 0;
    let startY = 0; // 세로 스크롤 허용 위해 체크 가능
    let isDragging = false;
    
    const onStart = (e) => {
        isDragging = true;
        startX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
        startY = e.type === 'touchstart' ? e.touches[0].clientY : e.clientY;
        card.style.transition = 'none'; 
    };

    const onMove = (e) => {
        if (!isDragging) return;
        const currentX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
        const offsetX = currentX - startX;
        
        // 회전 및 이동 효과
        card.style.transform = `translateX(${offsetX}px) rotate(${offsetX / 20}deg)`;

        // 인디케이터
        const likeInd = document.getElementById('like-indicator');
        const passInd = document.getElementById('pass-indicator');
        const opacity = Math.min(Math.abs(offsetX) / 100, 1);
        
        if (offsetX < 0) { // Dragging LEFT
            if(likeInd) likeInd.style.opacity = opacity; // Show LIKE
            if(passInd) passInd.style.opacity = 0;
        } else { // Dragging RIGHT
            if(passInd) passInd.style.opacity = opacity; // Show PASS
            if(likeInd) likeInd.style.opacity = 0;
        }
    };

    const onEnd = (e) => {
        if (!isDragging) return;
        isDragging = false;
        
        const endX = e.type === 'touchend' ? e.changedTouches[0].clientX : e.clientX;
        const endY = e.type === 'touchend' ? e.changedTouches[0].clientY : e.clientY;
        const offsetX = endX - startX;
        const offsetY = endY - startY;

        // [NEW] 드래그 거리 계산 (클릭 판단)
        const moveDist = Math.sqrt(offsetX*offsetX + offsetY*offsetY);
        
        // 이동 거리가 짧으면 클릭으로 간주 -> 상세 모달 열기
        if (moveDist < 10) {
            const policyId = card.dataset.id;
            openDetailModal(policyId);
            // 원위치 리셋
            card.style.transform = 'translateX(0) rotate(0)';
            return;
        }

        const threshold = window.innerWidth / 4; 
        if (Math.abs(offsetX) > threshold) {
            const direction = offsetX > 0 ? 1 : -1;
            completeSwipe(card, direction);
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

// 키보드/마우스 공통 스와이프 처리
function swipeTopCard(direction) {
    const cardContainer = document.getElementById('card-container');
    const cards = cardContainer.querySelectorAll('.card');
    if (cards.length === 0) return;
    
    // DOM상 맨 마지막 요소가 맨 위에 보이는 카드임 (absolute 배치 때문)
    const topCard = cards[cards.length - 1];
    const dirVal = direction === 'right' ? 1 : -1;
    
    completeSwipe(topCard, dirVal);
}

function completeSwipe(card, direction) {
    const winWidth = window.innerWidth;
    card.style.transition = 'transform 0.5s ease';
    card.style.transform = `translateX(${direction * winWidth}px) rotate(${direction * 30}deg)`;
    
    const policyId = card.dataset.id;
    const policyData = window.allPolicies.find(p => p.id == policyId);
    
    lastSwiped.push(policyData);
    if (direction === -1) saveLikedItem(policyId); // SWAPPED: Left swipe is now LIKE

    setTimeout(() => {
        currentCardStack.shift(); // 데이터 배열에서 제거
        renderCardStack();        // 재렌더링 (여기서 updateSideButtons도 호출됨)
        resetIndicators();
    }, 300);
}

function undoLastSwipe() {
    if (lastSwiped.length > 0) {
        const lastPolicy = lastSwiped.pop();
        currentCardStack.unshift(lastPolicy);
        renderCardStack();
    } else {
        alert('되돌릴 카드가 없습니다.');
    }
}

function resetIndicators() {
    const likeInd = document.getElementById('like-indicator');
    const passInd = document.getElementById('pass-indicator');
    if(likeInd) likeInd.style.opacity = 0;
    if(passInd) passInd.style.opacity = 0;
}

// --- My Page Logic ---
function renderMyPage() {
    setTimeout(renderHexagonChart, 100);
    renderGenreFilters();
    renderPlacardList();
}
// (이하 My Page 관련 함수들은 기존과 동일, 생략 없이 작동하도록 유지)
function renderHexagonChart() {
    const canvas = document.getElementById('hexagon-chart');
    if (!canvas) return;
    const container = canvas.parentElement;
    canvas.width = container.offsetWidth;
    canvas.height = container.offsetHeight;
    const ctx = canvas.getContext('2d');
    const size = Math.min(canvas.width, canvas.height) / 2 - 20;
    const centerX = canvas.width / 2, centerY = canvas.height / 2;
    const likedItems = getLikedItems();
    const genreCounts = {};
    const genres = [...new Set(window.allPolicies.map(p => p.genre || '기타'))];
    genres.forEach(g => genreCounts[g] = 0);
    likedItems.forEach(id => {
        const policy = window.allPolicies.find(p => p.id == id);
        if (policy) {
            let g = policy.genre || '기타';
            if (!genres.includes(g)) g = '기타';
            genreCounts[g]++;
        }
    });
    const maxVal = Math.max(...Object.values(genreCounts), 5);
    const angleStep = (Math.PI * 2) / genres.length;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Grid
    ctx.strokeStyle = '#666'; ctx.lineWidth = 1;
    for(let l=1; l<=3; l++) {
        const cs = (size/3)*l; ctx.beginPath();
        for(let i=0; i<genres.length; i++){
            const a = angleStep*i - Math.PI/2;
            const x = centerX + cs*Math.cos(a), y = centerY + cs*Math.sin(a);
            i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
        }
        ctx.closePath(); ctx.stroke();
    }
    // Data
    ctx.beginPath();
    genres.forEach((g, i) => {
        const val = genreCounts[g]/maxVal;
        const a = angleStep*i - Math.PI/2;
        const x = centerX + size*val*Math.cos(a), y = centerY + size*val*Math.sin(a);
        i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
    });
    ctx.closePath(); ctx.fillStyle = 'rgba(76, 175, 80, 0.6)'; ctx.fill(); ctx.strokeStyle = '#4CAF50'; ctx.stroke();
    // Labels
    ctx.fillStyle = '#fff'; ctx.font = '12px Arial'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    genres.forEach((g, i) => {
        const a = angleStep*i - Math.PI/2;
        ctx.fillText(g, centerX+(size+15)*Math.cos(a), centerY+(size+15)*Math.sin(a));
    });
}
function renderGenreFilters() {
    const container = document.querySelector('.genre-filters');
    container.innerHTML = '';
    const allBtn = document.createElement('button');
    allBtn.innerText = "전체"; allBtn.style.backgroundColor = "#555"; allBtn.onclick = () => renderPlacardList(null);
    container.appendChild(allBtn);
    const genres = [...new Set(window.allPolicies.map(p => p.genre || '기타'))];
    genres.forEach(g => {
        const btn = document.createElement('button');
        btn.innerText = g; btn.style.backgroundColor = getGenreColor(g);
        btn.addEventListener('click', () => renderPlacardList(g));
        container.appendChild(btn);
    });
}
function renderPlacardList(filter) {
    const container = document.getElementById('mypage-results');
    container.innerHTML = '';
    const likedIds = getLikedItems();
    let list = window.allPolicies.filter(p => likedIds.includes(String(p.id)));
    if(filter) list = list.filter(p => p.genre === filter);
    if(list.length === 0) { container.innerHTML = "<p style='text-align:center;color:#888;'>데이터 없음</p>"; return; }
    list.forEach(p => {
        const div = document.createElement('div');
        div.className = 'placard-card';
        div.onclick = () => openDetailModal(p.id);
        div.innerHTML = `<div><h3>${p.title}</h3><p>${p.summary?p.summary.substring(0,30):''}...</p></div><span>${p.genre}</span>`;
        container.appendChild(div);
    });
}

// --- Utils ---
function handleSearch(e) {
    const term = e.target.value.toLowerCase();
    if(!term) return;
    const filtered = window.allPolicies.filter(p => p.title.toLowerCase().includes(term));
    currentCardStack = filtered.slice(0, 10);
    renderCardStack();
}
function openModal(id) { document.getElementById(id).classList.remove('hidden'); }
function closeModal(id) { document.getElementById(id).classList.add('hidden'); }
function openDetailModal(id) {
    const p = window.allPolicies.find(x => x.id == id);
    if(!p) return;
    document.getElementById('modal-title').innerText = p.title;
    document.getElementById('modal-period').innerText = p.period;
    document.getElementById('modal-summary').innerText = p.summary;
    document.getElementById('modal-link-btn').href = p.link;
    document.getElementById('modal-share-btn').onclick = () => sharePolicy(p.title, p.link);
    openModal('detail-modal');
}
function sharePolicy(t, l) { navigator.share ? navigator.share({title:t, url:l}) : alert(`${t}\n${l}`); }
function getLikedItems() { return JSON.parse(localStorage.getItem('likedPolicies') || '[]'); }
function saveLikedItem(id) {
    const items = getLikedItems();
    if(!items.includes(String(id))) { items.push(String(id)); localStorage.setItem('likedPolicies', JSON.stringify(items)); }
}