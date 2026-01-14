import streamlit as st
import pandas as pd
import random
import time

# ✅ [추가] 로그/시간
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# -------------------------------------------------
# 1. 페이지 기본 설정
# -------------------------------------------------
st.set_page_config(
    page_title="귀염둥이 사서 AILY의 추천",
    page_icon="✨",
    layout="centered"
)

# [설정] 구글 스프레드시트 CSV 링크(읽기)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSaXBhEqbAxaH2cF6kjW8tXoNLC8Xb430gB9sb_xMjT5HvSe--sXDGUGp-aAOGrU3lQPjZUA2Tu9OlS/pub?gid=0&single=true&output=csv"

# ✅ [추가] 로그 적재 Webhook (Apps Script Web App URL)
# Streamlit Cloud 사용 시: st.secrets["LOG_WEBHOOK_URL"], st.secrets["LOG_TOKEN"] 권장
LOG_WEBHOOK_URL = st.secrets.get("LOG_WEBHOOK_URL", "")
LOG_TOKEN = st.secrets.get("LOG_TOKEN", "")

# -------------------------------------------------
# 2. 데이터 로드 및 초기화
# -------------------------------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return pd.DataFrame()

# ✅ [추가] 로그 적재 함수
def append_log(action: str, category: str = "", title: str = ""):
    # 한국 시간
    ts = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")

    # Webhook 없으면 조용히 스킵(개발 중일 때 편함)
    if not LOG_WEBHOOK_URL:
        return

    payload = {
        "token": LOG_TOKEN,          # Apps Script에서 검증용(권장)
        "timestamp": ts,
        "action": action,
        "category": category or "",
        "title": title or "",
    }

    try:
        requests.post(LOG_WEBHOOK_URL, json=payload, timeout=3)
    except Exception:
        # 로그 실패해도 앱이 죽지 않도록(조용히 무시)
        pass

# ✅ [추가] "중복 없이 다음 책" 뽑는 함수
def pick_next_book(df: pd.DataFrame, category: str, exclude_titles: set[str]):
    filtered = df[df["카테고리"] == category].copy()
    if filtered.empty:
        return None

    if exclude_titles:
        filtered = filtered[~filtered["도서명"].isin(exclude_titles)]

    if filtered.empty:
        return None

    # 랜덤 1개
    return filtered.sample(1).iloc[0].to_dict()

# 세션 상태 초기화
if "status" not in st.session_state:
    st.session_state.status = "idle"
if "result" not in st.session_state:
    st.session_state.result = None
if "last_book" not in st.session_state:
    st.session_state.last_book = None

# ✅ [추가] 카테고리별 추천 히스토리
# 형태: { "카테고리A": [ {도서1}, {도서2}, ... ], "카테고리B": [...] }
if "reco_by_cat" not in st.session_state:
    st.session_state.reco_by_cat = {}

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

if not df.empty and '카테고리' in df.columns:
    categories = df['카테고리'].unique().tolist()

    user_choice = st.radio(
        "카테고리를 선택하면 AILY가 움직여요!",
        categories,
        index=None,
        key="category_input"
    )

    if user_choice:
        if st.button("책 찾아오기 (클릭!)"):
            st.session_state.status = "thinking"

            with st.spinner('AILY가 서가에서 열심히 뛰어다니는 중... 🏃💨'):
                time.sleep(1.2)

            # ✅ [수정] 카테고리별 기존 추천 히스토리 가져오기
            history = st.session_state.reco_by_cat.get(user_choice, [])
            already_titles = {b.get("도서명", "") for b in history if b.get("도서명")}

            selected_book = pick_next_book(df, user_choice, already_titles)

            if selected_book:
                # ✅ [수정] 히스토리에 "추가" (기존 출력 유지)
                history.append(selected_book)
                st.session_state.reco_by_cat[user_choice] = history

                st.session_state.result = selected_book
                st.session_state.last_book = selected_book.get('도서명')

                # ✅ [추가] 로그 적재(책 찾아오기)
                append_log(
                    action="책 찾아오기",
                    category=user_choice,
                    title=selected_book.get("도서명", "")
                )

                st.session_state.status = "happy"
                st.rerun()
            else:
                st.warning("어라? 해당 카테고리에 더 이상 추천할 책이 없네요 ㅠㅠ")
                # ✅ [추가] 로그 적재(책 찾아오기 - 실패도 기록하고 싶다면)
                append_log(action="책 찾아오기(없음)", category=user_choice, title="")
                st.session_state.status = "idle"
else:
    st.error("서가가 비어있거나 연결되지 않았어요!")

# -------------------------------------------------
# 7. 결과 출력 (UI 프레임 유지)
# -------------------------------------------------
current_cat = st.session_state.get("category_input")
current_history = st.session_state.reco_by_cat.get(current_cat, []) if current_cat else []

if st.session_state.status == "happy" and current_history:
    st.balloons()
    st.success(f"### 🎯 AILY가 찾은 '인생 책'!")

    # ✅ [수정] "기존 추천된 도서"를 그대로 유지하면서 "리스트로 출력"
    # (포맷: 도서명/저자/한마디 유지)
    for idx, book in enumerate(current_history, start=1):
        container = st.container(border=True)
        title = book.get('도서명', '제목 없음')
        author = book.get('저자', '저자 미상')
        comment = book.get('한마디', '코멘트 없음')

        container.write(f"📖 **도서명:** {title}")
        container.write(f"✍️ **저자:** {author}")
        container.info(f"💬 **AILY의 한마디:** {comment}")
        if idx < len(current_history):
            container.write("---")

    # ✅ [추가] 마지막(최신) 추천 도서로 멘트 유지
    latest = current_history[-1]
    lt = latest.get("도서명", "이 책")
    st.chat_message("assistant").write(
        f"헤헤, **[{lt}]** 이 책은 진짜 강추예요! "
        "다 읽으시면 저한테 꼭 후기 알려주셔야 해요! 약속~! 🤗✨"
    )

    # -----------------------------------------------------------
    # ✅ [수정] "다른 책도 추천해줘!" 누르면 기존 목록 유지 + 중복 없이 추가
    # -----------------------------------------------------------
    if st.button("다른 책도 추천해줘! (새로고침)"):
        current_cat = st.session_state.get("category_input")

        if current_cat and not df.empty:
            history = st.session_state.reco_by_cat.get(current_cat, [])
            already_titles = {b.get("도서명", "") for b in history if b.get("도서명")}

            new_book = pick_next_book(df, current_cat, already_titles)

            if new_book:
                history.append(new_book)
                st.session_state.reco_by_cat[current_cat] = history

                st.session_state.result = new_book
                st.session_state.last_book = new_book.get('도서명')
                st.session_state.status = "happy"

                # ✅ [추가] 로그 적재(다른 책도 추천)
                append_log(
                    action="다른 책도 추천",
                    category=current_cat,
                    title=new_book.get("도서명", "")
                )

                st.rerun()
            else:
                st.warning("이 카테고리에는 더 이상 추천할 책이 없어요!")
                append_log(action="다른 책도 추천(없음)", category=current_cat, title="")
        else:
            st.session_state.status = "idle"
            st.rerun()

elif st.session_state.status == "idle":
    st.info("AILY: 이용자님! 메뉴에서 하나만 골라주세요! 제가 바로 달려갈 준비 완료됐거든요! 😤")

# -------------------------------------------------
# 8. 푸터
# -------------------------------------------------
st.write("---")
st.caption("© 2026 AI Librarian AILY - Simgok Library Project")
