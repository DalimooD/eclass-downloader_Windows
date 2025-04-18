# bin/save_cookies.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Canvas & eClass 쿠키 캡처 (bin/에 저장)"""
import json, sys, pathlib, time
from selenium import webdriver

BASE=pathlib.Path(__file__).resolve().parent
PROFILE=BASE/"selenium-profile"
COOKIES=BASE/"cookies.json"

print("[INFO ] 로그인을 완료하면 명령창으로 돌아와 Enter를 입력해주십시오.\n")
time.sleep(3)

opts=webdriver.ChromeOptions()
opts.add_argument(f"--user-data-dir={PROFILE}")
driver=webdriver.Chrome(options=opts)
print("[INIT ] 브라우저 실행")

# Canvas
driver.get("https://canvas.cau.ac.kr/login?type=integrated")
input("Canvas 로그인 후 Enter ▶ ")
canvas=driver.get_cookies(); print(f"[INFO ] Canvas {len(canvas)}개\n")

# eClass
driver.get("https://eclass3.cau.ac.kr/courses/")
input("eClass 모듈 화면 확인 후 Enter ▶ ")
eclass=driver.get_cookies(); print(f"[INFO ] eClass {len(eclass)}개\n")

driver.quit()
merged={(c['name'],c['domain']):c for c in canvas+eclass}.values()
with open(COOKIES,'w') as f: json.dump(list(merged),f,indent=2)
print(f"[SAVE ] cookies.json 저장 ({len(merged)}개 쿠키)")