import streamlit as st
import pandas as pd
import random
import time

# -------------------------------------------------
# 1. 설정 및 데이터 로드
# -------------------------------------------------
st.set_page_config(page_title="AILY의 도서 추천", page_icon="✨", layout="centered")

# [중요] 여기에 단계 1에서 복사한 CSV 링크를 붙여넣으세요.
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSaXBhEqbAxaH2cF6kjW8tXoNLC8Xb430gB9sb_xMjT5HvSe--sXDGUGp-aAOGrU3lQPjZUA2Tu9OlS/pub?gid=0&single=true&output=csv"

# 데이터 캐싱 (새로고침 시 서버 부하를 줄임, 1분마다 갱신)
@st.cache_data(ttl=60)
def load_data():
    try:
        # 구글 시트 CSV 읽어오기
        df = pd.read_csv(SHEET_URL)
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는데 실패했어요: {e}")
        return pd.DataFrame()

# -------------------------------------------------
# 2. 스타일 및 함수
# -------------------------------------------------
st.markdown("""
<style>
.stButton > button {
    width: 100%; border-radius: 15px; background-color: #4A90E2; color: white;
}
</style>
""", unsafe_allow_html=True)

def show_aily(state):
    # 이미지는 app.py와 같은 폴더에 있어야 합니다.
    # 만약 이미지가 없다면 에러 방지를 위해 텍스트로 대체하거나 try-except 처리 필요
    try:
        if state == "idle":
            st.image("aily_idle.png", use_container_width=True)
            st.caption("대기 중...")
        elif state == "thinking":
            st.image("aily_thinking.png", use_container_width=True)
            st.caption("생각 중...")
        elif state == "happy":
            st.image("aily_happy.png", use_container_width=True)
            st.caption("찾았다!")
    except:
        st.warning("이미지 파일(aily_idle.png 등)이 같은 폴더에 있는지 확인해주세요.")

# -------------------------------------------------
# 3. 상태 관리 초기화
# -------------------------------------------------
if "status" not in st.session_state:
    st.session_state.status = "idle"
if "result" not in st.session_state:
    st.session_state.result = None
if "last_book" not in st.session_state:
    st.session_state.last_book = None # 직전 추천 도서 저장용

# -------------------------------------------------
# 4. 메인 로직
# -------------------------------------------------
st.title("🌟 AILY의 추천도서")
st.write("---")

df = load_data()

col1, col2 = st.columns([1, 2])
with col1:
    show_aily(st.session_state.status)
with col2:
    st.info("안녕하세요! 실시간으로 추천 도서를 가져올게요.")

# 카테고리 선택
categories = df['카테고리'].unique().tolist() if not df.empty else []
choice = st.radio("기분을 선택하세요:", categories, horizontal=True)

# 추천 버튼
if st.button("책 추천받기 📚"):
    if df.empty:
        st.error("데이터가 비어있습니다. 데이터 링크를 확인해주세요.")
    else:
        st.session_state.status = "thinking"
        
        # '생각 중' 효과를 위한 임시 렌더링 (st.rerun 대신 sleep 활용)
        with st.spinner("서가 뒤지는 중..."):
            time.sleep(1.2)
        
        # 1. 해당 카테고리 책만 필터링
        filtered_books = df[df['카테고리'] == choice]
        
        # 2. 직전 추천 도서 제외 로직 (핵심)
        # 만약 책이 1권뿐이라면 제외하지 않음 (무한루프 방지)
        candidates = filtered_books.to_dict('records')
        
        if len(candidates) > 1 and st.session_state.last_book:
            candidates = [book for book in candidates if book['도서명'] != st.session_state.last_book]

        # 3. 랜덤 선택
        if candidates:
            selected_book = random.choice(candidates)
            st.session_state.result = selected_book
            st.session_state.last_book = selected_book['도서명'] # 이번 책을 '마지막 책'으로 저장
            st.session_state.status = "happy"
        else:
            st.warning("추천할 책이 없어요!")
        
        st.rerun()

# -------------------------------------------------
# 5. 결과 화면
# -------------------------------------------------
if st.session_state.status == "happy" and st.session_state.result:
    st.success("### 📖 추천 도서 도착!")
    st.write(f"**제목:** {st.session_state.result['도서명']}")
    st.write(f"**저자:** {st.session_state.result['저자']}")
    st.info(f"💌 **AILY:** {st.session_state.result['한마디']}")
