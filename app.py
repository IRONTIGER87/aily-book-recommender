import streamlit as st
import pandas as pd
import random
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# -------------------------------------------------
# 1. 페이지 기본 설정
# -------------------------------------------------
st.set_page_config(
    page_title="귀염둥이 사서 AILY의 추천",
    page_icon="✨",
    layout="centered"
)

# [설정]
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSaXBhEqbAxaH2cF6kjW8tXoNLC8Xb430gB9sb_xMjT5HvSe--sXDGUGp-aAOGrU3lQPjZUA2Tu9OlS/pub?gid=0&single=true&output=csv"
SPREADSHEET_NAME = "도서 리스트"    # 구글 시트 제목

# -------------------------------------------------
# 2. 데이터 로드 및 구글 시트 연결
# -------------------------------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"❌ 데이터 로드 실패: {e}")
        return pd.DataFrame()

def log_to_sheet(action_name):
    """구글 시트 로그 저장 (Streamlit Secrets 사용)"""
    try:
        # 1. 구글 연동 (Secrets에서 키 가져오기)
        # 중요: Secrets에 저장된 키 정보를 사전(dict) 형태로 가져옵니다.
        if "gcp_service_account" not in st.secrets:
            st.error("❌ Streamlit Secrets 설정이 안 되어 있습니다! [Settings] -> [Secrets]를 확인해주세요.")
            return

        key_dict = dict(st.secrets["gcp_service_account"])
        
        # 줄바꿈 문자 오류 방지 (가장 중요한 부분!)
        key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        client = gspread.authorize(creds)

        # 2. 시트 열기
        sh = client.open(SPREADSHEET_NAME)
        
        # 3. 워크시트 선택 (없으면 생성)
        try:
            worksheet = sh.worksheet("log")
        except:
            worksheet = sh.add_worksheet(title="log", rows="1000", cols="5")
            worksheet.append_row(["날짜_시간", "이벤트"])
        
        # 4. 데이터 쓰기
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_row([now, action_name])
        
    except Exception as e:
        st.error(f"❌ 로그 저장 에러: {e}")

# 세션 상태 초기화
if "status" not in st.session_state:
    st.session_state.status = "idle"
if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------------------------------
# 3. CSS & 이미지 헬퍼
# -------------------------------------------------
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button {
        width: 100%; border-radius: 20px; height: 3em;
        background-color: #4A90E2; color: white; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #
