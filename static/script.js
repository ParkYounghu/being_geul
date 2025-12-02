// --- Global State ---
window.allPolicies = window.allPolicies || [];
let currentCardStack = [];
let lastSwiped = [];
let likeCount = 0;
let likedDataForAI = { titles: [], genres: [] };
let deletedHistory = [];
let availablePolicies = [];

// [핵심 1] DB의 '긴 장르명' -> 실제 '폴더 이름(짧은거)' 매핑
const folderMapping = {
    // 사용자가 알려준 DB 항목
    '금융/자산': '금융',
    '취업/창업': '취업',
    '주거/생활': '주거',
    '교육/역량': '교육',
    '복지/건강': '복지',
    '참여/권리': '참여',
    
    // 예외 처리 (짧은 이름 대비)
    '금융': '금융',
    '취업': '취업', '창업': '취업', '일자리': '취업',
    '주거': '주거',
    '교육': '교육', '기술': '교육',
    '복지': '복지', '건강': '복지',
    '참여': '참여', '권리': '참여',
    '기타': '복지'
};

const genreColors = { 
    // DB 장르별 색상 지정
    '금융/자산': '#2E7D32', '취업/창업': '#F9A825', '주거/생활': '#1565C0',
    '교육/역량': '#009688', '복지/건강': '#EC407A', '참여/권리': '#AB47BC',
    
    // 폴더명(짧은거) 기준 색상 (Fallback)
    '금융': '#2E7D32', '주거': '#1565C0', '취업': '#F9A825',
    '교육': '#009688', '복지': '#EC407A', '참여': '#AB47BC', '기타': '#455A64'
};

// 랜덤 색상 팔레트
const colorPalette = ['#E57373', '#81C784', '#64B5F6', '#FFD54F', '#9575CD', '#A1887F', '#B0BEC5'];
let colorIndex = 0;

function getUniqueGenres() {
    if (!window.allPolicies || window.allPolicies.length === 0) return ['금융/자산', '주거/생활', '취업/창업', '교육/역량', '복지/건강', '참여/권리'];
    return [...new Set(window.allPolicies.map(p => p.genre || '기타'))].sort();
}

function getGenreColor(genre) {
    if (genreColors[genre]) return genreColors[genre];
    // 매핑된 짧은 이름으로도 색상 찾아보기
    const shortName = folderMapping[genre];
    if (shortName && genreColors[shortName]) return genreColors[shortName];
    
    // 그래도 없으면 랜덤
    if (!genreColors[genre]) { genreColors[genre] = colorPalette[colorIndex % colorPalette.length]; colorIndex++; }
    return genreColors[genre];
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('card-container')) initMainPage();
    else if (document.getElementById('mypage-container')) initMyPage();
});

// --- Main Page Logic ---
function initMainPage() {
    setupMainEventListeners();
    setupKeyboardNavigation();
    updateMainHeader();
    
    const savedImg = localStorage.getItem('myTypeImage');
    const savedNick = localStorage.getItem('myTypeNickname');
    
    if (savedImg && document.getElementById('ai-nickname-display')) {
        showResultImage(savedImg);
        if (savedNick) showNickname(savedNick);
    }

    if (window.allPolicies && window.allPolicies.length > 0) {
        // [중요] 카드를 랜덤하게 섞어서 보여줌
        availablePolicies = [...window.allPolicies].sort(() => 0.5 - Math.random());
    } else {
        console.warn("데이터가 로드되지 않았습니다.");
    }
    loadMoreCards();
    
    const canvas = document.getElementById('main-hexagon-chart');
    if (canvas) { canvas.width = 280; canvas.height = 280; renderHexagonChart('main-hexagon-chart'); }
}

function setupMainEventListeners() {
    const loginBtnLanding = document.getElementById('login-btn-landing');
    if(loginBtnLanding) loginBtnLanding.addEventListener('click', () => openModal('login-modal'));

    const browseBtn = document.getElementById('browse-btn-landing');
    if(browseBtn) {
        browseBtn.addEventListener('click', () => document.getElementById('main-section').scrollIntoView({ behavior: 'smooth' }));
    }

    document.getElementById('undo-btn')?.addEventListener('click', undoLastSwipe);
    document.getElementById('load-more-btn')?.addEventListener('click', loadMoreCards);
    document.getElementById('main-search-input')?.addEventListener('input', handleSearch);
    document.getElementById('login-btn-modal')?.addEventListener('click', handleLogin);
}

function setupKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        if (document.querySelector('.modal-overlay.hidden')) {
            if (e.key === 'ArrowRight') swipeTopCard('right');
            else if (e.key === 'ArrowLeft') swipeTopCard('left');
        }
    });
}

function updateMainHeader() {
    const container = document.querySelector('.top-right-buttons');
    if (!container) return;
    container.innerHTML = '';
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';

    if (isLoggedIn) {
        const myPageBtn = document.createElement('button');
        myPageBtn.innerText = "마이페이지";
        myPageBtn.onclick = () => location.href = 'mypage.html';
        const logoutBtn = document.createElement('button');
        logoutBtn.innerText = "로그아웃";
        logoutBtn.onclick = () => { localStorage.setItem('isLoggedIn', 'false'); alert('로그아웃'); location.href = '/'; };
        container.appendChild(myPageBtn); container.appendChild(logoutBtn);
    } else {
        const loginBtn = document.createElement('button');
        loginBtn.innerText = "로그인";
        loginBtn.onclick = () => openModal('login-modal');
        container.appendChild(loginBtn);
    }
}

function handleLogin() {
    if (document.getElementById('login-id').value === '123123') {
        localStorage.setItem('isLoggedIn', 'true');
        closeModal('login-modal');
        updateMainHeader();
        alert('로그인 성공!');
        document.getElementById('main-section').scrollIntoView({ behavior: 'smooth' });
    } else alert('실패 (Hint: 123123)');
}

// --- Card Logic ---
function loadMoreCards() {
    if (availablePolicies.length === 0) {
        if (window.allPolicies.length > 0 && currentCardStack.length === 0) {
             alert("모든 정책 카드를 확인하셨습니다!");
        }
        document.getElementById('load-more-btn').style.display = 'none';
        return;
    }
    const newCards = availablePolicies.splice(0, 10);
    currentCardStack = [...currentCardStack, ...newCards];
    renderCardStack();
    if (availablePolicies.length === 0) document.getElementById('load-more-btn').style.display = 'none';
}

function renderCardStack() {
    const container = document.getElementById('card-container');
    if(!container) return;
    container.innerHTML = '';
    [...currentCardStack].reverse().forEach(p => container.appendChild(createCardElement(p)));
    if (currentCardStack.length === 0 && availablePolicies.length > 0) document.getElementById('load-more-btn').style.display = 'block';
}

// [핵심 수정] 카드 이미지 생성 로직
function createCardElement(policy) {
    const card = document.createElement('div');
    card.className = 'card';
    card.dataset.id = policy.id;
    
    // 1. DB의 긴 장르명 (예: "금융/자산")
    const rawGenre = policy.genre || '기타';
    // 2. 실제 폴더 이름으로 변환 (예: "금융")
    const mappedGenre = folderMapping[rawGenre] || '복지'; 
    const bg = getGenreColor(rawGenre);
    
    // 3. 카드 대표 이미지 경로 설정
    // 규칙: "1[폴더명]/[폴더명]_[폴더명].png" (예: /images/1금융/금융_금융.png)
    // ※ 주의: 폴더 안에 이 파일이 있어야 이미지가 뜹니다. 없으면 handleImageError가 확장자를 바꿔가며 찾습니다.
    const imgPath = `/images/1${mappedGenre}/${mappedGenre}_${mappedGenre}.png`;

    card.style.background = `linear-gradient(135deg, ${bg} 0%, #111 120%)`;
    card.innerHTML = `
        <div class="card-period">${policy.period}</div>
        <div class="card-content">
            <div class="card-summary">${policy.summary || '내용 없음'}</div>
            <div class="card-title">${policy.title}</div>
            <div class="card-illustration">
                <img src="${imgPath}" alt="${mappedGenre}" onerror="handleImageError(this)">
            </div>
        </div>
    `;
    initCardEvents(card);
    return card;
}

function openDetailModal(id) {
    const p = window.allPolicies.find(x => x.id == id);
    if (!p) return;
    document.getElementById('modal-title').innerText = p.title;
    document.getElementById('modal-period').innerText = p.period;
    document.getElementById('modal-summary').innerText = p.summary;
    document.getElementById('modal-link-btn').href = p.link;
    const shareBtn = document.getElementById('modal-share-btn');
    if(shareBtn) shareBtn.onclick = () => { if (navigator.share) navigator.share({ title: p.title, text: p.summary, url: p.link }); else alert(`[공유]\n${p.title}\n${p.link}`); };
    const notifyBtn = document.getElementById('modal-notify-btn');
    if(notifyBtn) notifyBtn.onclick = () => alert(`'${p.title}' 알림 설정됨! 🔔`);
    openModal('detail-modal');
}

function initMyPage() {
    renderGenreFilters();
    renderPlacardList();
    const savedImg = localStorage.getItem('myTypeImage');
    const imgContainer = document.getElementById('mypage-type-image-container');
    if (savedImg && imgContainer) {
        imgContainer.innerHTML = `
            <img src="${savedImg}" 
                 style="max-width:300px; width:100%; border-radius:15px; box-shadow: 0 10px 20px rgba(0,0,0,0.3);" 
                 onerror="handleImageError(this)" 
                 alt="나의 정책 유형">
        `;
    }
    setTimeout(() => { const c = document.getElementById('hexagon-chart'); if (c) { c.width = 450; c.height = 450; renderHexagonChart('hexagon-chart'); }}, 300);
}

function deleteLikedItem(id, el) {
    const card = el.closest('.placard-card');
    card.style.transition = 'all 0.3s';
    card.style.opacity = '0';
    setTimeout(() => card.remove(), 300);
    let list = getLikedItems();
    if (list.includes(String(id))) deletedHistory.push(String(id));
    list = list.filter(x => x !== String(id));
    localStorage.setItem('likedPolicies', JSON.stringify(list));
    renderHexagonChart('hexagon-chart');
    updateRestoreButton();
}

function toggleAll(source) {
    const checkboxes = document.querySelectorAll('.card-checkbox:not(#select-all)');
    checkboxes.forEach(cb => cb.checked = source.checked);
}

function deleteSelectedItems() {
    const checkboxes = document.querySelectorAll('.card-checkbox:not(#select-all):checked');
    if (checkboxes.length === 0) { alert("삭제할 항목을 선택해주세요."); return; }
    if (!confirm(`${checkboxes.length}개 항목을 삭제하시겠습니까?`)) return;
    let list = getLikedItems();
    checkboxes.forEach(cb => {
        const id = cb.dataset.id;
        if (list.includes(String(id))) { deletedHistory.push(String(id)); }
        list = list.filter(x => x !== String(id));
        const card = cb.closest('.placard-card');
        if (card) card.remove();
    });
    localStorage.setItem('likedPolicies', JSON.stringify(list));
    renderHexagonChart('hexagon-chart');
    updateRestoreButton();
    document.getElementById('select-all').checked = false;
}

function restoreLastItem() {
    if (deletedHistory.length === 0) return;
    const lastId = deletedHistory.pop();
    saveLikedItem(lastId);
    renderPlacardList();
    renderHexagonChart('hexagon-chart');
    updateRestoreButton();
}

function updateRestoreButton() {
    const btn = document.getElementById('restore-btn');
    if (!btn) return;
    if (deletedHistory.length > 0) { btn.style.display = 'block'; btn.innerText = `↺ 삭제 취소 (${deletedHistory.length})`; } else { btn.style.display = 'none'; }
}

function renderGenreFilters(){ 
    const c=document.querySelector('.genre-filters'); if(!c)return; c.innerHTML=''; 
    const b=document.createElement('button'); b.innerText="전체"; b.style.backgroundColor = "#555"; b.onclick=()=>renderPlacardList(null); c.appendChild(b); 
    getUniqueGenres().forEach(g=>{ 
        const btn=document.createElement('button'); btn.innerText=g; btn.style.backgroundColor = getGenreColor(g); btn.onclick=()=>renderPlacardList(g); c.appendChild(btn); 
    }); 
}

function renderPlacardList(f){ 
    const c=document.getElementById('mypage-results'); if(!c)return; c.innerHTML=''; 
    const ids=getLikedItems(); 
    let l=window.allPolicies.filter(p=>ids.includes(String(p.id))); 
    if(f)l=l.filter(p=>p.genre===f); 
    const selectAll = document.getElementById('select-all');
    if(selectAll) selectAll.checked = false;
    if(!l.length){c.innerHTML="<p style='text-align:center; color:#666;'>저장된 정책이 없습니다.</p>";return;} 
    l.forEach(p=>{ 
        const d=document.createElement('div'); d.className='placard-card'; 
        d.innerHTML=`<input type="checkbox" class="card-checkbox" data-id="${p.id}" onclick="event.stopPropagation()">
            <div class="info-area" onclick="openDetailModal('${p.id}')"><h3>${p.title}</h3><p style="font-size:0.8rem; color:#888;">${p.genre}</p></div>
            <button class="delete-btn" onclick="deleteLikedItem('${p.id}',this); event.stopPropagation();">삭제</button>`; 
        c.appendChild(d); 
    }); 
}

function initCardEvents(card) {
    let startX = 0, startY = 0, isDragging = false;
    const onStart = (e) => { isDragging = true; startX = e.clientX||e.touches[0].clientX; startY = e.clientY||e.touches[0].clientY; card.style.transition = 'none'; };
    const onMove = (e) => {
        if (!isDragging) return;
        const x = (e.clientX||e.touches[0].clientX) - startX;
        card.style.transform = `translateX(${x}px) rotate(${x/20}deg)`;
        const op = Math.min(Math.abs(x)/100, 1);
        if(x<0) { if(document.getElementById('like-indicator')) document.getElementById('like-indicator').style.opacity=op; if(document.getElementById('pass-indicator')) document.getElementById('pass-indicator').style.opacity=0; }
        else { if(document.getElementById('pass-indicator')) document.getElementById('pass-indicator').style.opacity=op; if(document.getElementById('like-indicator')) document.getElementById('like-indicator').style.opacity=0; }
    };
    const onEnd = (e) => {
        if (!isDragging) return; isDragging = false;
        const x = (e.clientX||e.changedTouches[0].clientX) - startX;
        const y = (e.clientY||e.changedTouches[0].clientY) - startY;
        if(Math.sqrt(x*x+y*y)<10) { openDetailModal(card.dataset.id); card.style.transform=''; return; }
        if(Math.abs(x)>100) completeSwipe(card, x>0?1:-1);
        else { card.style.transition='0.3s'; card.style.transform=''; document.getElementById('like-indicator').style.opacity=0; document.getElementById('pass-indicator').style.opacity=0; }
    };
    card.addEventListener('mousedown',onStart); document.addEventListener('mousemove',onMove); document.addEventListener('mouseup',onEnd);
    card.addEventListener('touchstart',onStart); document.addEventListener('touchmove',onMove); document.addEventListener('touchend',onEnd);
}
function swipeTopCard(dir) { const c=document.querySelectorAll('.card'); if(c.length) completeSwipe(c[c.length-1], dir==='right'?1:-1); }

function completeSwipe(card, dir) {
    card.style.transition = '0.5s'; card.style.transform = `translateX(${dir*window.innerWidth}px) rotate(${dir*30}deg)`;
    const p = window.allPolicies.find(x => x.id == card.dataset.id);
    lastSwiped.push(p);
    if(dir === -1) {
        saveLikedItem(p.id); likeCount++;
        likedDataForAI.titles.push(p.title); likedDataForAI.genres.push(p.genre);
        if(likeCount === 10) triggerAIAnalysis();
    }
    setTimeout(() => { currentCardStack.shift(); renderCardStack(); document.getElementById('like-indicator').style.opacity=0; document.getElementById('pass-indicator').style.opacity=0; }, 300);
}

// [파일명 & 닉네임 처리]
async function triggerAIAnalysis() {
    alert("🎉 좋아요 10개 달성! 취향 분석 완료.");
    renderHexagonChart('main-hexagon-chart');

    const genreCounts = {};
    likedDataForAI.genres.forEach(g => { genreCounts[g] = (genreCounts[g] || 0) + 1; });
    const sortedGenres = Object.keys(genreCounts).sort((a,b) => genreCounts[b] - genreCounts[a]);
    
    // DB에서 온 원래 이름 (예: '취업/창업')
    const rawFirst = sortedGenres[0] || '기타';
    const rawSecond = sortedGenres[1] || rawFirst;

    console.log(`[DB 결과] 1순위: ${rawFirst}, 2순위: ${rawSecond}`);

    // ★ 폴더 이름 변환 (금융/자산 -> 금융)
    const first = folderMapping[rawFirst] || '복지'; 
    const second = folderMapping[rawSecond] || '복지';

    console.log(`[변환됨] 1순위: ${first}, 2순위: ${second}`);

    // 파일명 규칙: 1순위_2순위.png
    const imagePath = `/images/1${first}/${first}_${second}.png`;
    
    localStorage.setItem('myTypeImage', imagePath);
    showResultImage(imagePath); // 이미지 표시

    try {
        const res = await fetch('/api/generate-nickname', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ liked_titles: likedDataForAI.titles, liked_genres: likedDataForAI.genres })
        });
        const data = await res.json();
        
        if (data.nickname) {
            localStorage.setItem('myTypeNickname', data.nickname);
            showNickname(data.nickname);
        }

    } catch(e) { console.error(e); }
}

function showResultImage(src) {
    const display = document.getElementById('ai-nickname-display');
    if (display) {
        display.innerHTML = `
            <div style="margin-bottom: 10px;">
                <img src="${src}" 
                     style="width: 100%; max-width: 300px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);" 
                     onerror="handleImageError(this)" 
                     alt="취향 분석 결과">
            </div>
            <div id="nickname-placeholder" style="min-height:30px;"></div>
            <div style="font-size: 1.2rem; color: #aaa; margin-top:10px;">당신의 취향 카드</div>
        `;
        display.classList.remove('loading-text'); 
        display.style.border = 'none';
    }
}

function showNickname(nick) {
    const placeholder = document.getElementById('nickname-placeholder');
    if (placeholder) {
        placeholder.innerHTML = `<div style="font-size: 1.5rem; font-weight: bold; color: #FFD54F; margin-top: 10px;">"${nick}"</div>`;
    }
}

function handleImageError(img) {
    if (img.dataset.failed === 'true') return;

    if (img.src.includes('.png')) {
        const newSrc = img.src.replace('.png', '.jpeg');
        if (img.src === newSrc) return;
        
        console.log(`[이미지 재시도] ${img.src} -> ${newSrc}`);
        img.src = newSrc;
        return; 
    }
    
    console.error(`[이미지 로드 실패] 경로: ${img.src}`);
    img.dataset.failed = 'true'; 
    // 이미지 로드 실패 시 숨기기 (에러 메시지 대신)
    img.style.display = 'none';
}

function renderHexagonChart(canvasId) {
    const canvas = document.getElementById(canvasId); if (!canvas) return;
    const ctx = canvas.getContext('2d'); const w = canvas.width, h = canvas.height; ctx.clearRect(0, 0, w, h);
    const genres = getUniqueGenres(); const likedIds = getLikedItems(); const counts = {}; genres.forEach(g=>counts[g]=0);
    likedIds.forEach(id=>{ const p=window.allPolicies.find(x=>x.id==id); if(p) counts[p.genre||'기타']=(counts[p.genre||'기타']||0)+1; });
    const maxVal = Math.max(...Object.values(counts), 1); const size = Math.min(w, h)/2 - 60; const cx = w/2, cy = h/2; const step = (Math.PI*2)/genres.length;
    ctx.strokeStyle = '#555'; ctx.lineWidth=1;
    for(let r=1; r<=3; r++) { ctx.beginPath(); for(let i=0; i<genres.length; i++) { const rad = step*i - Math.PI/2; const x=cx+Math.cos(rad)*(size/3)*r, y=cy+Math.sin(rad)*(size/3)*r; i===0?ctx.moveTo(x,y):ctx.lineTo(x,y); } ctx.closePath(); ctx.stroke(); }
    ctx.beginPath(); genres.forEach((g,i)=>{ const rad = step*i - Math.PI/2; const val = (counts[g]/maxVal)*size; const x=cx+Math.cos(rad)*val, y=cy+Math.sin(rad)*val; i===0?ctx.moveTo(x,y):ctx.lineTo(x,y); });
    ctx.closePath(); ctx.fillStyle='rgba(76,175,80,0.6)'; ctx.fill(); ctx.strokeStyle='#4CAF50'; ctx.lineWidth=3; ctx.stroke();
    ctx.fillStyle='#ddd'; ctx.font='bold 14px sans-serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
    genres.forEach((g,i)=>{ const rad = step*i - Math.PI/2; const x=cx+Math.cos(rad)*(size+35), y=cy+Math.sin(rad)*(size+35); ctx.fillText(g, x, y); });
}
function undoLastSwipe(){ if(lastSwiped.length){ currentCardStack.unshift(lastSwiped.pop()); renderCardStack(); } }
function handleSearch(e){ const t=e.target.value.toLowerCase(); currentCardStack=window.allPolicies.filter(p=>p.title.toLowerCase().includes(t)).slice(0,10); renderCardStack(); }
function openModal(id){ document.getElementById(id)?.classList.remove('hidden'); }
function closeModal(id){ document.getElementById(id)?.classList.add('hidden'); }
function getLikedItems(){ return JSON.parse(localStorage.getItem('likedPolicies')||'[]'); }
function saveLikedItem(id){ const l=getLikedItems(); if(!l.includes(String(id))){ l.push(String(id)); localStorage.setItem('likedPolicies',JSON.stringify(l)); } }