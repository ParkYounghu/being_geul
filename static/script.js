document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    // 경로 확인을 유연하게 변경 (루트 '/' 또는 'index'가 포함된 주소)
    if (path === '/' || path.includes('index')) {
        initSwipePage();
    } else if (path === '/liked') {
        initLikedPage();
    } else if (path === '/analysis') {
        initAnalysisPage();
    }
});

// --- 스와이프 페이지 로직 (index_01) ---
function initSwipePage() {
    const cardContainer = document.getElementById('card-container');
    if (!cardContainer) return;

    // 카드를 배열로 가져오되, 맨 위 카드(사용자가 볼 카드)가 0번 인덱스가 되도록 역순 배열합니다.
    const cards = Array.from(cardContainer.querySelectorAll('.card')).reverse();
    
    const likeIndicator = document.getElementById('like-indicator');
    const passIndicator = document.getElementById('pass-indicator');
    
    let activeCard = null; 
    let startX = 0;
    let isDragging = false; 
    let offsetX = 0;
    
    let isClickAllowed = true; // [FIX] 드래그와 클릭을 구분하는 플래그
    let isTransitioning = false; // [FIX] 애니메이션 중 사용자 입력을 잠그는 플래그 (중간 멈춤 방지)

    // 카드 위치와 스타일을 업데이트하는 핵심 함수
    const updateCardStack = () => {
        cards.forEach((card, index) => {
            if (index < 3) { // 상위 3개 카드만 보이도록
                card.style.transform = `translateY(${index * -10}px) scale(${1 - index * 0.05})`;
                card.style.opacity = 1;
                card.style.zIndex = cards.length - index;
                card.style.display = 'block'; 
                card.style.transition = 'none'; // 위치 재설정 시 애니메이션 비활성화
            } else {
                card.style.opacity = 0;
                card.style.display = 'none'; // 뒤에 있는 카드는 이벤트 방지
            }
        });
    };
    
    // 드래그 시작 시점
    const startDrag = (e) => {
        // 애니메이션 중에는 모든 상호작용 무시 [FIX]
        if (isTransitioning) {
            return; 
        }

        // 맨 위 카드(0번 인덱스)가 현재 클릭한 카드인지 확인하여 다른 카드 조작 방지 [FIX]
        activeCard = e.currentTarget;
        if (!activeCard || cards[0] !== activeCard) {
            return;
        }

        isDragging = true;
        isClickAllowed = true; // 드래그 시작 시 클릭이라고 가정
        activeCard.classList.add('dragging');
        
        const touch = e.type === 'touchstart' ? e.touches[0] : e;
        startX = touch.clientX;
    };

    // 드래그 중
    const drag = (e) => {
        if (!isDragging || !activeCard) return;
        
        // 드래그 중 스크롤 등 기본 동작 방지
        if(e.cancelable) e.preventDefault(); 

        const touch = e.type === 'touchmove' ? e.touches[0] : e;
        const currentX = touch.clientX;
        
        offsetX = currentX - startX;
        
        // 5픽셀 이상 움직였으면 클릭 아님
        if (Math.abs(offsetX) > 5) {
            isClickAllowed = false;
        }
        
        const rotation = offsetX / 20;
        activeCard.style.transform = `translateX(${offsetX}px) rotate(${rotation}deg)`;

        const opacity = Math.abs(offsetX) / (window.innerWidth / 4);
        
        if (likeIndicator && passIndicator) {
            if (offsetX > 0) {
                likeIndicator.style.opacity = opacity;
                passIndicator.style.opacity = 0;
            } else {
                passIndicator.style.opacity = opacity;
                likeIndicator.style.opacity = 0;
            }
        }
    };

    // 드래그 종료 시점
    const endDrag = (e) => {
        if (!isDragging || !activeCard) return;
        isDragging = false;
        activeCard.classList.remove('dragging');

        const decisionThreshold = window.innerWidth / 4;

        if (Math.abs(offsetX) > decisionThreshold) {
            // 스와이프 성공
            
            // 상호작용 잠금 [FIX]
            isTransitioning = true;
            
            const direction = offsetX > 0 ? 1 : -1;

            activeCard.style.transition = 'transform 0.5s ease, opacity 0.5s ease';
            activeCard.style.transform = `translateX(${direction * window.innerWidth}px) rotate(${direction * 30}deg)`;
            activeCard.style.opacity = 0;

            if (direction === 1) { // Like
                saveLikedItem(activeCard.dataset.id);
            }
            
            // 애니메이션 후 DOM과 배열에서 제거
            setTimeout(() => {
                if (cardContainer.contains(activeCard)) {
                    cardContainer.removeChild(activeCard);
                }
                
                // [FIX] 배열에서 맨 앞 요소를 제거 (다음 카드가 0번이 되게 함)
                cards.shift(); 
                
                updateCardStack();
                
                // 잠금 해제 [FIX]
                isTransitioning = false;
            }, 300); 

        } else { 
            // 스와이프 실패 (원래 위치로 복귀)
            activeCard.style.transition = 'transform 0.4s ease';
            activeCard.style.transform = `translateY(0px) scale(1)`;
            
            if (likeIndicator) likeIndicator.style.opacity = 0;
            if (passIndicator) passIndicator.style.opacity = 0;
        }
        
        offsetX = 0;
    };
    
    // 클릭 시 링크 이동 처리
    const handleCardClick = (e) => {
        // 드래그가 발생했다면 클릭 무시 [FIX]
        if (!isClickAllowed) {
            return; 
        }
        
        const link = e.currentTarget.dataset.link;
        if (link && link !== 'None') {
            window.open(link, '_blank');
        }
    };

    // 이벤트 리스너 등록
    cards.forEach(card => {
        card.addEventListener('mousedown', startDrag);
        card.addEventListener('touchstart', startDrag, { passive: false });
        card.addEventListener('click', handleCardClick);
    });

    // 문서 전체에 이동/종료 이벤트 등록
    document.addEventListener('mousemove', drag);
    document.addEventListener('touchmove', drag, { passive: false });
    
    document.addEventListener('mouseup', endDrag);
    document.addEventListener('touchend', endDrag);
    
    // 초기화 실행
    updateCardStack();
}

// --- '좋아요' 저장 및 조회 로직 ---
function getLikedItems() {
    return JSON.parse(localStorage.getItem('likedPolicies') || '[]');
}

function saveLikedItem(id) {
    if (!id) {
        console.error("정책 ID가 없습니다.");
        return;
    }
    const likedItems = getLikedItems();
    if (!likedItems.includes(id)) {
        likedItems.push(id);
        localStorage.setItem('likedPolicies', JSON.stringify(likedItems));
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
        } else {
            item.style.display = 'none'; // 좋아요 안 한 건 숨김
        }
    });
}

// --- 분석 페이지 로직 (index_03) ---
function initAnalysisPage() {
    const analysisResults = document.getElementById('analysis-results');
    if (!analysisResults) return;

    const likedIds = getLikedItems();
    if (likedIds.length === 0) {
        analysisResults.innerHTML = "<p>아직 '좋아요'한 정책이 없습니다.</p>"; // [FIX] 따옴표 수정
        return;
    }

    const policies = [];
    document.querySelectorAll('.grid-item, .card').forEach(el => {
        const id = el.dataset.id;
        if (id && !policies.find(p => p.id === id)) {
            policies.push({
                id: id,
                genre: el.dataset.genre || '기타'
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
    
    analysisResults.innerHTML = ''; 

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

        setTimeout(() => {
            const bar = statElement.querySelector('.genre-bar');
            if(bar) bar.style.width = `${percentage}%`;
        }, 100);
    });
}