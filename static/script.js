/**
 * Policy Matcher - Main Script (Unified)
 * 각 페이지별 요소를 감지하여 필요한 로직만 안전하게 실행합니다.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. 스와이프 기능 (index_01.html)
    const cardStack = document.getElementById('cardStack');
    if (cardStack) {
        initSwipeFeature(cardStack);
    }

    // 2. 카테고리 칩 선택 기능 (index_04.html)
    const chipContainer = document.querySelector('.chip-scroll');
    if (chipContainer) {
        initChipFeature(chipContainer);
    }
});


/**
 * [기능 1] 틴더 스타일 스와이프 로직
 * - 드래그 앤 드롭, 카드 애니메이션, 데이터 렌더링 처리
 */
function initSwipeFeature(stackContainer) {
    const cardsData = [
        { title: "대중교통비 30% 환급", desc: "월 15회 이상 이용 시 지출금액의 일정 비율을 환급해 드립니다.", img: "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=600" },
        { title: "청년 주택 드림 청약", desc: "청약 당첨 시 연 2%대 저금리 대출을 지원하는 전용 통장입니다.", img: "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=600" },
        { title: "서울시 청년 수당", desc: "서울 거주 미취업 청년에게 매월 50만원씩 최대 6개월간 지원합니다.", img: "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=600" },
        { title: "K-패스 전국민 확대", desc: "전국 어디서나 대중교통 이용 시 마일리지 적립 혜택을 제공합니다.", img: "https://images.unsplash.com/photo-1615881842315-1365f3101933?w=600" },
        { title: "청년 도약 계좌 시즌2", desc: "5년 만기 시 최대 5천만 원 목돈 마련을 지원하는 정책금융 상품입니다.", img: "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=600" }
    ];

    let currentCardIndex = 0;

    // 카드 생성 함수
    function createCard(index) {
        if (index >= cardsData.length) return null;

        const data = cardsData[index];
        const el = document.createElement('div');
        el.className = 'swipe-card';
        
        // 카드 쌓임 효과 (Z-index 및 시각적 깊이감)
        const zIndex = cardsData.length - index;
        el.style.zIndex = zIndex;

        // HTML 구조
        el.innerHTML = `
            <div class="card-image" style="background-image: url('${data.img}')">
                <div class="status-text like-text">LIKE</div>
                <div class="status-text nope-text">NOPE</div>
            </div>
            <div class="card-info">
                <div>
                    <span class="card-badge">HOT 정책</span>
                    <h2 class="card-title">${data.title}</h2>
                    <p class="card-desc">${data.desc}</p>
                </div>
            </div>
        `;

        // 카드 스타일링 (뒤에 있는 카드는 작고 아래로 내려가게)
        if (index === currentCardIndex) {
            // 현재 카드 (맨 위)
            el.style.transform = 'scale(1) translateY(0)';
            el.style.opacity = '1';
            el.style.cursor = 'grab';
            // 드래그 이벤트 연결
            attachDragEvents(el);
        } else {
            // 대기 중인 카드들 (깊이감 연출)
            const offset = index - currentCardIndex;
            // 3장까지만 시각적으로 보여줌
            if (offset <= 2) {
                const scale = 1 - (offset * 0.05); // 0.95, 0.90 ...
                const translateY = offset * 15; // 15px, 30px ...
                el.style.transform = `scale(${scale}) translateY(${translateY}px)`;
                el.style.opacity = '1';
            } else {
                el.style.opacity = '0'; // 너무 뒤에 있는 카드는 숨김
            }
            el.style.pointerEvents = 'none'; // 클릭 방지
        }

        return el;
    }

    // 카드 전체 다시 그리기
    function renderCards() {
        stackContainer.innerHTML = '';
        
        // 남은 카드가 없을 때 (완료 화면)
        if (currentCardIndex >= cardsData.length) {
            stackContainer.innerHTML = `
                <div style="text-align:center; color:#555; padding-top: 50px;">
                    <i class="fas fa-check-circle" style="font-size: 50px; color: #3B82F6; margin-bottom: 20px;"></i>
                    <h3>모든 정책을 확인했어요!</h3>
                    <p>더 많은 정책이 업데이트될 예정입니다.</p>
                    <button id="resetBtn" style="margin-top:20px; padding:12px 24px; border:none; background:#3B82F6; color:white; border-radius:8px; cursor:pointer; font-weight:bold;">
                        처음부터 다시 보기
                    </button>
                </div>
            `;
            // 동적으로 생성된 버튼에 이벤트 리스너 추가
            setTimeout(() => {
                const resetBtn = document.getElementById('resetBtn');
                if(resetBtn) {
                    resetBtn.addEventListener('click', () => {
                        currentCardIndex = 0;
                        renderCards();
                    });
                }
            }, 0);
            return;
        }

        // 카드 렌더링 (현재 인덱스부터 끝까지)
        // 역순으로 렌더링하지 않고, CSS z-index로 제어
        for (let i = currentCardIndex; i < cardsData.length; i++) {
            const card = createCard(i);
            if (card) stackContainer.appendChild(card);
        }
    }

    // 드래그 이벤트 핸들러 (핵심 로직 - 클로저 사용으로 상태 격리)
    function attachDragEvents(card) {
        let isDragging = false;
        let startX = 0;
        let currentX = 0;
        const threshold = 120; // 날리기 판정 기준 거리

        const likeText = card.querySelector('.like-text');
        const nopeText = card.querySelector('.nope-text');

        // 내부 함수들을 미리 정의하여 이벤트 추가/제거 시 동일 참조 사용
        function onMove(e) {
            if (!isDragging) return;
            // 모바일 스크롤 방지
            if (e.type === 'touchmove') {
                // e.preventDefault(); // 필요 시 활성화 (단, 경고 발생 가능성 있음)
            }

            const clientX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
            currentX = clientX - startX;

            // 카드 회전 및 이동
            const rotate = currentX * 0.05; // 0.05도씩 회전
            card.style.transform = `translateX(${currentX}px) rotate(${rotate}deg)`;

            // LIKE / NOPE 텍스트 투명도 조절
            if (currentX > 0) {
                likeText.style.opacity = currentX / 100;
                nopeText.style.opacity = 0;
            } else {
                nopeText.style.opacity = Math.abs(currentX) / 100;
                likeText.style.opacity = 0;
            }
        }

        function onEnd() {
            if (!isDragging) return;
            isDragging = false;
            card.style.cursor = 'grab';

            // 이벤트 리스너 정리 (메모리 누수 및 충돌 방지)
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('touchmove', onMove);
            document.removeEventListener('mouseup', onEnd);
            document.removeEventListener('touchend', onEnd);

            // 판정 로직
            const moveOutWidth = window.innerWidth; // 화면 밖으로 보낼 거리
            
            if (currentX > threshold) {
                // 오른쪽 (LIKE)
                card.style.transition = 'transform 0.5s ease-out';
                card.style.transform = `translateX(${moveOutWidth}px) rotate(45deg)`;
                setTimeout(() => nextCard(), 300); // 애니메이션 후 데이터 변경
            } else if (currentX < -threshold) {
                // 왼쪽 (NOPE)
                card.style.transition = 'transform 0.5s ease-out';
                card.style.transform = `translateX(-${moveOutWidth}px) rotate(-45deg)`;
                setTimeout(() => nextCard(), 300);
            } else {
                // 원위치 복귀
                card.style.transition = 'transform 0.3s ease-out';
                card.style.transform = 'translateX(0) rotate(0)';
                likeText.style.opacity = 0;
                nopeText.style.opacity = 0;
            }
        }

        function onStart(e) {
            isDragging = true;
            startX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
            
            // 드래그 중에는 transition 제거 (즉각 반응)
            card.style.transition = 'none';
            card.style.cursor = 'grabbing';

            // document에 이벤트 붙이기 (마우스가 카드 밖으로 나가도 추적)
            document.addEventListener('mousemove', onMove);
            document.addEventListener('touchmove', onMove, { passive: false });
            document.addEventListener('mouseup', onEnd);
            document.addEventListener('touchend', onEnd);
        }

        card.addEventListener('mousedown', onStart);
        card.addEventListener('touchstart', onStart);
    }

    // 다음 카드로 인덱스 변경 및 리렌더링
    function nextCard() {
        currentCardIndex++;
        renderCards();
    }

    // 초기 실행
    renderCards();
}


/**
 * [기능 2] 카테고리 칩 선택 로직 (index_04.html)
 * - 칩 클릭 시 활성 상태(active) 토글
 */
function initChipFeature(container) {
    const chips = container.querySelectorAll('.chip');
    
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            // 다른 칩 active 제거
            chips.forEach(c => c.classList.remove('active'));
            // 클릭한 칩 active 추가
            chip.classList.add('active');
            
            console.log(`선택된 카테고리: ${chip.textContent}`);
        });
    });
}