# 중앙대학교 eClass 강의 다운로더 (Windows)

`중앙대학교 eClass 강의 다운로더`는 중앙대학교 eClass 플랫폼의 강의를 자동으로 다운로드하는 Python 스크립트입니다. 

현재 페이지는 **Windows용** 프로그램 설치를 안내하고 있습니다.

스크립트는 **헤드리스(Headless) Chrome**과 **가상환경(venv)** 기반으로 동작하도록 설계되었습니다.

---

## 주요 기능

- 강좌 URL을 입력하면 해당 강좌의 전체 모듈(강의) 목록을 자동으로 수집
- 비디오 스트림(MP4 혹은 m3u8) 자동 탐지 및 다운로드 링크 저장
- 지정한 강의만 선택 다운로드 가능 (전체, 번호 지정, 범위 지정, 제외 지정)
- 재생 중단 지점에서 이어보기 지원
- 헤드리스 Chrome `--mute-audio` 옵션으로 소리 제거 및 불필요 로그 억제
- Windows용 `.bat` 및 macOS용 `.command` 실행 래퍼 스크립트 제공

---

## 사전 요구사항

- Python 3.8 이상
- Git 설치
- Chrome 또는 Chromium 브라우저 (버전 호환)
- ChromeDriver (브라우저 버전과 일치하는 드라이버)

---

## 사용 방법

## macOS: `.command` 더블 클릭하여 실행

혹은 Option + Command로 Spotlight 실행 -> 터미널 입력 후 실행 ->

```bash
cd (다운로드한 폴더 경로)
chmod +x eclass_downloader.command
eclass_downloader.command
```

## Windows: `.bat` 더블 클릭하여 실행

혹은 Windows + S -> cmd 입력 후 실행 ->

```batch
eclass_downloader.bat
```

스크립트가 실행되면 순서대로:
1. 가상환경을 확인/생성하고 패키지 설치
2. 쿠키 존재 여부를 확인하고 없다면 수동 생성
   
   **브라우저 창이 자동으로 열립니다. 로그인 한 뒤 종료하지 말고 터미널에서 [Enter] 버튼을 입력해주세요**
4. 브라우저를 headless 모드로 실행하고 쿠키 주입
5. 강좌 ID 입력 → 모듈 목록 수집
6. 다운로드 모드 선택 (전체, 번호, 범위, 제외)
7. m3u8 링크 혹은 MP4 파일 다운로드

다운로드된 결과물은 프로젝트 최상위의 강좌명 폴더 아래에 저장됩니다.

---

## 보안 및 주의사항

- **`bin/cookies.json`** 파일은 절대 공개 저장소에 업로드하지 마세요. 계정 세션이 포함되어 있어 탈취 위험이 있습니다.
- `.gitignore`에 이미 `bin/cookies.json`, `*.mp4`, `*.txt`, `__pycache__/` 등이 설정되어 있습니다.

---

## 기여

1. Fork 저장소
2. 새로운 브랜치에서 수정
3. Pull Request 생성

---

## 라이선스

MIT

