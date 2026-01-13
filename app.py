import streamlit as st
import random
import time

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="귀염둥이 사서 AILY의 추천",
    page_icon="✨",
    layout="centered"
)

# 2. 커스텀 CSS
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
    }
    </style>
""", unsafe_allow_html=True)

# 3. 도서 데이터베이스 (comment 키로 통일)
book_db = {
    "포근한 위로가 필요해 (힐링)": [
        {"title": "불편한 편의점", "author": "김호연", "comment": "마음이 말랑말랑해지는 기적이 일어날 거예요! 💖"},
        {"title": "메리골드 마음 세탁소", "author": "윤정은", "comment": "슬픈 기억은 제가 싹~ 세탁해 드릴게요! 🫧"},
        {"title": "보노보노처럼 살다니 다행이야", "author": "김신회", "comment": "서툴러도 괜찮아요, 우리 천천히 가요! 🦦"}
    ],
    "갓생 살고 싶어! (자기계발)": [
        {"title": "원씽", "author": "게리 켈러", "comment": "딱 하나에만 집중! 선배님은 할 수 있어요! 🔥"},
        {"title": "역행자", "author": "자청", "comment": "운명의 자동장치를 해체하러 가볼까요? 슝~! 🚀"},
        {"title": "아주 작은 습관의 힘", "author": "제임스 클리어", "comment": "매일 1%씩만 성장해봐요, 저랑 약속! 🤙"}
    ],
    "미래가 궁금해 (IT/과학)": [
        {"title": "AI 2041", "author": "리 카이푸", "comment": "우리가 살게 될 미래, 제가 미리 보여드릴게요! 🤖"},
        {"title": "하늘과 바람과 별과 인간", "author": "김상욱", "comment": "우주는 정말 신비로워요! 선배님도 궁금하시죠? ✨"},
        {"title": "도둑맞은 집중력", "author": "요한 하리", "comment": "앗! 집중력을 누가 가져갔을까요? 같이 찾아봐요! 👀"}
    ]
}

# 4. 메인 화면
st.title("🌟 AILY의 반짝반짝 도서 추천")
st.write("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.write("# 🤖✨")

with col2:
    st.chat_message("assistant").write(
        "**AILY:** 선배님, 안녕! 도서관 귀염둥이 4년 차 사서 AILY 등장! "
        "오늘은 어떤 기분이신가요? 제가 딱 맞는 책을 찾아올게요!"
    )

# 5. 사용자 입력 (radio 올바른 사용)
st.subheader("📍 오늘의 기분을 골라주세요!")

options = ["선택해주세요"] + list(book_db.keys())

user_choice = st.radio(
    "카테고리를 선택하면 AILY가 움직여요!",
    options,
    index=0
)

# 6. 추천 로직
if user_choice != "선택해주세요":
    with st.spinner("AILY가 서가를 뒤지는 중... 🏃💨"):
        time.sleep(1.5)

    selected_book = random.choice(book_db[user_choice])

    st.balloons()
    st.success("### 🎯 AILY가 찾은 '인생 책'!")

    box = st.container(border=True)
    box.write(f"📖 **도서명:** {selected_book['title']}")
    box.write(f"✍️ **저자:** {selected_book['author']}")
    box.info(f"💬 **AILY의 한마디:** {selected_book['comment']}")

    st.chat_message("assistant").write(
        f"헤헤, 이 책은 진짜 {user_choice}에 딱이에요! "
        "다 읽고 나면 저한테 꼭 후기 알려주셔야 해요! 🤗"
    )

    if st.button("📚 다른 책도 추천해줘!"):
        st.rerun()

else:
    st.info("AILY: 선배님! 카테고리 하나만 골라주시면 바로 출동할게요! 🚀")

# 7. 푸터
st.write("---")
st.caption("© 2026 AI Librarian AILY - Simgok Library Project")
