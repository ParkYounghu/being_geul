document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    if (path === '/') {
        initSwipePage();
    } else if (path === '/liked') {
        initLikedPage();
    } else if (path === '/analysis') {
        initAnalysisPage();
    } else if (path === '/search') {
        // 검색 페이지는 별도 JS 로직이 현재 필요 없음
    }
});

// --- 스와이프 페이지 로직 (index_01) ---
function initSwipePage() {
    const cardContainer = document.getElementById('card-container');
    if (!cardContainer) return;

    const cards = Array.from(cardContainer.querySelectorAll('.card')).reverse();
    const likeIndicator = document.getElementById('like-indicator');
    const passIndicator = document.getElementById('pass-indicator');
    let activeCard = null;
    let startX = 0, startY = 0;
    let isDragging = false;
    let offsetX = 0, offsetY = 0;

    const updateCardStack = () => {
        cards.forEach((card, index) => {
            if (index < 3) { // 상위 3개 카드만 보이도록
                card.style.transform = `translateY(${index * -10}px) scale(${1 - index * 0.05})`;
                card.style.opacity = 1;
                card.style.zIndex = cards.length - index;
            } else {
                card.style.opacity = 0;
                card.style.pointerEvents = 'none';
            }
        });
    };
    
    const startDrag = (e) => {
        activeCard = e.currentTarget;
        if (!activeCard || cards[cards.length - 1] !== activeCard) return;

        isDragging = true;
        activeCard.classList.add('dragging');
        
        const touch = e.type === 'touchstart' ? e.touches[0] : e;
        startX = touch.clientX;
        startY = touch.clientY;
        
        e.preventDefault();
    };

    const drag = (e) => {
        if (!isDragging || !activeCard) return;

        const touch = e.type === 'touchmove' ? e.touches[0] : e;
        const currentX = touch.clientX;
        
        offsetX = currentX - startX;
        
        const rotation = offsetX / 20;
        activeCard.style.transform = `translateX(${offsetX}px) rotate(${rotation}deg)`;

        const opacity = Math.abs(offsetX) / (window.innerWidth / 4);
        if (offsetX > 0) {
            likeIndicator.style.opacity = opacity;
            passIndicator.style.opacity = 0;
        } else {
            passIndicator.style.opacity = opacity;
            likeIndicator.style.opacity = 0;
        }
    };

    const endDrag = (e) => {
        if (!isDragging || !activeCard) return;
        isDragging = false;
        activeCard.classList.remove('dragging');

        const decisionThreshold = window.innerWidth / 4;

        if (Math.abs(offsetX) > decisionThreshold) {
            const direction = offsetX > 0 ? 1 : -1;
            activeCard.style.transition = 'transform 0.5s ease, opacity 0.5s ease';
            activeCard.style.transform = `translateX(${direction * window.innerWidth}px) rotate(${direction * 30}deg)`;
            activeCard.style.opacity = 0;

            if (direction === 1) { // Like
                saveLikedItem(activeCard.dataset.id);
            }
            
            setTimeout(() => {
                cardContainer.removeChild(activeCard);
                cards.pop();
                updateCardStack();
            }, 500);

        } else { // 원래 위치로 복귀
            activeCard.style.transition = 'transform 0.4s ease';
            activeCard.style.transform = '';
        }
        
        likeIndicator.style.opacity = 0;
        passIndicator.style.opacity = 0;
        offsetX = 0;
    };
    
    const handleCardClick = (e) => {
        if (isDragging && Math.abs(offsetX) > 5) return; // 드래그 중에는 클릭 무시
        
        const link = e.currentTarget.dataset.link;
        if (link) {
            window.open(link, '_blank');
        }
    };

    cards.forEach(card => {
        card.addEventListener('mousedown', startDrag);
        card.addEventListener('touchstart', startDrag, { passive: false });
        card.addEventListener('click', handleCardClick);
    });

    document.addEventListener('mousemove', drag);
    document.addEventListener('touchmove', drag, { passive: false });
    
    document.addEventListener('mouseup', endDrag);
    document.addEventListener('touchend', endDrag);
    
    updateCardStack();
}

// --- '좋아요' 저장 및 조회 로직 ---
function getLikedItems() {
    return JSON.parse(localStorage.getItem('likedPolicies') || '[]');
}

function saveLikedItem(id) {
    const likedItems = getLikedItems();
    if (!likedItems.includes(id)) {
        likedItems.push(id);
        localStorage.setItem('likedPolicies', JSON.stringify(likedItems));
        console.log(`Liked: ${id}`);
    }
}

// --- '좋아요' 페이지 로직 (index_02) ---
function initLikedPage() {
    const likedGrid = document.getElementById('liked-grid');
    if (!likedGrid) return;
    
    const likedIds = getLikedItems();
    const allItems = Array.from(likedGrid.querySelectorAll('.grid-item'));

    allItems.forEach(item => {
        const id = item.dataset.id;
        if (likedIds.includes(id)) {
            item.style.display = 'block';
        }
    });
}

// --- 분석 페이지 로직 (index_03) ---
function initAnalysisPage() {
    const analysisResults = document.getElementById('analysis-results');
    if (!analysisResults) return;

    const likedIds = getLikedItems();
    if (likedIds.length === 0) {
        analysisResults.innerHTML = "<p>아직 '좋아요'한 정책이 없습니다.</p>";
        return;
    }

    // 서버에서 전달된 전체 정책 데이터에서 장르 정보 추출
    const policies = [];
     // index_03.html 템플릿에 전체 policy 데이터가 없으므로, 
     // 다른 페이지(예: /search)의 데이터를 참조하는 방식으로 구현해야 함.
     // 여기서는 임시로 document에서 데이터를 읽어오는 것으로 가정합니다.
    document.querySelectorAll('.grid-item, .card').forEach(el => {
        const id = el.dataset.id;
        // 중복 방지
        if (!policies.find(p => p.id === id)) {
            policies.push({
                id: el.dataset.id,
                genre: el.dataset.genre || '기타' // genre 데이터가 없을 경우
            });
        }
    });
    
    const likedPolicies = policies.filter(p => likedIds.includes(p.id));
    
    const genreCounts = likedPolicies.reduce((acc, policy) => {
        const genre = policy.genre;
        acc[genre] = (acc[genre] || 0) + 1;
        return acc;
    }, {});

    const totalLiked = likedPolicies.length;
    const sortedGenres = Object.entries(genreCounts).sort(([,a],[,b]) => b-a);
    
    analysisResults.innerHTML = ''; // 기존 내용 초기화

    sortedGenres.forEach(([genre, count]) => {
        const percentage = ((count / totalLiked) * 100).toFixed(1);
        const statElement = document.createElement('div');
        statElement.classList.add('genre-stat');
        
        statElement.innerHTML = `
            <div class="genre-name">${genre}</div>
            <div class="genre-bar-container">
                <div class="genre-bar" style="width: 0%;"></div>
            </div>
            <div class="genre-percentage">${percentage}%</div>
        `;
        analysisResults.appendChild(statElement);

        // 애니메이션 효과를 위해 약간의 지연 후 너비 설정
        setTimeout(() => {
            statElement.querySelector('.genre-bar').style.width = `${percentage}%`;
        }, 100);
    });
}