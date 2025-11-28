import os
import shutil

# 파일 목록 정의
html_files = ["index_01.html", "index_02.html", "index_03.html", "index_04.html"]
css_files = ["style.css"]
js_files = ["script.js"]

# 디렉토리 경로 정의
templates_dir = "templates"
static_dir = "static"

def setup_project_structure():
    """
    프로젝트 구조를 설정하고 HTML, CSS, JS 파일을 이동합니다.
    """
    print("프로젝트 구조를 설정합니다...")

    # templates 디렉토리 생성
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        print(f"디렉토리 생성: {templates_dir}/")
    else:
        print(f"디렉토리 존재: {templates_dir}/")

    # static 디렉토리 생성
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        print(f"디렉토리 생성: {static_dir}/")
    else:
        print(f"디렉토리 존재: {static_dir}/")

    # HTML 파일 이동
    for file in html_files:
        if os.path.exists(file):
            shutil.move(file, os.path.join(templates_dir, file))
            print(f"파일 이동: {file} -> {templates_dir}/{file}")
        else:
            print(f"파일을 찾을 수 없음 (스킵): {file}")

    # CSS 및 JS 파일 이동
    for file in css_files + js_files:
        if os.path.exists(file):
            shutil.move(file, os.path.join(static_dir, file))
            print(f"파일 이동: {file} -> {static_dir}/{file}")
        else:
            print(f"파일을 찾을 수 없음 (스킵): {file}")

    print("프로젝트 구조 설정 완료.")

if __name__ == "__main__":
    setup_project_structure()

