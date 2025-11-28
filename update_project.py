import os
import shutil

def generate_env_file():
    """Generates the .env file with placeholder DB credentials."""
    env_content = """# PostgreSQL 데이터베이스 연결 정보
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name

# 전체 DATABASE_URL (위의 정보를 기반으로 자동 생성)
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
"""
    with open(".env", "w") as f:
        f.write(env_content)
    print(".env 파일이 생성되거나 업데이트되었습니다. 데이터베이스 정보를 수정해주세요.")

def generate_main_py():
    """Generates the main.py FastAPI application file."""
    main_py_content = """import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Load environment variables
load_dotenv()

# Database configuration from .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# CRITICAL: Check if DB credentials are set
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    # This check is more robust for actual usage. For generation, we assume user will fill it.
    print("경고: .env 파일에 데이터베이스 연결 정보가 올바르게 설정되지 않았을 수 있습니다. 실행 전에 확인해주세요.")
    # raise ValueError("데이터베이스 연결 정보가 .env 파일에 올바르게 설정되지 않았습니다.")


DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Model
class BeingGeul(Base):
    __tablename__ = "being_geul" # CRITICAL: Ensure table name is explicitly set

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    summary = Column(Text) # Use Text for longer summaries
    period = Column(String)
    link = Column(String)

# Create database tables (if they don't exist)
# NOTE: This will create tables on application startup.
# For production, consider using Alembic for migrations.
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# 정적 파일 (CSS, JS 등)을 제공하기 위한 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 템플릿 설정을 위한 디렉토리 지정
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: SessionLocal = Depends(get_db)):
    geuls = db.query(BeingGeul).all()
    return templates.TemplateResponse("index_01.html", {"request": request, "geuls": geuls, "active_page": "/"})

@app.get("/{page_name}", response_class=HTMLResponse)
async def read_page(page_name: str, request: Request, db: SessionLocal = Depends(get_db)):
    # Prevent directory traversal
    if ".." in page_name or "/" in page_name:
        raise HTTPException(status_code=400, detail="Invalid page name")

    template_file = f"{page_name}.html"
    template_path = os.path.join(templates.directory, template_file)

    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="Page not found")
    
    context = {"request": request, "active_page": f"/{page_name}"}
    # Only index_01 gets dynamic data for this specific implementation
    # Other pages are static placeholders for now
    if page_name == "index_01":
        geuls = db.query(BeingGeul).all()
        context["geuls"] = geuls
    
    return templates.TemplateResponse(template_file, context)

"""
    with open("main.py", "w") as f:
        f.write(main_py_content)
    print("main.py 파일이 생성되거나 업데이트되었습니다.")

def generate_templates_and_static_files():
    """Creates/overwrites templates and static directories and their respective files."""
    # Create directories
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    print("templates/ 및 static/ 디렉토리가 생성되거나 이미 존재합니다.")

    # Create index_01.html with Jinja2 loop and dark theme elements
    # Note: Variable name changed from 'items' to 'geuls' as per request
    index_01_html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>오늘의 정책 - Policy Matcher</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link rel="stylesheet" href="/static/style.css">
</head>
<body class="dark-mode">
    <div class="main-container">
        <aside class="sidebar">
            <div class="logo-area">Policy Matcher</div>
            <nav class="menu">
                <a href="/" class="menu-item {% if active_page == '/' %}active{% endif %}">
                    <i class="fas fa-layer-group"></i>
                    <span>오늘의 정책</span>
                </a>
                <a href="/index_02" class="menu-item {% if active_page == '/index_02' %}active{% endif %}">
                    <i class="fas fa-bookmark"></i>
                    <span>찜한 정책</span>
                </a>
                <a href="/index_03" class="menu-item {% if active_page == '/index_03' %}active{% endif %}">
                    <i class="fas fa-chart-pie"></i>
                    <span>취향 분석</span>
                </a>
                <a href="/index_04" class="menu-item {% if active_page == '/index_04' %}active{% endif %}">
                    <i class="fas fa-search"></i>
                    <span>정책 탐색</span>
                </a>
            </nav>
        </aside>

        <main class="content-area">
            <div class="content-header">
                <h2>오늘의 정책 추천</h2>
                <p>데이터베이스에서 가져온 정책 정보입니다.</p>
            </div>
            <div class="policy-card-list-container">
                {% if geuls %}
                    {% for item in geuls %}
                    <a href="{{ item.link }}" target="_blank" class="policy-card">
                        <h3>{{ item.title }}</h3>
                        <p>{{ item.summary }}</p>
                        <span class="period">{{ item.period }}</span>
                    </a>
                    {% endfor %}
                {% else %}
                    <p class="no-data-message">표시할 정책 데이터가 없습니다. 데이터베이스에 데이터를 추가해주세요.</p>
                {% endif %}
            </div>
        </main>
    </div>
    <script src="/static/script.js"></script>
</body>
</html>"""
    with open("templates/index_01.html", "w") as f:
        f.write(index_01_html_content)
    print("templates/index_01.html 파일이 생성되거나 업데이트되었습니다.")

    # Create placeholder HTML files for index_02 to index_04 as duplicates of index_01.html
    # Adjusting for active menu item and title/header
    for i in range(2, 5):
        current_page_path = f"/index_0{i}"
        
        # Create a modified content for each placeholder page
        modified_content = index_01_html_content.replace(
            '',
            '\n            <div class="content-body">\n                <p>이 페이지는 아직 내용이 없습니다. 곧 업데이트될 예정입니다.</p>\n            </div>'
        ).replace(
            '<div class="content-header">\n                <h2>오늘의 정책 추천</h2>\n                <p>데이터베이스에서 가져온 정책 정보입니다.</p>\n            </div>',
            f'<div class="content-header">\n                <h2>페이지 0{i}</h2>\n                <p>이곳에 페이지 0{i}의 특정 콘텐츠가 들어갑니다.</p>\n            </div>'
        ).replace(
            '<title>오늘의 정책 - Policy Matcher</title>',
            f'<title>페이지 0{i} - Policy Matcher</title>'
        ).replace(
            # Remove the dynamic geuls loop for placeholder pages
            """            <div class="policy-card-list-container">
                {% if geuls %}
                    {% for item in geuls %}
                    <a href="{{ item.link }}" target="_blank" class="policy-card">
                        <h3>{{ item.title }}</h3>
                        <p>{{ item.summary }}</p>
                        <span class="period">{{ item.period }}</span>
                    </a>
                    {% endfor %}
                {% else %}
                    <p class="no-data-message">표시할 정책 데이터가 없습니다. 데이터베이스에 데이터를 추가해주세요.</p>
                {% endif %}
            </div>""",
            "" # Remove the entire block
        )
        
        # Adjust active class for navigation
        modified_content = modified_content.replace(
            'href="/" class="menu-item {% if active_page == \'/\' %}active{% endif %}"',
            'href="/" class="menu-item"'
        )
        for j in range(2, 5):
            if j == i:
                modified_content = modified_content.replace(
                    f'href="/index_0{j}" class="menu-item {{% if active_page == \'/index_0{j}\' %}}active{{% endif %}}"',
                    f'href="/index_0{j}" class="menu-item active"'
                )
            else:
                 modified_content = modified_content.replace(
                    f'href="/index_0{j}" class="menu-item {{% if active_page == \'/index_0{j}\' %}}active{{% endif %}}"',
                    f'href="/index_0{j}" class="menu-item"'
                )

        with open(f"templates/index_0{i}.html", "w") as f:
            f.write(modified_content)
        print(f"templates/index_0{i}.html 파일이 생성되거나 업데이트되었습니다.")


    # Create style.css with dark theme for policy cards
    style_css_content = """/* --- 기본 리셋 및 폰트 --- */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Pretendard", Roboto, sans-serif;
    height: 100vh;
    overflow: hidden;
    background-color: #1a1a1a; /* Global Dark body background */
    color: #f0f0f0; /* Light text for dark mode */
}

a {
    text-decoration: none; /* 링크 밑줄 제거 */
    color: inherit; /* 부모 색상 상속 */
}

/* --- 메인 레이아웃 컨테이너 --- */
.main-container {
    display: flex;
    height: 100%;
}

/* --- 왼쪽 사이드바 (메뉴) 스타일 --- */
.sidebar {
    width: 250px;
    background-color: #222222; /* Darker sidebar */
    color: #ecf0f1;
    display: flex;
    flex-direction: column;
    padding: 20px;
    box-shadow: 2px 0 10px rgba(0,0,0,0.5);
}

.logo-area {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 40px;
    text-align: center;
    letter-spacing: 1px;
}

.menu {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.menu-item {
    display: flex;
    align-items: center;
    padding: 15px 20px;
    cursor: pointer;
    border-radius: 10px;
    transition: all 0.3s ease;
    color: #bdc3c7;
}

.menu-item i {
    font-size: 20px;
    margin-right: 15px;
    width: 25px;
    text-align: center;
}

.menu-item:hover {
    background-color: rgba(255,255,255,0.1);
    color: white;
}

/* 활성 상태 강조 */
.menu-item.active {
    background-color: #555555; /* Darker active background */
    color: white;
    font-weight: 600;
}


/* --- 오른쪽 콘텐츠 영역 스타일 --- */
.content-area {
    flex: 1;
    background-color: #282828; /* Dark content area */
    padding: 40px;
    overflow-y: auto;
    position: relative;
    color: #f0f0f0; /* Light text for content */
}

.content-header {
    margin-bottom: 30px;
}

.content-header h2 {
    font-size: 28px;
    color: #ffffff;
    margin-bottom: 10px;
}

.content-header p {
    color: #cccccc;
    font-size: 16px;
}


/* 정책 카드 리스트 컨테이너 */
.policy-card-list-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); /* Responsive grid */
    gap: 25px;
    padding: 20px 0;
}

/* 정책 카드 스타일 */
.policy-card {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background-color: #000000; /* Black background */
    color: #FFFFFF; /* White text */
    border-radius: 15px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.6); /* Enhanced shadow for dark card */
    padding: 25px;
    cursor: pointer;
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    text-decoration: none;
    min-height: 200px; /* Ensure cards have a minimum height */
}

.policy-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 25px rgba(0,0,0,0.8);
}

.policy-card h3 {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 10px;
    line-height: 1.3;
}

.policy-card p {
    font-size: 15px;
    line-height: 1.6;
    margin-bottom: 15px;
    flex-grow: 1;
    color: #e0e0e0;
}

.policy-card .period {
    font-size: 13px;
    font-weight: 500;
    color: #bbbbbb;
    text-align: right;
}

.no-data-message {
    grid-column: 1 / -1; /* Span across all columns */
    text-align: center;
    color: #cccccc;
    font-size: 18px;
    padding: 50px 0;
}

/* --- 기타 페이지 콘텐츠를 위한 기본 스타일 --- */
.content-body {
    padding: 20px 0;
    line-height: 1.6;
    font-size: 16px;
    color: #e0e0e0;
}
"""
    with open("static/style.css", "w") as f:
        f.write(style_css_content)
    print("static/style.css 파일이 생성되거나 업데이트되었습니다.")

    # Create script.js with a simple console log placeholder
    script_js_content = """console.log("script.js loaded for FastAPI project.");
// Your custom JavaScript for interactivity can go here.
"""
    with open("static/script.js", "w") as f:
        f.write(script_js_content)
    print("static/script.js 파일이 생성되거나 업데이트되었습니다.")

def main():
    """Main function to orchestrate project setup."""
    print("FastAPI 프로젝트 초기화 스크립트를 시작합니다.")
    
    # Ensure all target directories exist
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)

    generate_env_file()
    generate_main_py()
    generate_templates_and_static_files()
    
    print("\n프로젝트 설정이 완료되었습니다.")
    print("다음 단계를 진행해주세요:")
    print("1. 'pip install fastapi uvicorn jinja2 python-dotenv sqlalchemy psycopg2-binary' 명령어로 필요한 라이브러리를 설치합니다.")
    print("2. '.env' 파일을 열어 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME' 정보를 실제 PostgreSQL 설정에 맞게 수정합니다.")
    print("3. 'main.py'가 실행될 때 'being_geul' 테이블이 자동으로 생성됩니다. (운영 환경에서는 Alembic 사용 권장)")
    print("4. 데이터베이스에 샘플 데이터를 추가하여 '/index_01' 페이지에서 동적으로 표시되는지 확인합니다.")
    print("5. 'uvicorn main:app --reload' 명령어로 FastAPI 애플리케이션을 실행합니다.")
    print("6. 웹 브라우저에서 'http://127.0.0.1:8000'으로 접속하여 결과를 확인합니다.")

if __name__ == "__main__":
    main()