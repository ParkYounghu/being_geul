document.addEventListener('DOMContentLoaded', () => {
    init();
});

// --- 전역 변수 ---
let cards = [];
let activeCard = null;
let swipedHistory = [];

function init() {
    // 페이지 초기화
    buildCardStack(allPolicies);
    initLikedPage();
    initSearchPage();
    initAnalysisPage();

    // 이벤트 리스너 설정
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filteredPolicies = allPolicies.filter(p => 
            p.title.toLowerCase().includes(query) || 
            p.summary.toLowerCase().includes(query)
        );
        buildCardStack(filteredPolicies);
    });

    const undoButton = document.getElementById('undo-button');
    undoButton.addEventListener('click', undoLastSwipe);

    // Modal listeners
    const modal = document.getElementById('modal');
    const closeButton = document.querySelector('.close-button');
    closeButton.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });
}

function switchTab(targetId) {
    const pages = document.querySelectorAll('.page');
    const navLinks = document.querySelectorAll('nav a');

    gsap.to(pages, {
        duration: 0.3,
        opacity: 0,
        onComplete: () => {
            pages.forEach(page => page.style.display = 'none');
            const targetPage = document.getElementById(targetId);
            if (targetPage) {
                targetPage.style.display = 'flex';
                gsap.to(targetPage, { duration: 0.3, opacity: 1 });
            }

            navLinks.forEach(link => {
                link.classList.toggle('active', link.getAttribute('onclick').includes(targetId));
            });
            
            // 데이터 새로고침
            if (targetId === 'section-liked') initLikedPage();
            if (targetId === 'section-analysis') initAnalysisPage();
        }
    });
}

// --- 카드 스택 생성 ---
function buildCardStack(policies) {
    const cardContainer = document.getElementById('card-container');
    cardContainer.innerHTML = '';
    cards = [];

    // 역순으로 배열에 추가하여 렌더링 순서를 제어
    policies.forEach(policy => {
        const cardEl = document.createElement('div');
        cardEl.className = 'card';
        cardEl.dataset.id = policy.id;
        cardEl.dataset.link = policy.link;
        cardEl.dataset.genre = policy.genre;
        cardEl.innerHTML = `
            <h2>${policy.title}</h2>
            <p>${policy.summary}</p>
            <span>기간: ${policy.period}</span>
        `;
        cards.unshift(cardEl); // 배열의 맨 앞에 추가
    });

    cards.forEach(card => {
        cardContainer.appendChild(card);
    });

    initSwipePage();
}


// --- 스와이프 로직 ---
function initSwipePage() {
    if (!cards.length) return;
    
    const likeIndicator = document.getElementById('like-indicator');
    const passIndicator = document.getElementById('pass-indicator');
    
    let startX = 0, isDragging = false, offsetX = 0, isClickAllowed = true, isTransitioning = false;

    const updateCardStack = () => {
        cards.forEach((card, index) => {
            if (index < 3) {
                card.style.transform = `translateY(${index * -10}px) scale(${1 - index * 0.05})`;
                card.style.opacity = 1;
                card.style.zIndex = cards.length - index;
                card.style.display = 'flex';
            } else {
                card.style.opacity = 0;
                card.style.display = 'none';
            }
        });
    };
    
    const startDrag = (e) => {
        if (isTransitioning) return;
        activeCard = e.currentTarget;
        if (cards[0] !== activeCard) return;

        isDragging = true;
        isClickAllowed = true;
        activeCard.classList.add('dragging');
        startX = (e.type === 'touchstart' ? e.touches[0] : e).clientX;
    };

    const drag = (e) => {
        if (!isDragging || !activeCard) return;
        if(e.cancelable) e.preventDefault();
        
        offsetX = (e.type === 'touchmove' ? e.touches[0] : e).clientX - startX;
        if (Math.abs(offsetX) > 5) isClickAllowed = false;
        
        activeCard.style.transform = `translateX(${offsetX}px) rotate(${offsetX / 20}deg)`;

        const opacity = Math.min(Math.abs(offsetX) / (window.innerWidth / 4), 1);

        // SWAPPED: LIKE on left, PASS on right
        if (offsetX < 0) { // LEFT -> LIKE
            likeIndicator.style.opacity = opacity;
            passIndicator.style.opacity = 0;
        } else { // RIGHT -> PASS
            passIndicator.style.opacity = opacity;
            likeIndicator.style.opacity = 0;
        }
    };

    const endDrag = () => {
        if (!isDragging || !activeCard) return;
        isDragging = false;
        activeCard.classList.remove('dragging');

        const decisionThreshold = window.innerWidth / 4;

        if (Math.abs(offsetX) > decisionThreshold) {
            isTransitioning = true;
            const direction = offsetX > 0 ? 1 : -1; // 1 for right (PASS), -1 for left (LIKE)

            const policyId = activeCard.dataset.id;
            const swipedPolicy = allPolicies.find(p => p.id == policyId);
            swipedHistory.push(swipedPolicy);

            gsap.to(activeCard, {
                x: direction * window.innerWidth,
                rotation: direction * 30,
                opacity: 0,
                duration: 0.5,
                onComplete: () => {
                    cards.shift();
                    activeCard.remove();
                    updateCardStack();
                    isTransitioning = false;
                }
            });

            // SWAPPED: Save on LEFT swipe
            if (direction === -1) { // LIKE
                saveLikedItem(policyId);
            }
        } else {
            gsap.to(activeCard, { x: 0, y: 0, rotation: 0, duration: 0.4, ease: 'power3.out' });
        }
        likeIndicator.style.opacity = 0;
        passIndicator.style.opacity = 0;
        offsetX = 0;
    };
    
    const handleCardClick = (e) => {
        if (!isClickAllowed) return;
        const policyId = e.currentTarget.dataset.id;
        const policy = allPolicies.find(p => p.id == policyId);
        openModal(policy);
    };

    cards.forEach(card => {
        card.removeEventListener('mousedown', startDrag);
        card.removeEventListener('touchstart', startDrag);
        card.removeEventListener('click', handleCardClick);

        card.addEventListener('mousedown', startDrag);
        card.addEventListener('touchstart', startDrag, { passive: false });
        card.addEventListener('click', handleCardClick);
    });

    document.removeEventListener('mousemove', drag);
    document.removeEventListener('touchmove', drag);
    document.removeEventListener('mouseup', endDrag);
    document.removeEventListener('touchend', endDrag);

    document.addEventListener('mousemove', drag);
    document.addEventListener('touchmove', drag, { passive: false });
    document.addEventListener('mouseup', endDrag);
    document.addEventListener('touchend', endDrag);
    
    updateCardStack();
}

function undoLastSwipe() {
    if (swipedHistory.length === 0) return;
    const lastSwipedPolicy = swipedHistory.pop();
    
    // Check if card is already on screen
    const isAlreadyVisible = cards.some(cardEl => cardEl.dataset.id == lastSwipedPolicy.id);
    if(isAlreadyVisible) return;

    // Remove from liked if it was a like
    const likedItems = getLikedItems();
    if(likedItems.includes(String(lastSwipedPolicy.id))){
        removeLikedItem(String(lastSwipedPolicy.id));
    }
    
    // Recreate and add card to the top
    const cardContainer = document.getElementById('card-container');
    const cardEl = document.createElement('div');
    cardEl.className = 'card';
    cardEl.dataset.id = lastSwipedPolicy.id;
    cardEl.dataset.link = lastSwipedPolicy.link;
    cardEl.dataset.genre = lastSwipedPolicy.genre;
    cardEl.innerHTML = `
        <h2>${lastSwipedPolicy.title}</h2>
        <p>${lastSwipedPolicy.summary}</p>
        <span>기간: ${lastSwipedPolicy.period}</span>
    `;

    cards.unshift(cardEl);
    cardContainer.appendChild(cardEl);
    initSwipePage();
}


// --- Modal 로직 ---
function openModal(policy) {
    if (!policy) return;
    document.getElementById('modal-title').innerText = policy.title;
    document.getElementById('modal-summary').innerText = policy.summary;
    document.getElementById('modal-period').innerText = `기간: ${policy.period}`;
    document.getElementById('modal-link-button').href = policy.link;

    const shareButton = document.getElementById('modal-share-button');
    shareButton.onclick = () => {
        if (navigator.share) {
            navigator.share({
                title: policy.title,
                text: policy.summary,
                url: policy.link,
            });
        } else {
            alert('이 브라우저에서는 공유 기능을 지원하지 않습니다.');
        }
    };
    
    document.getElementById('modal').style.display = 'flex';
}


// --- '좋아요' 저장, 조회, 삭제 ---
function getLikedItems() {
    return JSON.parse(localStorage.getItem('likedPolicies') || '[]');
}

function saveLikedItem(id) {
    if (!id) return;
    const likedItems = getLikedItems();
    if (!likedItems.includes(id)) {
        likedItems.push(id);
        localStorage.setItem('likedPolicies', JSON.stringify(likedItems));
    }
}

function removeLikedItem(id) {
    let likedItems = getLikedItems();
    likedItems = likedItems.filter(itemId => itemId !== id);
    localStorage.setItem('likedPolicies', JSON.stringify(likedItems));
}


// --- 페이지 컨텐츠 생성 ---
function initLikedPage() {
    const likedGrid = document.getElementById('liked-grid');
    if (!likedGrid) return;
    
    const likedIds = getLikedItems();
    const likedPolicies = allPolicies.filter(p => likedIds.includes(String(p.id)));
    
    likedGrid.innerHTML = '';
    likedPolicies.forEach(policy => {
        const item = document.createElement('div');
        item.className = 'grid-item';
        item.innerHTML = `
            <a href="${policy.link}" target="_blank">
                <h2>${policy.title}</h2>
                <p>${policy.summary}</p>
                <span>기간: ${policy.period}</span>
            </a>`;
        likedGrid.appendChild(item);
    });
}

function initSearchPage() {
    const searchGrid = document.getElementById('search-grid');
    if (!searchGrid) return;
    
    searchGrid.innerHTML = '';
    allPolicies.forEach(policy => {
        const item = document.createElement('div');
        item.className = 'grid-item';
        item.innerHTML = `
            <a href="${policy.link}" target="_blank">
                <h2>${policy.title}</h2>
                <p>${policy.summary}</p>
                <span>기간: ${policy.period}</span>
            </a>`;
        searchGrid.appendChild(item);
    });
}

function initAnalysisPage() {
    const analysisResults = document.getElementById('analysis-results');
    if (!analysisResults) return;

    const likedIds = getLikedItems();
    if (likedIds.length === 0) {
        analysisResults.innerHTML = "<p>아직 '좋아요'한 정책이 없습니다.</p>";
        return;
    }
    
    const likedPolicies = allPolicies.filter(p => likedIds.includes(String(p.id)));
    
    const genreCounts = likedPolicies.reduce((acc, policy) => {
        const genre = policy.genre || '기타';
        acc[genre] = (acc[genre] || 0) + 1;
        return acc;
    }, {});

    const totalLiked = likedPolicies.length;
    const sortedGenres = Object.entries(genreCounts).sort(([,a],[,b]) => b-a);
    
    analysisResults.innerHTML = ''; 
    sortedGenres.forEach(([genre, count]) => {
        const percentage = ((count / totalLiked) * 100).toFixed(1);
        const statElement = document.createElement('div');
        statElement.className = 'genre-stat';
        statElement.innerHTML = `
            <div class="genre-name">${genre}</div>
            <div class="genre-bar-container">
                <div class="genre-bar" style="width: 0%;"></div>
            </div>
            <div class="genre-percentage">${percentage}%</div>
        `;
        analysisResults.appendChild(statElement);

        setTimeout(() => {
            statElement.querySelector('.genre-bar').style.width = `${percentage}%`;
        }, 100);
    });
}