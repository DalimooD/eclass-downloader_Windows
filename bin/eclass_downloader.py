#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import os, sys, subprocess, pathlib

# ─── 프로젝트 최상위(root) 자동 탐지 ────────────────────────────────── #
_this = pathlib.Path(__file__).resolve()
ROOT_DIR = _this.parent.parent if _this.parent.name == 'bin' else _this.parent

# ────────────────────────────── 경로 설정 ────────────────────────────── #
BASE_DIR     = ROOT_DIR
BIN_DIR      = ROOT_DIR / "bin"
VENV_DIR     = BIN_DIR  / "eclass-venv"
PROFILE_DIR  = BIN_DIR  / "selenium-profile"
COOKIES_FILE = BIN_DIR  / "cookies.json"
COOKIES_PY   = BIN_DIR  / "save_cookies.py"
EXT_TOOL_ID  = "211"

# ── 플랫폼별 가상환경 실행 파일 경로 계산 ───────────────────────────── #
IS_WIN   = os.name == 'nt'
VENV_BIN = VENV_DIR / ('Scripts' if IS_WIN else 'bin')
ENV_PY   = VENV_BIN / ('python.exe' if IS_WIN else 'python')
PIP_EXE  = VENV_BIN / ('pip.exe'    if IS_WIN else 'pip')

# ────────────────────────── 가상환경 준비 / 재실행 ───────────────────── #
if pathlib.Path(sys.executable).resolve() != ENV_PY.resolve():
    if not VENV_DIR.exists():
        print("[가상환경 준비] 새로운 가상환경을 생성합니다...")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])

    for pkg in ("selenium", "requests"):
        if subprocess.call([str(PIP_EXE), "show", pkg],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL):
            print(f"[가상환경 준비] '{pkg}' 패키지 설치 중...")
            subprocess.check_call([str(PIP_EXE), "install", pkg])

    print("[가상환경 준비] 가상환경으로 재실행...")
    os.execv(str(ENV_PY), [str(ENV_PY), __file__, *sys.argv[1:]])

# ───────────────────────────── venv 내부 영역 ───────────────────────── #
import json, re, time, requests
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, JavascriptException

# ───────────────────────────── 프로그램 배너 ─────────────────────────── #
print("\n" + "="*50)
print("          ★ eClass 강의 다운로더 v2.6 ★      ")
print("      제작자: 푸앙이 | 업데이트: 2025-04-18")
print("="*50 + "\n")

# ────────────────────────────── 유틸 함수 ───────────────────────────── #
def safe(text: str) -> str:
    """파일 시스템에 안전한 짧은 이름 생성"""
    return ''.join(c for c in text if c.isalnum() or c in ' _-')[:120]

def click_resume():
    try:
        btn = WebDriverWait(driver, 4).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '.confirm-dialog-wrapper .confirm-ok-btn'))
        )
        btn.click()
        print("[이어보기] 팝업 '예' 클릭")
    except TimeoutException:
        pass

def poll_video(max_wait: int = 120) -> tuple[str, float]:
    print(f"[비디오 탐지] 본편 영상 탐색 중... 최대 {max_wait}초 대기")
    start = time.time()
    last_report = start
    while time.time() - start < max_wait:
        if time.time() - last_report >= 5:
            print(f"[비디오 탐지] {int(time.time() - start)}초 경과...")
            last_report = time.time()
        for v in driver.find_elements(By.TAG_NAME, 'video'):
            try:
                src = driver.execute_script("return arguments[0].currentSrc", v) or ''
                dur = driver.execute_script("return arguments[0].duration",   v) or 0
            except JavascriptException:
                continue
            if src.startswith('blob:') or re.search(r'(preloader|intro)\.mp4', src, re.I):
                continue
            if dur >= 60:
                print(f"[비디오 탐지] 본편 영상 발견: 재생시간 {dur/60:.1f}분")
                return src, float(dur)
        time.sleep(1)
    print("[비디오 탐지] 시간 초과 - 본편 영상 미발견")
    return '', 0.0

# ───────────────────────── 쿠키 확인 및 로드 ────────────────────────── #
BIN_DIR.mkdir(exist_ok=True)
PROFILE_DIR.mkdir(exist_ok=True)
print('[쿠키 확인] cookies.json 상태 점검...', end=' ')
need_cookie = True
if COOKIES_FILE.exists():
    try:
        domains = {c.get('domain','') for c in json.load(open(COOKIES_FILE))}
        if any('canvas.cau.ac.kr' in d for d in domains) and \
           any('eclass3.cau.ac.kr' in d for d in domains):
            need_cookie = False
            print('정상')
    except Exception:
        pass
if need_cookie:
    print('쿠키 누락 - save_cookies.py 실행')
    if subprocess.call([str(ENV_PY), str(COOKIES_PY)]) != 0 or not COOKIES_FILE.exists():
        print('[오류] 쿠키 캡처 실패')
        sys.exit(1)
COOKIES = json.load(open(COOKIES_FILE))
print('[완료] 쿠키 로드 완료\n\n')
print('========================================================================================================================\n')
print('[주의] !!! 생성된 bin/cookies.json 파일이 유출될 경우 본인의 계정 정보가 탈취될 수 있으니 보안에 각별히 주의하십시오 !!!\n')
print('========================================================================================================================\n\n')

# ────────────────────────── 강좌 ID 입력 및 확인 ───────────────────── #
print('강좌 URL 예시: https://eclass3.cau.ac.kr/courses/{123456}/ ▶ 강좌 ID: 123456')
course_id = input('[강좌 설정] 강좌 ID ▶ ').strip()
if not course_id.isdigit():
    print('[오류] 숫자만 입력하십시오')
    sys.exit(1)
COURSE_URL = f'https://eclass3.cau.ac.kr/courses/{course_id}'
print(f'[완료] 강좌 주소 설정: {COURSE_URL}\n')

# ───────────────────────── Chrome WebDriver 초기화 ─────────────────── #
print('[브라우저] Chrome 드라이버 실행...')
opts = webdriver.ChromeOptions()
opts.add_argument('--headless=new')
opts.add_argument('--mute-audio')          
opts.add_argument(f'--user-data-dir={PROFILE_DIR}')
opts.add_experimental_option('excludeSwitches', ['enable-logging'])
opts.add_argument('--disable-logging')               
opts.add_argument('--log-level=3')                 

from selenium.webdriver.chrome.service import Service 
service = Service(log_path=os.devnull)              

driver = webdriver.Chrome(service=service, options=opts)
driver.implicitly_wait(8)
wait = WebDriverWait(driver, 20)
print('[완료] 드라이버 준비 완료\n')

# ───────────────────────────── 쿠키 주입 ───────────────────────────── #
print('[쿠키 주입] 브라우저에 쿠키 적용...')
for dom in {c['domain'] for c in COOKIES if c.get('domain')}:
    driver.get(f'https://{dom.lstrip(".")}/')
    for c in [x for x in COOKIES if x['domain'] == dom]:
        ent = {'name': c['name'], 'value': c['value'], 'path': c.get('path','/')}
        if isinstance(c.get('expiry'), (int, float)):
            ent['expiry'] = int(c['expiry'])
        driver.add_cookie(ent)
print('[완료] 쿠키 주입 완료\n')

# ──────────────── 강좌 페이지 로드 및 저장 디렉터리 생성 ─────────────── #
print('[강좌 확인] 강좌 페이지 로드...')
driver.get(COURSE_URL)
title = driver.title.strip()
print(f'[강좌 확인] 강좌명: {title}')
if input('[강좌 확인] 계속 진행하시겠습니까? (y/n) ▶ ').lower() != 'y':
    driver.quit()
    sys.exit(0)
DL_DIR = BASE_DIR / safe(title)
DL_DIR.mkdir(exist_ok=True)
TXT_DIR = DL_DIR / 'stream_links'
TXT_DIR.mkdir(exist_ok=True)
print(f'[완료] 저장 폴더: {DL_DIR}\n')

# ─────────────────────────── 강의 리스트 링크 수집 ────────────────────── #
print('[목록 수집] 강의 리스트에서 링크 수집 중...')
driver.get(f'{COURSE_URL}/external_tools/{EXT_TOOL_ID}')
wait.until(EC.presence_of_element_located((By.ID, 'tool_form'))).submit()
wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'tool_content')))
links = [a.get_attribute('href') for a in wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="/modules/items/"]')))]
modules = []
for idx, link in enumerate(links, 1):
    driver.get(link)
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'tool_content')))
    modules.append((idx, driver.title.strip(), link))
    print(f' {idx:>2}. {modules[-1][1]}')
print()

# ──────────────────────────── 다운로드 대상 선택 ────────────────────── #
print('  A) 전체 다운로드')
print('  N) 번호 지정 (예: 1,4,6)')
print('  R) 범위 지정 (예: 2-5)')
print('  E) 제외 지정 (예: 3,7)')
mode = input('모드 선택 [A/N/R/E] ▶ ').lower().strip()
selection: set[int] = set()
if mode == 'a':
    selection = set(range(1, len(modules) + 1))
elif mode == 'n':
    nums = input('번호 ▶ ').strip()
    selection = {int(n) for n in re.split(r'[ ,]+', nums) if n.isdigit()}
elif mode == 'r':
    rng = input('범위 (시작-끝) ▶ ').strip()
    start, end = map(int, rng.split('-', 1))
    selection = set(range(start, end + 1))
elif mode == 'e':
    nums = input('제외 번호 ▶ ').strip()
    excl = {int(n) for n in re.split(r'[ ,]+', nums) if n.isdigit()}
    selection = set(range(1, len(modules) + 1)) - excl
else:
    print('[오류] 잘못된 선택입니다')
    driver.quit()
    sys.exit(1)
filtered = [m for m in modules if m[0] in selection]
print('\n[알림] 비디오 파일이 아닐 경우 탐지에 시간이 걸릴 수 있습니다. 정상 작동 중이니 잠시만 기다려 주세요...')
print(f'[설정] 다운로드 대상: {len(filtered)}개 강의')
if not filtered:
    sys.exit(0)
session = requests.Session()

# ───────────────────────────── 다운로드 루프 ────────────────────────── #
for idx, (num, title, href) in enumerate(filtered, 1):
    print(f'\n[다운로드] {title}')
    driver.get(href)
    wait.until(EC.presence_of_element_located((By.ID, 'tool_form'))).submit()
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'tool_content')))
    try:
        wait.until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[src*='ocs.cau.ac.kr']")), 6)
    except TimeoutException:
        print('[건너뜀] iframe이 없습니다')
        driver.switch_to.default_content()
        continue
    try:
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'div.vc-front-screen-play-btn'))).click()
    except TimeoutException:
        pass
    click_resume()
    src, dur = poll_video()
    if not src:
        print('[건너뜀] 본편 비디오 미발견')
        driver.switch_to.default_content()
        continue
    print(f'[정보] 재생시간: {dur/60:.1f}분')
    if src.endswith('.m3u8'):
        (TXT_DIR / f'{safe(title)}.txt').write_text(src)
        print('[저장] m3u8 링크 저장')
    else:
        size = int(session.head(src, allow_redirects=True)
                         .headers.get('Content-Length', '0') or 0)
        if size and size < 5 * 1024 * 1024:
            print('[건너뜀] 5MB 미만 파일')
        else:
            fn = DL_DIR / f'{safe(title)}.mp4'
            with session.get(src, stream=True) as r, open(fn, 'wb') as f:
                for chunk in r.iter_content(1024 * 1024):
                    f.write(chunk)
            print(f'[완료] 저장: {fn.name}')
    driver.switch_to.default_content()

print('\n[종료] 모든 다운로드 완료')
driver.quit()
