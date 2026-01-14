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
SPREADSHEET_NAME = "도서 리스트"    # 구글 시트 제목 (정확해야 함!)

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
    """구글 시트 로그 저장 (Invalid JWT 에러 해결 버전)"""
    try:
        # 1. Secrets 확인
        if "gcp_service_account" not in st.secrets:
            st.error("❌ Streamlit Secrets 설정이 필요합니다!")
            return

        # 2. 키 정보 가져오기 및 '줄바꿈' 문자 수동 보정 (핵심!)
        # st.secrets 객체를 일반 dict로 변환
        key_dict = dict(st.secrets["gcp_service_account"])
        
        # [!!!여기가 제일 중요합니다!!!]
        # TOML에서 문자열로 들어온 \n을 실제 줄바꿈 문자로 변경해줍니다.
        if "private_key" in key_dict:
            key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")

        # 3. 구글 연동
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        client = gspread.authorize(creds)

        # 4. 시트 열기
        sh = client.open(SPREADSHEET_NAME)
        
        # 5. 워크시트 선택 (없으면 생성)
        try:
            worksheet = sh.worksheet("log")
        except:
            worksheet = sh.add_worksheet(title="log", rows="1000", cols="5")
            worksheet.append_row(["날짜_시간", "이벤트"])
        
        # 6. 데이터 쓰기
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_row([now, action_name])
        
    except Exception as e:
        # 에러 내용을 자세히 출력해서 디버깅
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
    .stButton>button:hover { background-color: #357ABD; transform: scale(1.02); }
    .book-card {
        background-color: white; padding: 20px; border-radius: 15px;
        margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #4A90E2;
    }
    </style>
    """, unsafe_allow_html=True)

def get_aily_image(state):
    if state == "idle": return "aily_idle.png"
    elif state == "thinking": return "aily_thinking.png"
    elif state == "happy": return "aily_happy.png"
    return "aily_idle.png"

# -------------------------------------------------
# 4. 메인 화면
# -------------------------------------------------
st.title("🌟 AILY의 반짝반짝 도서 추천")
st.write("---")

df = load_data()

col1, col2 = st.columns([1, 2])

with col1:
    img_placeholder = st.empty()
    try:
        current_img = get_aily_image(st.session_state.status)
        img_placeholder.image(current_img, use_container_width=True)
    except:
        img_placeholder.write("🤖")

with col2:
    if st.session_state.status == "idle":
        st.chat_message("assistant").write("AILY: 카테고리를 골라주세요!")
    elif st.session_state.status == "thinking":
        st.chat_message("assistant").write("AILY: 서가 뒤지는 중! 🏃💨")
    elif st.session_state.status == "happy":
        st.chat_message("assistant").write("AILY: 추천 도서 도착! 😎")

st.subheader("📍 오늘의 기분을 골라주세요!")

if not df.empty and '카테고리' in df.columns:
    categories = df['카테고리'].unique().tolist()
    user_choice = st.radio("카테고리 선택", categories, index=None, key="category_input")

    def pick_a_book(trigger_source):
        # 1. 로그 저장 시도 (에러나도 앱은 멈추지 않게 try-except는 함수 내부에 있음)
        log_to_sheet(trigger_source)

        # 2. 이미지 변경
        try: img_placeholder.image("aily_thinking.png", use_container_width=True)
        except: pass
        st.session_state.status = "thinking"
        
        with st.spinner('AILY가 책 찾는 중...'):
            time.sleep(1.2)
        
        filtered_books = df[df['카테고리'] == st.session_state.category_input]
        candidates = filtered_books.to_dict('records')
        current_titles = [book['도서명'] for book in st.session_state.history]
        candidates = [b for b in candidates if b['도서명'] not in current_titles]

        if not candidates:
             candidates = filtered_books.to_dict('records')

        if candidates:
            selected_book = random.choice(candidates)
            st.session_state.history.append(selected_book)
            if len(st.session_state.history) > 3:
                st.session_state.history.pop(0)
            st.session_state.status = "happy"
        else:
            st.warning("책이 없어요!")
            st.session_state.status = "idle"

    if len(st.session_state.history) == 0:
        if user_choice:
            if st.button("책 찾아오기 (클릭!)"):
                pick_a_book("책 찾아오기 클릭")
                st.rerun()
    else:
        pass 

else:
    st.error("데이터 로드 실패")

if st.session_state.status == "happy" and st.session_state.history:
    st.write("---")
    st.success(f"### 📚 AILY의 추천 리스트 ({len(st.session_state.history)}/3)")

    for idx, book in enumerate(st.session_state.history):
        title = book.get('도서명', '')
        author = book.get('저자', '')
        comment = book.get('한마디', '')
        
        st.markdown(f"""
        <div class="book-card">
            <h4>📖 {idx+1}. {title}</h4>
            <p>✍️ {author}</p>
            <p style="color: #555;">💬 {comment}</p>
        </div>
        """, unsafe_allow_html=True)

    if st.button("다른 책도 추천해줘! (리스트 추가)"):
        if st.session_state.get("category_input"):
            pick_a_book("다른 책 추천 클릭")
            st.rerun()
        else:
            st.warning("카테고리 선택 필요!")

    if st.button("리스트 비우기"):
        st.session_state.history = []
        st.session_state.status = "idle"
        st.rerun()
