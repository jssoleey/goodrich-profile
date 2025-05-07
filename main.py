import streamlit as st
import streamlit.components.v1 as components
import os
import json
import uuid

# ----------------- 설정 -------------------
URLS = {
    "page_icon": "https://github.com/jssoleey/goodrich-profile/blob/main/image/logo.png?raw=true",
    "top_image": "https://github.com/jssoleey/goodrich-profile/blob/main/image/top_box.png?raw=true",
    "bottom_image": "https://github.com/jssoleey/goodrich-profile/blob/main/image/bottom_box.png?raw=true",
    "logo": "https://github.com/jssoleey/goodrich-profile/blob/main/image/logo.png?raw=true",
}

st.set_page_config(
    page_title="온라인 전자 명함 생성 - goodrich",
    page_icon=URLS["page_icon"],
    layout="centered"
)

# ----------------- CSS -------------------
st.markdown("""
    <style>
    .centered {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .login-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 400px;
        text-align: center;
    }
    .stTextInput > div > input {
        text-align: center;
    }
    /* 사이드바 숨기기 */
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    /* input box 색상 */
    input[type="text"] {
        background-color: #e4e9f0 !important;
        color: #333333;
        border-radius: 8px;
    }
    input[placeholder="예: 1234"] {
        background-color: #e4e9f0 !important;
        color: black !important;
    }
    /* 첫 번째 textarea만 스타일 적용 */
    textarea:nth-of-type(1) {
        background-color: #e4e9f0 !important;
        color: #333333;
        border-radius: 8px;
    }
    text_input:nth-of-type(4) {
        background-color: #e4e9f0 !important;
        color: #333333;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- 세션 상태 초기화 -------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

# ----------------- 로그인 화면 -------------------
# 이미지 URL
top_image_url = URLS["top_image"]

# 최상단에 이미지 출력
st.markdown(
    f"""
    <div style="text-align:center; margin-bottom:20px;">
        <img src="{top_image_url}" alt="Top Banner" style="width:100%; max-width:1000px;">
    </div>
    """,
    unsafe_allow_html=True
)

if st.session_state.page == "login":
    logo_url = URLS["logo"]
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: -10px;">
            <img src="{logo_url}" alt="logo" width="50">
            <h2 style="margin: 0;">굿리치 온라인 명함 생성</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")
    name = st.text_input("ID (이름)", placeholder="예: 홍길동")
    emp_id = st.text_input("Password", placeholder="예: 1234", type="password")
    st.markdown("")

    col1, col2, col3 = st.columns(3)
    with col2 :
        if st.button("로그인", use_container_width=True):
            if name and emp_id:
                id_key = f"{name}_{emp_id}"
                index_path = os.path.join("data", "index.json")
                os.makedirs("data", exist_ok=True)

                if os.path.exists(index_path):
                    with open(index_path, encoding="utf-8") as f:
                        index = json.load(f)
                else:
                    index = {}

                if id_key not in index:
                    folder_id = str(uuid.uuid4())
                    index[id_key] = folder_id
                    with open(index_path, "w", encoding="utf-8") as f:
                        json.dump(index, f, ensure_ascii=False, indent=2)

                session_id = index[id_key]
                user_folder = os.path.join("data", session_id)
                os.makedirs(user_folder, exist_ok=True)

                st.session_state.update({
                    'user_folder': user_folder,
                    'user_name': name,
                    'user_id': emp_id,
                    'session_id': session_id,
                    'page': 'input'
                })
                st.experimental_rerun()
            else:
                st.warning("이름과 비밀번호를 모두 입력해 주세요.")

# ----------------- 입력 화면 -------------------
elif st.session_state.page == "input":
    st.markdown(f"<h4>📇 {st.session_state['user_name']}님의 전자명함 등록</h4>", unsafe_allow_html=True)

    user_folder = st.session_state['user_folder']
    os.makedirs(user_folder, exist_ok=True)

    # --- 프로필 정보 불러오기 ---
    profile_path = os.path.join(user_folder, "profile.json")
    default_data = {
        "name": st.session_state["user_name"],
        "department": "", "position": "", "mobile": "", "phone": "",
        "fax": "", "email": "", "introduction": "", "background_image": "",
        "histories": []  # 이력도 기본 포함
    }
    if os.path.exists(profile_path):
        with open(profile_path, encoding="utf-8") as f:
            saved = json.load(f)
            default_data.update(saved)

    # --- 이력 세션 상태 초기화 ---
    if "histories" not in st.session_state:
        st.session_state.histories = default_data.get("histories", []).copy()

    # --- 명함 정보 입력 ---
    st.markdown("")
    st.markdown("")
    st.markdown("##### 📍 기본 정보 입력")
    fields = {
        "name": "이름", "department": "부서", "position": "직급",
        "mobile": "핸드폰번호", "phone": "전화번호", "fax": "팩스번호",
        "email": "이메일", "introduction": "자기 소개"
    }

    profile_data = {}
    for key, label in fields.items():
        placeholder = f"예: {'홍길동' if key == 'name' else '플러스사업부' if key == 'department' else '팀장' if key == 'position' else '01012345678(숫자만 입력하세요)' if key == 'mobile' else '01012345678(숫자만 입력하세요)' if key == 'phone' else '0212345678(숫자만 입력하세요)' if key == 'fax' else 'example@company.com' if key == 'email' else ''}"
        if key == "introduction":
            profile_data[key] = st.text_area(label, value=default_data.get(key, ""), height=120, placeholder="자유롭게 작성해 주세요.")
        else:
            profile_data[key] = st.text_input(label, value=default_data.get(key, ""), placeholder=placeholder)

    # 세션 상태 초기화
    if "histories" not in st.session_state:
        st.session_state.histories = default_data.get("histories", []).copy()

    st.markdown("")
    st.markdown("---")
    st.markdown("")
    st.markdown("##### 📍 개인 이력 입력")

    # 현재 이력 항목 렌더링
    to_delete = None  # 삭제할 인덱스 추적용
    for i, item in enumerate(st.session_state.histories):
        col1, col2, col3 = st.columns([1.5, 4, 1])
        with col1:
            year = st.text_input(f"연도/월", placeholder="예: 2020. 01", value=item["year"], key=f"year_{i}")
        with col2:
            desc = st.text_input(f"이력 설명", placeholder="예: 굿리치플러스 입사", value=item["desc"], key=f"desc_{i}")
        with col3:
            if st.button("🗑 삭제", key=f"delete_{i}", use_container_width=True):
                to_delete = i
                
        # 삭제 예정이 아닌 항목만 업데이트
        if to_delete is None:
            st.session_state.histories[i] = {"year": year, "desc": desc}

    # 삭제 처리
    if to_delete is not None:
        del st.session_state.histories[to_delete]
        st.experimental_rerun()

    # ➕ 이력 추가
    col1, col2, col3 = st.columns([1.5, 4, 1])
    
    with col1 :
        if st.button("➕ 이력 추가", use_container_width=True):
            st.session_state.histories.append({"year": "", "desc": ""})
            st.experimental_rerun() 

    # --- 저장 시 이력 포함 ---
    profile_data["histories"] = st.session_state.histories
    
    # 📸 프로필 사진 업로드
    st.markdown("")
    st.markdown("---")
    st.markdown("")
    st.markdown("##### 📍 프로필 사진 업로드 (정사각형 권장)", unsafe_allow_html=True)
    uploaded_img = st.file_uploader("프로필 사진 선택", type=["png", "jpg", "jpeg"])

    if uploaded_img is not None:
        img_save_path = os.path.join(user_folder, "profile.jpg")
        with open(img_save_path, "wb") as f:
            f.write(uploaded_img.read())
        st.success("✅ 프로필 사진이 업로드되었습니다.")

    # 명함 배경 업로드
    st.markdown("")
    st.markdown("---")
    st.markdown("")
    st.markdown("##### 📍 명함 배경 이미지 선택", unsafe_allow_html=True)
    
    # 이미지 파일 불러오기
    bg_dir = "backgrounds"
    os.makedirs(bg_dir, exist_ok=True)
    bg_files = sorted([f for f in os.listdir(bg_dir) if f.endswith((".png", ".jpg", ".jpeg"))])

    # 상태 초기화
    if bg_files:
        if "bg_index" not in st.session_state:
            st.session_state.bg_index = 0
        if "nav_action" not in st.session_state:
            st.session_state.nav_action = None

        # 이미지 미리보기
        selected_bg = bg_files[st.session_state.bg_index]
        st.image(os.path.join(bg_dir, selected_bg), width = 440)

        # 버튼을 누르면 상태에만 기록
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("◀ 이전"):
                st.session_state.nav_action = "prev"
        with col2:
            if st.button("다음 ▶"):
                st.session_state.nav_action = "next"

        # 버튼 클릭에 따른 인덱스 변경은 한 번만 처리
        if st.session_state.nav_action == "prev":
            st.session_state.bg_index = (st.session_state.bg_index - 1) % len(bg_files)
            st.session_state.nav_action = None
            st.experimental_rerun()  # 즉시 반영

        elif st.session_state.nav_action == "next":
            st.session_state.bg_index = (st.session_state.bg_index + 1) % len(bg_files)
            st.session_state.nav_action = None
            st.experimental_rerun()

        st.markdown(f"**선택된 배경:** `{selected_bg}`")
    else:
        st.warning("⚠️ 사용할 수 있는 배경 이미지가 없습니다.")

    # 저장용
    profile_data["background_image"] = selected_bg
    
    st.markdown("")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 저장하기", use_container_width=True):
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
            st.success("✅ 프로필 정보가 저장되었습니다!")

    with col2:
        if st.button("▶️ 모바일 명함 생성하기", use_container_width=True):
            base_url = "http://localhost:8501/view"
            session_id = st.session_state['session_id']
            view_url = f"{base_url}?session_id={session_id}"

            # 새 창에서 열 수 있는 안전한 링크 제공
            st.markdown(
                f'<a href="{view_url}" target="_blank">🔗 👉 새 창에서 명함 보기</a>',
                unsafe_allow_html=True
            )

bottom_image_url = URLS["bottom_image"]
st.markdown("")            
st.markdown(
    f"""
    <div style="text-align:center; margin-bottom:20px;">
        <img src="{bottom_image_url}" alt="Bottom Banner" style="width:100%; max-width:1000px;">
    </div>
    """,
    unsafe_allow_html=True
)
