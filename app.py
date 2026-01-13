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
    st.session_state.status = "idle" # idle | thinking | happy
if "history" not in st.session_state:
    st.session_state.history = [] # 추천된 책들을 저장할 리스트 (최대 3개)

# -------------------------------------------------
# 3. 커스텀 CSS
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
    /* 결과 카드 스타일 */
    .book-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #4A90E2;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# 4. 헬퍼 함수: AILY 이미지 표시
# -------------------------------------------------
def get_aily_image(state):
    """상태에 따른 이미지 파일명 반환"""
    if state == "idle": return "aily_idle.png"
    elif state == "thinking": return "aily_thinking.png"
    elif state == "happy": return "aily_happy.png"
    return "aily_idle.png"

# -------------------------------------------------
# 5. 메인 화면 구성
# -------------------------------------------------
st.title("🌟 AILY의 반짝반짝 도서 추천")
st.write("---")

df = load_data()

# [레이아웃] 캐릭터(좌) + 말풍선(우)
col1, col2 = st.columns([1, 2])

# 왼쪽 캐릭터 영역 (placeholder 사용으로 실시간 교체 가능하게 함)
with col1:
    img_placeholder = st.empty() # 빈 공간 확보
    
    # 현재 상태에 맞는 이미지 표시
    current_img = get_aily_image(st.session_state.status)
    try:
        img_placeholder.image(current_img, use_container_width=True)
    except:
        img_placeholder.write("🤖") # 이미지 없을 때 대체

# 오른쪽 말풍선 영역
with col2:
    if st.session_state.status == "idle":
        st.chat_message("assistant").write(
            "**AILY:** 안녕하세요! 도서관 귀염둥이 사서 AILY입니다! "
            "원하시는 카테고리를 골라주세요! (최대 3권까지 모아서 보여드릴게요!)"
        )
    elif st.session_state.status == "thinking":
        st.chat_message("assistant").write(
            "**AILY:** 으랏차차! 서가 깊숙한 곳까지 뒤지고 있어요! 잠시만요! 🏃💨"
        )
    elif st.session_state.status == "happy":
        st.chat_message("assistant").write(
            "**AILY:** 짜잔! 여기 이용자님을 위한 추천 도서 리스트입니다! 😎"
        )

# -------------------------------------------------
# 6. 사용자 입력 및 로직
# -------------------------------------------------
st.subheader("📍 오늘은 어떤 분야의 도서를 추천해 드릴까요?")

if not df.empty and '카테고리' in df.columns:
    categories = df['카테고리'].unique().tolist()
    
    # 라디오 버튼
    user_choice = st.radio(
        "카테고리를 선택하면 AILY가 움직여요!",
        categories,
        index=None,
        key="category_input"
    )

    # -------------------------------------------------------
    # [로직 함수] 책 한 권 뽑아서 history에 추가하기
    # -------------------------------------------------------
    def pick_a_book():
        # 1. 이미지 즉시 변경 (thinking)
        try:
            img_placeholder.image("aily_thinking.png", use_container_width=True)
        except:
            pass
        
        st.session_state.status = "thinking"
        
        # 2. 로딩 효과
        with st.spinner('AILY가 서가에서 책을 꺼내오는 중...'):
            time.sleep(1.2)
        
        # 3. 책 추천 로직
        filtered_books = df[df['카테고리'] == st.session_state.category_input]
        candidates = filtered_books.to_dict('records')

        # 현재 리스트에 있는 책들은 가급적 제외 (중복 방지)
        current_titles = [book['도서명'] for book in st.session_state.history]
        candidates = [b for b in candidates if b['도서명'] not in current_titles]

        # 만약 남은 후보가 없으면(다 뽑았으면) 전체에서 다시 뽑기
        if not candidates:
             candidates = filtered_books.to_dict('records')

        if candidates:
            selected_book = random.choice(candidates)
            
            # [핵심] 리스트에 추가 (최대 3개 유지)
            st.session_state.history.append(selected_book)
            if len(st.session_state.history) > 3:
                st.session_state.history.pop(0) # 가장 오래된 것 삭제
                
            st.session_state.status = "happy"
        else:
            st.warning("이 카테고리에는 책이 더 이상 없어요!")
            st.session_state.status = "idle"

    # -------------------------------------------------------
    # [버튼 표시]
    # -------------------------------------------------------
    # 리스트가 비어있으면 '시작 버튼', 있으면 '추가 추천 버튼'
    if len(st.session_state.history) == 0:
        if user_choice:
            if st.button("책 찾아오기 (클릭!)"):
                pick_a_book()
                st.rerun()
    else:
        # 리스트가 있을 때 하단에 '다른 책도 추천해줘' 버튼 표시
        # (주의: UI 상단에 두기 위해 여기서 렌더링하지 않고, 리스트 출력 후 아래에 배치할 수도 있음.
        #  여기서는 로직 흐름상 리스트 출력 후 버튼을 두는 것이 자연스러우므로 아래쪽(Section 7)에서 처리)
        pass 

else:
    st.error("서가가 비어있거나 연결되지 않았어요!")

# -------------------------------------------------
# 7. 결과 출력 (누적 리스트 형태)
# -------------------------------------------------
if st.session_state.status == "happy" and st.session_state.history:
    
    st.write("---")
    st.success(f"### 📚 AILY의 추천 리스트 ({len(st.session_state.history)}/3)")

    # [핵심] 누적된 리스트 출력 (최신이 아래로 쌓임)
    for idx, book in enumerate(st.session_state.history):
        title = book.get('도서명', '제목 없음')
        author = book.get('저자', '저자 미상')
        comment = book.get('한마디', '코멘트 없음')
        
        # HTML/CSS로 카드 디자인 직접 구현
        st.markdown(f"""
        <div class="book-card">
            <h4>📖 {idx+1}. {title}</h4>
            <p>✍️ <b>저자:</b> {author}</p>
            <p style="color: #555;">💬 <b>AILY's Pick:</b> {comment}</p>
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------------------------------------
    # [버튼] 하단에 '다른 책도 추천해줘!' 배치
    # -----------------------------------------------------------
    if st.button("다른 책도 추천해줘! (리스트 추가)"):
        # 카테고리가 선택되어 있는지 확인
        if st.session_state.get("category_input"):
            pick_a_book() # 함수 재사용
            st.rerun()
        else:
            st.warning("카테고리를 먼저 선택해주세요!")

    # 리셋 버튼 (선택 사항)
    if st.button("리스트 비우기 (처음부터)"):
        st.session_state.history = []
        st.session_state.status = "idle"
        st.rerun()

elif st.session_state.status == "idle":
    st.info("👆 위에서 카테고리를 선택하고 버튼을 눌러보세요!")

# -------------------------------------------------
# 8. 푸터
# -------------------------------------------------
st.write("---")
st.caption("© 2026 AI Librarian AILY - Simgok Library Project")
