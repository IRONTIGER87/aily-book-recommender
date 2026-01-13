import streamlit as st
import pandas as pd
import random
import time

# -------------------------------------------------
# 1. 페이지 기본 설정
# -------------------------------------------------
st.set_page_config(
    page_title="귀염둥이 사서 AILY의 추천",
    page_icon="✨",
    layout="centered"
)

# [설정] 구글 스프레드시트 CSV 링크
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSaXBhEqbAxaH2cF6kjW8tXoNLC8Xb430gB9sb_xMjT5HvSe--sXDGUGp-aAOGrU3lQPjZUA2Tu9OlS/pub?gid=0&single=true&output=csv"

# -------------------------------------------------
# 2. 데이터 로드 및 초기화
# -------------------------------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip() # 공백 제거 안전장치
        return df
    except Exception as e:
        return pd.DataFrame()

# 세션 상태 초기화
if "status" not in st.session_state:
    st.session_state.status = "idle" # idle(대기) | thinking(생각) | happy(완료)
if "result" not in st.session_state:
    st.session_state.result = None
if "last_book" not in st.session_state:
    st.session_state.last_book = None

# -------------------------------------------------
# 3. 커스텀 CSS (요청하신 스타일 유지)
# -------------------------------------------------
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #4A90E2;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #357ABD;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# 4. 헬퍼 함수: AILY 이미지 표시
# -------------------------------------------------
def show_aily_image(state):
    try:
        if state == "idle":
            st.image("aily_idle.png", use_container_width=True)
        elif state == "thinking":
            st.image("aily_thinking.png", use_container_width=True)
        elif state == "happy":
            st.image("aily_happy.png", use_container_width=True)
    except:
        if state == "idle": st.write("# 🤖✨")
        elif state == "thinking": st.write("# 🤖🌀")
        elif state == "happy": st.write("# 🤖💖")

# -------------------------------------------------
# 5. 메인 화면 구성
# -------------------------------------------------
st.title("🌟 AILY의 반짝반짝 도서 추천")
st.write("---")

df = load_data()

# [레이아웃] 캐릭터(좌) + 말풍선(우)
col1, col2 = st.columns([1, 2])

with col1:
    show_aily_image(st.session_state.status)

with col2:
    if st.session_state.status == "idle":
        st.chat_message("assistant").write(
            "**AILY:** 안녕하세요! 도서관 귀염둥이 4년 차 사서 AILY 등장! "
            "오늘은 어떤 기분이신가요? 제가 이용자님 마음을 콕! 집어낼 책을 찾아올게요! (두근두근)"
        )
    elif st.session_state.status == "thinking":
        st.chat_message("assistant").write(
            "**AILY:** 으랏차차! 서가 깊숙한 곳까지 뒤지고 있어요! 잠시만요! 🏃💨"
        )
    elif st.session_state.status == "happy":
        st.chat_message("assistant").write(
            "**AILY:** 짜잔! 이용자님을 위한 완벽한 책을 찾아왔어요! 어때요, 맘에 드시나요? 😎"
        )

# -------------------------------------------------
# 6. 사용자 입력 및 로직
# -------------------------------------------------
st.subheader("📍 오늘의 기분을 골라주세요!")

# 데이터가 있을 때만 실행
if not df.empty and '카테고리' in df.columns:
    categories = df['카테고리'].unique().tolist()
    
    # 라디오 버튼 (key='category_input'으로 세션에 저장됨)
    user_choice = st.radio(
        "카테고리를 선택하면 AILY가 움직여요!",
        categories,
        index=None,
        key="category_input"
    )

    # 선택 시 버튼 활성화
    if user_choice:
        if st.button("책 찾아오기 (클릭!)"):
            st.session_state.status = "thinking"
            
            with st.spinner('AILY가 서가에서 열심히 뛰어다니는 중... 🏃💨'):
                time.sleep(1.2)
            
            # [핵심 로직] 필터링 & 중복 방지
            filtered_books = df[df['카테고리'] == user_choice]
            candidates = filtered_books.to_dict('records')

            # 직전 추천 도서 제외
            if len(candidates) > 1 and st.session_state.last_book:
                candidates = [b for b in candidates if b['도서명'] != st.session_state.last_book]

            if candidates:
                selected_book = random.choice(candidates)
                st.session_state.result = selected_book
                st.session_state.last_book = selected_book['도서명']
                st.session_state.status = "happy"
                st.rerun()
            else:
                st.warning("어라? 해당 카테고리에 책이 없네요 ㅠㅠ")
                st.session_state.status = "idle"

else:
    st.error("서가가 비어있거나 연결되지 않았어요!")

# -------------------------------------------------
# 7. 결과 출력 (UI 프레임 유지)
# -------------------------------------------------
if st.session_state.status == "happy" and st.session_state.result:
    st.balloons() # 축하 효과
    
    st.success(f"### 🎯 AILY가 찾은 '인생 책'!")
    
    # 결과 박스
    container = st.container(border=True)
    
    title = st.session_state.result.get('도서명', '제목 없음')
    author = st.session_state.result.get('저자', '저자 미상')
    comment = st.session_state.result.get('한마디', '코멘트 없음')

    container.write(f"📖 **도서명:** {title}")
    container.write(f"✍️ **저자:** {author}")
    container.info(f"💬 **AILY의 한마디:** {comment}")
    
    st.chat_message("assistant").write(
        f"헤헤, **[{title}]** 이 책은 진짜 강추예요! "
        "다 읽으시면 저한테 꼭 후기 알려주셔야 해요! 약속~! 🤗✨"
    )

    # -----------------------------------------------------------
    # [수정된 부분] 버튼 클릭 시 같은 카테고리에서 다시 뽑기
    # -----------------------------------------------------------
    if st.button("다른 책도 추천해줘! (새로고침)"):
        # 1. 현재 선택된 카테고리 가져오기
        current_cat = st.session_state.get("category_input")
        
        if current_cat and not df.empty:
            # 2. 로직 재실행 (필터링 및 추첨)
            filtered_books = df[df['카테고리'] == current_cat]
            candidates = filtered_books.to_dict('records')

            # 직전 추천 도서 제외 (연속 중복 방지)
            if len(candidates) > 1 and st.session_state.last_book:
                candidates = [b for b in candidates if b['도서명'] != st.session_state.last_book]

            if candidates:
                new_book = random.choice(candidates)
                st.session_state.result = new_book
                st.session_state.last_book = new_book['도서명']
                # 상태는 'happy' 그대로 유지
                st.session_state.status = "happy"
                st.rerun()
            else:
                st.warning("이 카테고리에는 더 이상 추천할 책이 없어요!")
        else:
            # 혹시라도 카테고리 선택이 풀렸다면 초기화
            st.session_state.status = "idle"
            st.rerun()

elif st.session_state.status == "idle":
    st.info("AILY: 이용자님! 메뉴에서 하나만 골라주세요! 제가 바로 달려갈 준비 완료됐거든요! 😤")

# -------------------------------------------------
# 8. 푸터
# -------------------------------------------------
st.write("---")
st.caption("© 2026 AI Librarian AILY - Simgok Library Project")
