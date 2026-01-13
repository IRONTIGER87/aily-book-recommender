import streamlit as st
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

# -------------------------------------------------
# 2. 커스텀 CSS
# -------------------------------------------------
st.markdown("""
<style>
.main {
    background-color: #f0f2f6;
}
.stButton > button {
    width: 100%;
    border-radius: 20px;
    height: 3em;
    background-color: #4A90E2;
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 3. 도서 데이터베이스
# -------------------------------------------------
book_db = {
    "포근한 위로가 필요해 (힐링)": [
        {"title": "불편한 편의점", "author": "김호연", "comment": "마음이 말랑말랑해지는 기적이 일어날 거예요!"},
        {"title": "메리골드 마음 세탁소", "author": "윤정은", "comment": "슬픈 기억은 제가 싹~ 세탁해 드릴게요!"},
        {"title": "보노보노처럼 살다니 다행이야", "author": "김신회", "comment": "서툴러도 괜찮아요, 우리 천천히 가요!"}
    ],
    "갓생 살고 싶어! (자기계발)": [
        {"title": "원씽", "author": "게리 켈러", "comment": "딱 하나에만 집중! 선배님은 할 수 있어요!"},
        {"title": "역행자", "author": "자청", "comment": "운명의 자동장치를 해체하러 가볼까요?"},
        {"title": "아주 작은 습관의 힘", "author": "제임스 클리어", "comment": "매일 1%씩만 성장해봐요!"}
    ],
    "미래가 궁금해 (IT/과학)": [
        {"title": "AI 2041", "author": "리 카이푸", "comment": "우리가 살게 될 미래를 함께 엿봐요!"},
        {"title": "하늘과 바람과 별과 인간", "author": "김상욱", "comment": "우주는 정말 신비로워요!"},
        {"title": "도둑맞은 집중력", "author": "요한 하리", "comment": "집중력을 같이 되찾아볼까요?"}
    ]
}

# -------------------------------------------------
# 4. 세션 상태 초기화
# -------------------------------------------------
if "choice" not in st.session_state:
    st.session_state.choice = None

if "result" not in st.session_state:
    st.session_state.result = None

if "status" not in st.session_state:
    st.session_state.status = "idle"  # idle | thinking | happy

# -------------------------------------------------
# 5. 캐릭터 출력 함수
# -------------------------------------------------
def show_aily(state: str):
    if state == "idle":
        st.write("🤖✨")
        st.caption("AILY 대기 중…")
    elif state == "thinking":
        st.write("🤖💭")
        st.caption("AILY 생각 중…")
    elif state == "happy":
        st.write("🤖🎉")
        st.caption("추천 완료!")

# -------------------------------------------------
# 6. 메인 화면
# -------------------------------------------------
st.title("🌟 AILY의 반짝반짝 도서 추천")
st.write("---")

col_char, col_chat = st.columns([1, 2])

with col_char:
    show_aily(st.session_state.status)

with col_chat:
    st.chat_message("assistant").write(
        "**AILY:** 선배님 안녕하세요! "
        "오늘 기분에 딱 맞는 책을 제가 직접 골라드릴게요!"
    )

# -------------------------------------------------
# 7. 사용자 선택
# -------------------------------------------------
st.subheader("📍 오늘의 기분을 골라주세요!")

choice = st.radio(
    "카테고리를 선택하세요",
    list(book_db.keys()),
    index=None
)

if choice:
    if st.session_state.choice != choice:
        st.session_state.choice = choice
        st.session_state.result = None
        st.session_state.status = "thinking"

# -------------------------------------------------
# 8. 추천 생성 (thinking 유지 → 결과 시 happy)
# -------------------------------------------------
if st.session_state.status == "thinking" and st.session_state.result is None:
    with st.spinner("AILY가 서가에서 열심히 책을 찾고 있어요..."):
        time.sleep(1.5)

    st.session_state.result = random.choice(
        book_db[st.session_state.choice]
    )
    st.session_state.status = "happy"
    st.rerun()

# -------------------------------------------------
# 9. 결과 출력
# -------------------------------------------------
if st.session_state.result:
    st.balloons()

    st.success("### 🎯 AILY의 추천 도서!")

    box = st.container(border=True)
    box.write(f"📖 **도서명:** {st.session_state.result['title']}")
    box.write(f"✍️ **저자:** {st.session_state.result['author']}")
    box.info(f"💬 **AILY의 한마디:** {st.session_state.result['comment']}")

    st.chat_message("assistant").write(
        "마음에 드셨나요? 다 읽고 나면 꼭 후기 들려주세요!"
    )

    if st.button("📚 다른 책도 추천받기"):
        st.session_state.result = None
        st.session_state.status = "thinking"
        st.rerun()

# ------------------------------------------------
# 10. 아무 선택도 안 했을 때
# -------------------------------------------------
if st.session_state.status == "idle":
    st.info("AILY: 카테고리를 하나 골라주시면 바로 움직일게요!")

# -------------------------------------------------
# 11. 푸터
# -------------------------------------------------
st.write("---")
st.caption("© 2026 AI Librarian AILY - Simgok Library Project")
