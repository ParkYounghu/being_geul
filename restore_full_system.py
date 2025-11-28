# -*- coding: utf-8 -*-
import os

def create_project_structure():
    """
    프로젝트 디렉토리 구조를 생성합니다.
    'templates', 'static' 디렉토리가 없으면 생성합니다.
    """
    print("프로젝트 구조를 설정합니다...")
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    print("디렉토리 구조 생성 완료.")

def write_env_file():
    """
    .env 파일을 생성하여 데이터베이스 연결 정보를 설정합니다.
    """
    print(".env 파일을 생성합니다...")
    content = """
# PostgreSQL 데이터베이스 연결 정보
# 실제 값으로 변경해야 합니다.
db_host=db_postgresql
db_port=5432
db_name=main_db
db_user=admin
db_password=admin123

"""
    with open(".env", "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(".env 파일 생성 완료.")

def write_main_py_file():
    """
    main.py 파일을 생성합니다.
    FastAPI 애플리케이션, SQLAlchemy 모델, 데이터베이스 세션 및 라우팅 로직을 포함합니다.
    """
    print("main.py 파일을 생성합니다...")
    content = """
# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# .env 파일에서 환경 변수 로드
load_dotenv()

# 데이터베이스 연결 정보
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy 설정
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 데이터베이스 모델 정의
class BeingGeul(Base):
    __tablename__ = "being_geul"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    summary = Column(Text)
    period = Column(String)
    link = Column(String)
    genre = Column(String) # 장르 컬럼 추가

# FastAPI 앱 초기화
app = FastAPI()

# 정적 파일 마운트 (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 데이터베이스 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 라우팅 ---

@app.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    ''' Tinder-style Swipe UI 페이지 '''
    policies = db.query(BeingGeul).all()
    return templates.TemplateResponse("index_01.html", {"request": request, "policies": policies})

@app.get("/liked")
def read_liked(request: Request, db: Session = Depends(get_db)):
    ''' '좋아요' 표시한 정책을 보여주는 페이지 '''
    policies = db.query(BeingGeul).all()
    return templates.TemplateResponse("index_02.html", {"request": request, "policies": policies})

@app.get("/analysis")
def read_analysis(request: Request, db: Session = Depends(get_db)):
    ''' '좋아요' 기반 장르 분석 페이지 '''
    policies = db.query(BeingGeul).all()
    return templates.TemplateResponse("index_03.html", {"request": request, "policies": policies})

@app.get("/search")
def read_search(request: Request, db: Session = Depends(get_db)):
    ''' 모든 정책을 그리드 뷰로 보여주는 페이지 '''
    policies = db.query(BeingGeul).all()
    return templates.TemplateResponse("index_04.html", {"request": request, "policies": policies})

# --- 서버 실행 (디버깅용) ---
# if __name__ == "__main__":
#     import uvicorn
#     # 테이블 생성 (최초 실행 시 필요)
#     # Base.metadata.create_all(bind=engine)
#     uvicorn.run(app, host="0.0.0.0", port=8000)
"""
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content.strip())
    print("main.py 파일 생성 완료.")

def write_template_files():
    """
    네 개의 HTML 템플릿 파일을 생성합니다.
    """
    print("HTML 템플릿 파일을 생성합니다...")

    # index_01.html (스와이프 UI)
    index_01_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>빙글 - 홈</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <nav>
        <a href="/" class="active">홈</a>
        <a href="/liked">좋아요</a>
        <a href="/analysis">분석</a>
        <a href="/search">검색</a>
    </nav>
    <div id="card-container">
        {% for policy in policies %}
        <div class="card" data-id="{{ policy.id }}" data-link="{{ policy.link }}" data-genre="{{ policy.genre }}">
            <h2>{{ policy.title }}</h2>
            <p>{{ policy.summary }}</p>
            <span>기간: {{ policy.period }}</span>
        </div>
        {% endfor %}
    </div>
    <div id="action-indicators">
        <div id="pass-indicator" class="indicator">PASS</div>
        <div id="like-indicator" class="indicator">LIKE</div>
    </div>
    <script src="/static/script.js"></script>
</body>
</html>
"""
    with open("templates/index_01.html", "w", encoding="utf-8") as f:
        f.write(index_01_content.strip())

    # index_02.html ('좋아요' 목록)
    index_02_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>빙글 - 좋아요</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <nav>
        <a href="/">홈</a>
        <a href="/liked" class="active">좋아요</a>
        <a href="/analysis">분석</a>
        <a href="/search">검색</a>
    </nav>
    <div id="liked-grid" class="grid-container">
        {% for policy in policies %}
        <div class="grid-item" data-id="{{ policy.id }}" style="display: none;">
             <a href="{{ policy.link }}" target="_blank">
                <h2>{{ policy.title }}</h2>
                <p>{{ policy.summary }}</p>
                <span>기간: {{ policy.period }}</span>
            </a>
        </div>
        {% endfor %}
    </div>
    <script src="/static/script.js"></script>
</body>
</html>
"""
    with open("templates/index_02.html", "w", encoding="utf-8") as f:
        f.write(index_02_content.strip())

    # index_03.html (분석)
    index_03_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>빙글 - 분석</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <nav>
        <a href="/">홈</a>
        <a href="/liked">좋아요</a>
        <a href="/analysis" class="active">분석</a>
        <a href="/search">검색</a>
    </nav>
    <div id="analysis-container">
        <h1>'좋아요'한 정책 장르 분석</h1>
        <div id="analysis-results">
            <!-- 분석 결과가 여기에 동적으로 삽입됩니다. -->
        </div>
    </div>
    <script src="/static/script.js"></script>
</body>
</html>
"""
    with open("templates/index_03.html", "w", encoding="utf-8") as f:
        f.write(index_03_content.strip())

    # index_04.html (검색)
    index_04_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>빙글 - 검색</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <nav>
        <a href="/">홈</a>
        <a href="/liked">좋아요</a>
        <a href="/analysis">분석</a>
        <a href="/search" class="active">검색</a>
    </nav>
    <div id="search-grid" class="grid-container">
        {% for policy in policies %}
        <div class="grid-item" data-id="{{ policy.id }}">
            <a href="{{ policy.link }}" target="_blank">
                <h2>{{ policy.title }}</h2>
                <p>{{ policy.summary }}</p>
                <span>기간: {{ policy.period }}</span>
            </a>
        </div>
        {% endfor %}
    </div>
     <script src="/static/script.js"></script>
</body>
</html>
"""
    with open("templates/index_04.html", "w", encoding="utf-8") as f:
        f.write(index_04_content.strip())

    print("HTML 템플릿 파일 생성 완료.")


def write_static_files():
    """
    static/style.css와 static/script.js 파일을 생성합니다.
    """
    print("정적 파일(CSS, JS)을 생성합니다...")

    # style.css
    style_css_content = """
/* --- 기본 및 다크 모드 스타일 --- */
body {
    background-color: #1a1a1a;
    color: #fff;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    margin: 0;
    padding: 70px 0 0 0;
    overflow-x: hidden;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
}

/* --- 네비게이션 --- */
nav {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: #000;
    display: flex;
    justify-content: space-around;
    padding: 10px 0;
    z-index: 1000;
    border-bottom: 1px solid #333;
}

nav a {
    color: #fff;
    text-decoration: none;
    padding: 10px 15px;
    font-weight: bold;
    transition: color 0.3s;
}

nav a.active {
    color: #4CAF50;
    border-bottom: 2px solid #4CAF50;
}

/* --- 카드 스와이프 UI (index_01) --- */
#card-container {
    position: relative;
    width: 90vw;
    max-width: 400px;
    height: 70vh;
    margin-top: 20px;
}

.card {
    position: absolute;
    width: 100%;
    height: 100%;
    background-color: #000;
    border-radius: 15px;
    border: 1px solid #333;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
    padding: 20px;
    box-sizing: border-box;
    cursor: grab;
    user-select: none;
    transform-origin: center;
    transition: transform 0.5s ease, opacity 0.5s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.card:last-child {
    z-index: 10;
}

.card.dragging {
    cursor: grabbing;
    transition: none;
}

.card h2 {
    margin: 0 0 15px 0;
    font-size: 1.5em;
    color: #fff;
}

.card p {
    flex-grow: 1;
    font-size: 1em;
    line-height: 1.6;
    color: #ccc;
}

.card span {
    font-size: 0.9em;
    color: #888;
}

#action-indicators {
    position: fixed;
    top: 50%;
    left: 0;
    width: 100%;
    display: flex;
    justify-content: space-between;
    pointer-events: none;
    z-index: 100;
}

.indicator {
    font-size: 4em;
    font-weight: bold;
    padding: 20px;
    border-radius: 10px;
    opacity: 0;
    transition: opacity 0.3s;
}

#like-indicator {
    color: #4CAF50;
    border: 5px solid #4CAF50;
    transform: rotate(-15deg);
}

#pass-indicator {
    color: #F44336;
    border: 5px solid #F44336;
    transform: rotate(15deg);
}

/* --- 그리드 뷰 (index_02, index_04) --- */
.grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    padding: 20px;
    width: 100%;
    max-width: 1200px;
    box-sizing: border-box;
}

.grid-item {
    background-color: #000;
    border: 1px solid #333;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
    transition: transform 0.2s;
}
.grid-item a {
    text-decoration: none;
    color: inherit;
    display: flex;
    flex-direction: column;
    height: 100%;
}


.grid-item:hover {
    transform: translateY(-5px);
}

.grid-item h2 {
    margin: 0 0 10px 0;
    font-size: 1.2em;
    color: #fff;
}
.grid-item p {
    flex-grow: 1;
    font-size: 0.9em;
    color: #ccc;
    line-height: 1.5;
}
.grid-item span {
    font-size: 0.8em;
    color: #888;
    margin-top: 10px;
}


/* --- 분석 페이지 (index_03) --- */
#analysis-container {
    width: 90%;
    max-width: 800px;
    padding: 20px;
    text-align: center;
}

#analysis-results {
    background-color: #000;
    border: 1px solid #333;
    border-radius: 10px;
    padding: 20px;
    margin-top: 20px;
}

.genre-stat {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding: 10px;
    background-color: #1a1a1a;
    border-radius: 5px;
}

.genre-name {
    font-weight: bold;
    flex: 1;
    text-align: left;
}

.genre-bar-container {
    flex: 3;
    background-color: #333;
    border-radius: 5px;
    height: 20px;
    margin: 0 15px;
}

.genre-bar {
    background-color: #4CAF50;
    height: 100%;
    border-radius: 5px;
    transition: width 0.5s ease-in-out;
}

.genre-percentage {
    font-weight: bold;
    flex: 0 0 50px;
    text-align: right;
}
"""
    with open("static/style.css", "w", encoding="utf-8") as f:
        f.write(style_css_content.strip())

    # script.js
    script_js_content = """
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
        analysisResults.innerHTML = '<p>아직 \'좋아요\'한 정책이 없습니다.</p>';
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
"""
    with open("static/script.js", "w", encoding="utf-8") as f:
        f.write(script_js_content.strip())

    print("정적 파일 생성 완료.")

def main():
    """
    전체 시스템 복원 스크립트를 실행합니다.
    """
    print("FastAPI 프로젝트 전체 시스템 복원을 시작합니다.")
    create_project_structure()
    write_env_file()
    write_main_py_file()
    write_template_files()
    write_static_files()
    print("\n모든 파일이 성공적으로 생성되었습니다.")
    print("다음을 수행하여 프로젝트를 실행하세요:")
    print("1. '.env' 파일에 실제 데이터베이스 정보를 입력하세요.")
    print("2. pip install -r requirements.txt (필요한 라이브러리 설치)")
    print("3. python -c 'from main import Base, engine; Base.metadata.create_all(bind=engine)' (DB 테이블 생성)")
    print("4. uvicorn main:app --reload (서버 실행)")


if __name__ == "__main__":
    main()
