import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime
import json

# -------------------------------------------------
# 1. 페이지 설정
# -------------------------------------------------
st.set_page_config(page_title="AILY 추천", page_icon="✨")

# 설정
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSaXBhEqbAxaH2cF6kjW8tXoNLC8Xb430gB9sb_xMjT5HvSe--sXDGUGp-aAOGrU3lQPjZUA2Tu9OlS/pub?gid=0&single=true&output=csv"
SPREADSHEET_NAME = "도서 리스트"

# 라이브러리 체크
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

def log_to_sheet(action_name):
    if not GSPREAD_AVAILABLE: return

    try:
        # [수정] Secrets에서 필드별로 가져오기
        if "gcp_service_account" not in st.secrets:
            st.error("Secrets 설정 오류: [gcp_service_account]가 없습니다.")
            return

        # dict로 변환 후 줄바꿈 문자 강제 치환 (핵심!)
        key_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in key_dict:
            # 문자열 "\\n"을 실제 엔터키 "\n"으로 변경
            key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        client = gspread.authorize(creds)
        sh = client.open(SPREADSHEET_NAME)
        
        try: worksheet = sh.worksheet("log")
        except: 
            worksheet = sh.add_worksheet(title="log", rows="1000", cols="5")
            worksheet.append_row(["날짜_시간", "이벤트"])
            
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_row([now, action_name])
        
    except Exception as e:
        st.warning(f"로그 저장 실패: {e}")

# -------------------------------------------------
# 메인 로직
# -------------------------------------------------
if "status" not in st.session_state: st.session_state.status = "idle"
if "history" not in st.session_state: st.session_state.history = []

# 스타일
st.markdown("""<style>.stButton>button {width: 100%; border-radius: 20px; background-color: #4A90E2; color: white;}</style>""", unsafe_allow_html=True)

df = load_data()
col1, col2 = st.columns([1, 2])

with col1:
    img = st.empty()
    try: img.image(f"aily_{st.session_state.status}.png")
    except: img.write("🤖")

with col2:
    if st.session_state.status == "idle": st.write("AILY: 카테고리를 골라주세요!")
    elif st.session_state.status == "thinking": st.write("AILY: 찾는 중... 🏃")
    elif st.session_state.status == "happy": st.write("AILY: 찾았다! 😎")

if not df.empty and '카테고리' in df.columns:
    cat = st.radio("카테고리", df['카테고리'].unique(), key="category_input")

    def pick():
        log_to_sheet("클릭함")
        st.session_state.status = "thinking"
        try: img.image("aily_thinking.png")
        except: pass
        time.sleep(1)
        
        pool = df[df['카테고리'] == st.session_state.category_input].to_dict('records')
        hist = [b['도서명'] for b in st.session_state.history]
        cand = [b for b in pool if b['도서명'] not in hist]
        if not cand: cand = pool
        
        if cand:
            st.session_state.history.append(random.choice(cand))
            if len(st.session_state.history) > 3: st.session_state.history.pop(0)
            st.session_state.status = "happy"
        else:
            st.session_state.status = "idle"

    if len(st.session_state.history) == 0:
        if cat and st.button("책 찾아오기"): pick(); st.rerun()
    
    if st.session_state.status == "happy":
        st.success(f"추천 리스트 ({len(st.session_state.history)}/3)")
        for b in st.session_state.history:
            st.info(f"📖 {b['도서명']} / ✍️ {b['저자']}")
            
        if st.button("다른 책도 추천해줘!"): pick(); st.rerun()
        if st.button("리셋"): 
            st.session_state.history = []
            st.session_state.status = "idle"
            st.rerun()
