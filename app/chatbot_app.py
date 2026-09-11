import base64
import io
import re
import time
import urllib.parse

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # app/
PROJECT_ROOT = BASE_DIR.parent  # out-traveler/ (레포 루트)
APP_DATA_DIR = BASE_DIR / "app_data"  # 챗봇 전용 데이터
RAW_DIR = PROJECT_ROOT / "data" / "raw"  # 팀 공용 원본 데이터

# =========================================================
# 1. 페이지 설정
# =========================================================
# Out-Traveler 로고 (외부 파일 없이 코드에 포함)
OT_LOGO_B64 = "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"
OT_LOGO_SRC = "data:image/png;base64," + OT_LOGO_B64


def _logo_image():
    import base64 as _b64, io as _io
    from PIL import Image as _Image
    return _Image.open(_io.BytesIO(_b64.b64decode(OT_LOGO_B64)))


st.set_page_config(page_title="Out-Traveler AI chatbot", page_icon=_logo_image(), layout="centered")

# =========================================================
# 2. 디자인 (흰 배경 + 대화형 말풍선)
# =========================================================
st.markdown("""
<style>
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] { background-color: #ffffff !important; }
    [data-testid="stHeader"] { background: transparent !important; }

    .block-container {
        max-width: 620px !important;
        padding: 1.2rem 1.1rem 4rem !important;
        background: #ffffff !important;
        border: none !important;
        box-shadow: none !important;
        margin: 0 auto !important;
        color: #111111 !important;
    }

    /* 스크롤바를 구분선처럼 */
    *::-webkit-scrollbar { width: 8px; height: 8px; }
    *::-webkit-scrollbar-track { background: transparent; }
    *::-webkit-scrollbar-thumb { background: #d3d6da; border-radius: 999px; }
    *::-webkit-scrollbar-thumb:hover { background: #b6babf; }
    * { scrollbar-width: thin; scrollbar-color: #d3d6da transparent; }

    /* ---------- 대화 말풍선 ---------- */
    .ot-row { display: flex; margin: 10px 0; align-items: flex-start; gap: 8px; }
    .ot-row.left  { justify-content: flex-start; }
    .ot-row.right { justify-content: flex-end; }

    .ot-avatar {
        width: 32px; height: 32px; flex: 0 0 32px;
        border-radius: 50%;
        background: #ffffff;
        border: 1px solid #E6F1FB;
        object-fit: contain;
        margin-top: 2px;
    }

    .ot-bubble {
        max-width: 78%;
        padding: 11px 14px;
        border-radius: 16px;
        line-height: 1.6;
        font-size: 0.94rem;
        word-break: break-word;
    }
    .ot-bubble.bot {
        background: #f4f5f7;
        color: #111 !important;
        border-top-left-radius: 4px;
    }
    .ot-bubble.user {
        background: #1B5FA8;
        color: #ffffff !important;
        border-top-right-radius: 4px;
        font-weight: 600;
    }
    .ot-bubble.user * { color: #ffffff !important; }
    .ot-bubble.card {
        background: #ffffff;
        border: 1px solid #e7e9ee;
        max-width: 88%;
    }
    .ot-bubble .t { font-weight: 700; font-size: 0.98rem; }
    .ot-bubble .meta { color: #6b7280 !important; font-size: 0.86rem; }
    .ot-bubble .tag {
        display: inline-block; background: #E6F1FB; color: #0C3D6E !important;
        border-radius: 6px; padding: 1px 7px; font-size: 0.78rem; margin-left: 2px;
    }
    .ot-bubble a { color: #1B5FA8 !important; text-decoration: none; font-weight: 600; }
    .ot-cursor { color: #9aa0a6 !important; }

    .ot-loading { color: #9aa0a6 !important; font-size: 0.92rem; }

    /* ---------- 선택 버튼(퀵리플라이) ---------- */
    /* 지역 그리드: 버튼이 칸을 꽉 채우고 칸 사이 간격을 좁힘 */
    [data-testid="stHorizontalBlock"] {
        gap: 6px !important;
        margin-bottom: 0 !important;
    }
    [data-testid="stHorizontalBlock"] [data-testid="stElementContainer"],
    [data-testid="stHorizontalBlock"] [data-testid="stButton"] { width: 100% !important; }
    [data-testid="stHorizontalBlock"] [data-testid="stColumn"] { padding: 0 !important; }

    div.stButton > button, [data-testid="stButton"] > button {
        width: 100% !important;
        border-radius: 18px !important;
        padding: 7px 10px !important;
        font-weight: 700 !important;
        margin-bottom: 5px !important;
        transition: all .15s ease-in-out;
    }

    /* 시·특별시·광역시 (하위 지역 없음) = 파랑 */
    button[kind="primary"] {
        border: 1.5px solid #8FC1E8 !important;
        background-color: #E6F1FB !important;
    }
    button[kind="primary"] p { color: #1B5FA8 !important; font-weight: 700 !important; }
    button[kind="primary"]:hover { background-color: #1B5FA8 !important; }
    button[kind="primary"]:hover p { color: #ffffff !important; }

    /* 도 (하위 시/군 있음) = 노랑 */
    button[kind="secondary"] {
        border: 1.5px solid #F9AB00 !important;
        background-color: #FEF7E0 !important;
    }
    button[kind="secondary"] p { color: #B06000 !important; font-weight: 700 !important; }
    button[kind="secondary"]:hover { background-color: #F9AB00 !important; }
    button[kind="secondary"]:hover p { color: #ffffff !important; }

    /* 대화 지우기만 무채색 */
    .st-key-reset button {
        border: 1px solid #e3e5ea !important;
        background: #f7f8fa !important;
    }
    .st-key-reset button p { color: #6b7280 !important; }
    .st-key-reset button:hover { background: #eceef2 !important; }
    .st-key-reset button:hover p { color: #374151 !important; }

    .ot-linkbtn {
        display: block; text-align: center; text-decoration: none !important;
        border-radius: 18px; padding: 10px 12px; margin-top: 8px; font-weight: 700;
    }
    .ot-linkbtn.blue   { background: #1B5FA8; color: #fff !important; }
    .ot-linkbtn.orange { background: #e8682a; color: #fff !important; }

    .ot-divider { height: 1px; background: #eef0f3; margin: 18px 0 12px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. 상수
# =========================================================
SIDO_LIST = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
             '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']

NO_SUB_REGIONS = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종']

SIDO_TO_SIGUNGU = {
    '전남': ['여수', '목포', '순천', '나주', '담양', '곡성', '구례', '고흥', '보성', '장흥', '진도', '함평', '영광', '장성', '완도', '해남', '강진', '무안', '신안', '영암'],
    '경남': ['남해', '하동', '산청', '거창', '사천', '김해', '통영', '진주', '함양', '밀양', '창원', '양산', '거제', '의령', '합천', '창녕', '함안'],
    '강원': ['영월', '정선', '태백', '삼척', '동해', '강릉', '속초', '양양', '홍천', '춘천', '원주', '인제', '철원', '화천', '양구', '평창', '횡성'],
    '경북': ['경주', '포항', '안동', '구미', '영주', '영천', '상주', '문경', '영덕', '성주', '청도', '고령', '의성', '청송', '영양', '봉화', '울진'],
    '충남': ['홍성', '보령', '서산', '당진', '아산', '천안', '공주', '논산', '금산', '부여', '서천', '청양', '예산', '태안'],
    '충북': ['청주', '충주', '제천', '보은', '옥천', '영동', '진천', '괴산', '음성', '단양'],
    '전북': ['전주', '군산', '익산', '정읍', '남원', '김제', '완주', '진안', '무주', '장수', '임실', '순창', '고창', '부안'],
    '경기': ['동두천', '수원', '성남', '의정부', '안양', '부천', '광명', '평택', '안산', '고양', '과천', '구리', '남양주', '오산', '시흥', '군포', '의왕', '하남', '용인', '파주', '이천', '안성', '김포', '화성', '양주', '포천', '여주', '연천', '가평', '양평'],
    '부산': ['부산시 전체'], '인천': ['인천시 전체'], '서울': ['서울시 전체'], '대구': ['대구시 전체'],
    '광주': ['광주시 전체'], '대전': ['대전시 전체'], '울산': ['울산시 전체'], '세종': ['세종시 전체'],
    '제주': ['제주시', '서귀포시'],
}

SIDO_TO_SIGUNGU = {k: sorted(v) for k, v in SIDO_TO_SIGUNGU.items()}

SIGUNGU_TO_SIDO = {}
for _sido, _list in SIDO_TO_SIGUNGU.items():
    for _sgg in _list:
        if "전체" not in _sgg:
            SIGUNGU_TO_SIDO[_sgg] = _sido

REGION_ALIASES = {
    '강원': ['강원', '강원도'], '전북': ['전북', '전라북도'], '전남': ['전남', '전라남도'],
    '경북': ['경북', '경상북도'], '경남': ['경남', '경상남도'], '충북': ['충북', '충청북도'],
    '충남': ['충남', '충청남도'], '제주': ['제주', '제주도'], '경기': ['경기', '경기도'],
    '서울': ['서울', '서울특별시'], '부산': ['부산', '부산광역시'], '대구': ['대구', '대구광역시'],
    '인천': ['인천', '인천광역시'], '광주': ['광주', '광주광역시'], '대전': ['대전', '대전광역시'],
    '울산': ['울산', '울산광역시'], '세종': ['세종', '세종시'],
}

# 모션 속도 (숫자가 클수록 느림)
LOADING_DELAY = 1.0    # "답변을 작성하고 있어요" 노출 시간(초)
TYPE_CHUNK = 1         # 한 번에 찍는 글자 수
TYPE_DELAY = 0.045     # 글자 사이 간격(초)
BETWEEN_MSG_DELAY = 0.4  # 말풍선과 말풍선 사이 간격(초)
PAD_SLOTS = 25         # 이전 화면 잔상 제거용 빈 슬롯

VISITKOREA_TRAVEL = "https://korean.visitkorea.or.kr/list/travelinfo.do?service=ms"
VISITKOREA_SHOW = "https://korean.visitkorea.or.kr/list/travelinfo.do?service=show"

# =========================================================
# 4. 데이터
# =========================================================
@st.cache_data
def load_subsidy():
    try:
        df = pd.read_csv(APP_DATA_DIR / "masil_chatbot.csv", encoding="utf-8-sig")
    except FileNotFoundError:
        return pd.DataFrame()

    def extract_sido(region, name):
        for sido in SIDO_LIST:
            if sido in str(region):
                return sido
        for sgg, sido in SIGUNGU_TO_SIDO.items():
            if sgg in str(region) or sgg in str(name):
                return sido
        for sido in SIDO_LIST:
            if sido in str(name):
                return sido
        return '기타'

    df['시도'] = df.apply(lambda r: extract_sido(r['지역'], r['지원금명']), axis=1)
    return df


@st.cache_data
def load_track2():
    try:
        return pd.read_csv(RAW_DIR / "track_2_dataset_2023_2024_2025.csv", encoding="utf-8-sig")
    except FileNotFoundError:
        return pd.DataFrame()


df = load_subsidy()
track2_df = load_track2()


def find_subsidy(keyword: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    keyword = keyword.strip()
    std = next((s for s, al in REGION_ALIASES.items() if keyword in al or keyword == s), None)
    if std:
        return df[df['시도'] == std].reset_index(drop=True)
    mask = df['지역'].fillna('').str.contains(keyword, na=False) | \
           df['지원금명'].fillna('').str.contains(keyword, na=False)
    return df[mask].reset_index(drop=True)


# =========================================================
# 5. 대화 상태
# =========================================================
def init_state():
    if "history" not in st.session_state:
        st.session_state.history = []
        push_bot("안녕하세요, Out-Traveler입니다 👋<br>어떤 도움이 필요하세요?")
    st.session_state.setdefault("step", "main")
    st.session_state.setdefault("sido", None)
    st.session_state.setdefault("region", None)
    st.session_state.setdefault("month", None)


def push_bot(html: str, kind: str = "text"):
    st.session_state.history.append({"role": "bot", "kind": kind, "html": html, "typed": False})


def push_user(text: str):
    st.session_state.history.append({"role": "user", "kind": "text", "html": text, "typed": True})


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# =========================================================
# 6. 렌더링 헬퍼
# =========================================================
def pad_slots(n: int = PAD_SLOTS):
    """이전 실행이 남긴 위젯 자리를 빈 슬롯으로 덮어쓴다."""
    for _ in range(n):
        st.empty()


def row_bot(inner_html: str, kind: str = "text") -> str:
    cls = "card" if kind == "card" else "bot"
    return (f"<div class='ot-row left'>"
            f"<img class='ot-avatar' src='{OT_LOGO_SRC}' alt='Out-Traveler'/>"
            f"<div class='ot-bubble {cls}'>{inner_html}</div></div>")


def row_user(text: str) -> str:
    return (f"<div class='ot-row right'>"
            f"<div class='ot-bubble user'>{esc(text)}</div></div>")


TOKEN_RE = re.compile(r"<[^>]+>|&[a-zA-Z#0-9]+;|.", re.S)


def type_into(slot, inner_html: str, kind: str = "text"):
    """HTML 태그는 통째로, 글자는 한 자씩 찍는다."""
    tokens = TOKEN_RE.findall(inner_html)
    shown, buf = "", 0
    for tk in tokens:
        shown += tk
        if len(tk) == 1 and tk.strip():
            buf += 1
        if buf >= TYPE_CHUNK:
            buf = 0
            slot.markdown(row_bot(shown + "<span class='ot-cursor'>▌</span>", kind),
                          unsafe_allow_html=True)
            time.sleep(TYPE_DELAY)
    slot.markdown(row_bot(shown, kind), unsafe_allow_html=True)


def card_html(row: pd.Series) -> str:
    title = esc(row.get('지원금명', '제목 없음'))
    loc = esc(row.get('지역', '-'))
    date = esc(row.get('신청기간', '기간 미상'))
    cat = str(row.get('카테고리', ''))
    det = str(row.get('지원내용', ''))
    url = str(row.get('상세URL', ''))

    html = f"<span class='t'>{title}</span><br>"
    html += f"<span class='meta'>📍 {loc} · 📅 {date}</span>"
    if cat and cat.lower() != 'nan':
        html += f"<span class='tag'>{esc(cat)}</span>"
    if det and det.lower() != 'nan':
        html += f"<br><br>🎁 {esc(det)}"
    if url and url.lower() != 'nan':
        html += f"<br><br><a href='{esc(url)}' target='_blank'>상세 보기 →</a>"
    return html


def button_grid(items, key_prefix, fixed_type=None, label_fn=None, cols_per_row=4):
    clicked = None
    for i in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j >= len(items):
                with cols[j]:
                    pad_slots(3)
                continue
            item = items[i + j]
            btype = fixed_type or ("primary" if item in NO_SUB_REGIONS else "secondary")
            label = label_fn(item) if label_fn else str(item)
            if cols[j].button(label, type=btype, key=f"{key_prefix}_{item}"):
                clicked = item
    return clicked


# =========================================================
# 7. 단계 전환 시 봇 응답 생성
# =========================================================
def goto(step: str):
    st.session_state.step = step

    if step == "main":
        push_bot("어떤 도움이 필요하세요?")

    elif step == "support_sido":
        push_bot("어떤 지역(도/시)의 지원금을 알고 싶으신가요?")

    elif step == "support_sigungu":
        push_bot(f"<b>{esc(st.session_state.sido)}</b> 안에서 구체적인 지역(시/군)을 선택해 주세요.")

    elif step == "support_result":
        region = st.session_state.region or st.session_state.sido
        matched = find_subsidy(region)
        if matched.empty:
            push_bot(f"<b>{esc(region)}</b> 지역은 아직 등록된 지원금 사례가 없어요.")
        else:
            push_bot(f"<b>{esc(region)}</b> 지역 지원금을 {len(matched)}건 찾았어요 🎉")
            for _, r in matched.iterrows():
                push_bot(card_html(r), kind="card")

    elif step == "travel_menu":
        push_bot("원하시는 여행 정보를 선택해 주세요.")

    elif step == "visitkorea":
        push_bot("한국관광공사 <b>대한민국 구석구석</b>에서 바로 확인하실 수 있어요.")
        push_bot("아래 버튼을 눌러보세요 👇", kind="links")

    elif step == "cong_sido":
        push_bot("혼잡도를 확인할 지역(도/시)을 선택해 주세요.")

    elif step == "cong_sigungu":
        push_bot(f"<b>{esc(st.session_state.sido)}</b> 안에서 구체적인 지역(시/군)을 선택해 주세요.")

    elif step == "cong_month":
        push_bot(f"<b>{esc(st.session_state.region)}</b>의 몇 월 혼잡도가 궁금하세요?")

    elif step == "cong_result":
        region, sido, month = st.session_state.region, st.session_state.sido, st.session_state.month
        if track2_df.empty:
            push_bot("track_2_dataset CSV 파일을 찾을 수 없어요.")
        else:
            m = track2_df[(track2_df['지역'] == sido) & (track2_df['월'] == month)]
            if m.empty:
                push_bot("해당 지역의 데이터가 없어요.")
            else:
                c = m.iloc[0]['혼잡도지수']
                push_bot(
                    f"2023~2025년 통합 데이터 기준, <b>{esc(region)}</b>의 {month}월 "
                    f"여행 혼잡도 지수는 <b>{c:.1f}</b>입니다."
                )
                push_bot(
                    "<span class='meta'>💡 해석 기준 (평소 100)<br>"
                    "· 100 = 그 지역의 평소 월평균 수준<br>"
                    "· 150 이상 = 평소보다 1.5배 이상 붐빔<br>"
                    "· 70 이하 = 평소보다 한산함</span>"
                )

    elif step == "exp_sido":
        push_bot("1인 평균 지출을 확인할 지역(도/시)을 선택해 주세요.")

    elif step == "exp_sigungu":
        push_bot(f"<b>{esc(st.session_state.sido)}</b> 안에서 구체적인 지역(시/군)을 선택해 주세요.")

    elif step == "exp_result":
        region, sido = st.session_state.region, st.session_state.sido
        if track2_df.empty:
            push_bot("track_2_dataset CSV 파일을 찾을 수 없어요.")
        else:
            m = track2_df[track2_df['지역'] == sido]
            if m.empty:
                push_bot(f"<b>{esc(sido)}</b> 지역의 데이터가 없어요.")
            else:
                w = m['표본수(n)']
                avg = (m['1인평균지출_가중평균'] * w).sum() / w.sum()
                lo, hi = m['1인평균지출_중앙값'].min(), m['1인평균지출_중앙값'].max()
                n = int(w.sum())
                msg = (f"<b>{esc(region)}</b>의 1인 평균 지출은 <b>{int(avg):,}원</b>이에요.<br>"
                       f"<span class='meta'>월별 중앙값은 {int(lo):,}원 ~ {int(hi):,}원 범위입니다. "
                       f"2023~2025년 데이터를 월별 표본수로 가중해 계산했습니다.</span>")
                if n < 100:
                    msg += f"<br><span class='meta'>⚠️ 표본이 적어({n}건) 참고용으로만 봐주세요.</span>"
                push_bot(msg)


# =========================================================
# 8. 화면 그리기
# =========================================================
init_state()

st.markdown(
    f"<div style='display:flex;align-items:center;gap:9px;margin-bottom:2px;'>"
    f"<img src='{OT_LOGO_SRC}' style='width:30px;height:30px;border-radius:50%;'/>"
    f"<span style='font-size:1.28rem;font-weight:800;color:#0C3D6E;'>Out-Traveler AI chatbot</span>"
    f"</div>",
    unsafe_allow_html=True,
)
st.markdown("<div class='ot-divider'></div>", unsafe_allow_html=True)

pending = []          # 이번 실행에서 타이핑할 (slot, html, kind)
history = st.session_state.history

for msg in history:
    if msg["role"] == "user":
        st.markdown(row_user(msg["html"]), unsafe_allow_html=True)
        continue

    if msg["kind"] == "links":
        st.markdown(row_bot(msg["html"]), unsafe_allow_html=True)
        st.markdown(
            f"<a class='ot-linkbtn blue' href='{VISITKOREA_TRAVEL}' target='_blank'>"
            f"📌 대한민국 구석구석 · 전국 여행지 보기 ↗</a>"
            f"<a class='ot-linkbtn orange' href='{VISITKOREA_SHOW}' target='_blank'>"
            f"🎉 대한민국 구석구석 · 축제 / 공연 / 행사 보기 ↗</a>",
            unsafe_allow_html=True,
        )
        msg["typed"] = True
        continue

    if msg["typed"]:
        st.markdown(row_bot(msg["html"], msg["kind"]), unsafe_allow_html=True)
    else:
        slot = st.empty()
        slot.markdown(row_bot("<span class='ot-loading'>✨ 답변을 작성하고 있어요…</span>"),
                      unsafe_allow_html=True)
        pending.append((slot, msg))

# ---------- 현재 단계의 선택 버튼 ----------
st.markdown("<div class='ot-divider'></div>", unsafe_allow_html=True)
step = st.session_state.step
picked = None

if step == "main":
    if st.button("💰 지원금 관련", type="primary", key="m1"):
        push_user("지원금 관련"); goto("support_sido"); st.rerun()
    if st.button("✈️ 여행지 관련", type="primary", key="m2"):
        push_user("여행지 관련"); goto("travel_menu"); st.rerun()

elif step == "support_sido":
    avail = [s for s in SIDO_LIST if s in df['시도'].values] if not df.empty else SIDO_LIST
    picked = button_grid(avail, "sup_sido")
    if st.button("🏠 처음으로", type="primary", key="sup_sido_home"):
        push_user("처음으로"); goto("main"); st.rerun()
    if picked:
        push_user(picked)
        st.session_state.sido, st.session_state.region = picked, None
        goto("support_result" if picked in NO_SUB_REGIONS else "support_sigungu")
        st.rerun()

elif step == "support_sigungu":
    picked = button_grid(SIDO_TO_SIGUNGU.get(st.session_state.sido, []), "sup_sgg", "secondary")
    if st.button("⬅️ 이전으로", type="primary", key="sup_sgg_back"):
        push_user("이전으로"); goto("support_sido"); st.rerun()
    if picked:
        push_user(picked)
        st.session_state.region = picked
        goto("support_result"); st.rerun()

elif step == "support_result":
    if st.button("🔎 다른 지역 지원금 보기", type="primary", key="sup_more"):
        push_user("다른 지역 지원금 보기"); goto("support_sido"); st.rerun()
    if st.button("🏠 처음으로", type="primary", key="sup_res_home"):
        push_user("처음으로"); goto("main"); st.rerun()

elif step == "travel_menu":
    if st.button("📊 특정 지역 혼잡도 알고 싶어요", type="primary", key="t1"):
        push_user("특정 지역 혼잡도"); goto("cong_sido"); st.rerun()
    if st.button("💳 특정 지역 1인 평균 지출 알고 싶어요", type="primary", key="t2"):
        push_user("1인 평균 지출"); goto("exp_sido"); st.rerun()
    if st.button("🗺️ 특정 지역의 여행 정보를 알고 싶어요", type="primary", key="t3"):
        push_user("여행 정보"); goto("visitkorea"); st.rerun()
    if st.button("🏠 처음으로", type="primary", key="tm_home"):
        push_user("처음으로"); goto("main"); st.rerun()

elif step == "visitkorea":
    if st.button("🏠 처음으로", type="primary", key="vk_home"):
        push_user("처음으로"); goto("main"); st.rerun()

elif step == "cong_sido":
    picked = button_grid(SIDO_LIST, "cong_sido")
    if st.button("🏠 처음으로", type="primary", key="cong_sido_home"):
        push_user("처음으로"); goto("main"); st.rerun()
    if picked:
        push_user(picked)
        st.session_state.sido = picked
        st.session_state.region = f"{picked}시 전체" if picked in NO_SUB_REGIONS else None
        goto("cong_month" if picked in NO_SUB_REGIONS else "cong_sigungu")
        st.rerun()

elif step == "cong_sigungu":
    picked = button_grid(SIDO_TO_SIGUNGU.get(st.session_state.sido, []), "cong_sgg", "secondary")
    if st.button("⬅️ 이전으로", type="primary", key="cong_sgg_back"):
        push_user("이전으로"); goto("cong_sido"); st.rerun()
    if picked:
        push_user(picked)
        st.session_state.region = picked
        goto("cong_month"); st.rerun()

elif step == "cong_month":
    picked = button_grid(list(range(1, 13)), "cong_m", "primary", lambda m: f"{m}월")
    if st.button("⬅️ 이전으로", type="primary", key="cong_m_back"):
        push_user("이전으로")
        goto("cong_sido" if st.session_state.sido in NO_SUB_REGIONS else "cong_sigungu")
        st.rerun()
    if picked:
        push_user(f"{picked}월")
        st.session_state.month = picked
        goto("cong_result"); st.rerun()

elif step == "cong_result":
    if st.button("🔎 다른 지역 혼잡도 보기", type="primary", key="cong_more"):
        push_user("다른 지역 혼잡도 보기"); goto("cong_sido"); st.rerun()
    if st.button("🏠 처음으로", type="primary", key="cong_res_home"):
        push_user("처음으로"); goto("main"); st.rerun()

elif step == "exp_sido":
    picked = button_grid(SIDO_LIST, "exp_sido")
    if st.button("🏠 처음으로", type="primary", key="exp_sido_home"):
        push_user("처음으로"); goto("main"); st.rerun()
    if picked:
        push_user(picked)
        st.session_state.sido = picked
        st.session_state.region = f"{picked}시 전체" if picked in NO_SUB_REGIONS else None
        goto("exp_result" if picked in NO_SUB_REGIONS else "exp_sigungu")
        st.rerun()

elif step == "exp_sigungu":
    picked = button_grid(SIDO_TO_SIGUNGU.get(st.session_state.sido, []), "exp_sgg", "secondary")
    if st.button("⬅️ 이전으로", type="primary", key="exp_sgg_back"):
        push_user("이전으로"); goto("exp_sido"); st.rerun()
    if picked:
        push_user(picked)
        st.session_state.region = picked
        goto("exp_result"); st.rerun()

elif step == "exp_result":
    if st.button("🔎 다른 지역 지출 보기", type="primary", key="exp_more"):
        push_user("다른 지역 지출 보기"); goto("exp_sido"); st.rerun()
    if st.button("🏠 처음으로", type="primary", key="exp_res_home"):
        push_user("처음으로"); goto("main"); st.rerun()

# 대화 초기화
if len(history) > 1:
    if st.button("🗑 대화 지우기", key="reset"):
        for k in ("history", "step", "sido", "region", "month"):
            st.session_state.pop(k, None)
        st.rerun()

# 잔상 제거용 빈 슬롯 (반드시 타이핑 전에)
pad_slots()

# ---------- 타이핑 실행 ----------
if pending:
    time.sleep(LOADING_DELAY)
    for slot, msg in pending:
        type_into(slot, msg["html"], msg["kind"])
        msg["typed"] = True
        time.sleep(BETWEEN_MSG_DELAY)

# ---------- 항상 마지막 대화가 보이도록 스크롤 ----------
components.html(
    """
    <script>
      const doc = window.parent.document;
      const target = doc.querySelector('[data-testid="stMain"]') || doc.scrollingElement;
      if (target) { target.scrollTo({ top: target.scrollHeight, behavior: 'smooth' }); }
    </script>
    """,
    height=0,
)
