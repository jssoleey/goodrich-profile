import streamlit as st
import streamlit.components.v1 as components
from streamlit_cropper import st_cropper
import os
import json
import uuid
from PIL import Image
import base64
from io import BytesIO
import time
from card_uploader import upload_to_github

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
    [data-testid="stColorPicker"] input[type="color"] {
        width: 100px !important;
        height: 100px !important;
        border: none;
        padding: 0;
        border-radius: 50px;
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
                index_path = os.path.join("/data", "index.json")
                os.makedirs("/data", exist_ok=True)

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
                user_folder = os.path.join("/data", session_id)
                os.makedirs(user_folder, exist_ok=True)

                st.session_state.update({
                    'user_folder': user_folder,
                    'user_name': name,
                    'user_id': emp_id,
                    'session_id': session_id,
                    'page': 'input'
                })
                st.rerun()
            else:
                st.warning("이름과 비밀번호를 모두 입력해 주세요.")

#------------------------- 기본정보 입력 -------------------------
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
            
    for key in default_data:
        if key not in st.session_state and key != "histories":  # 이력은 별도 관리
            st.session_state[key] = default_data[key]

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
            st.text_area(label, key=key, height=120, placeholder="자유롭게 작성해 주세요.")
        else:
            st.text_input(label, key=key, placeholder=placeholder)

    # 세션 상태 초기화
    if "histories" not in st.session_state:
        st.session_state.histories = default_data.get("histories", []).copy()
        
    st.markdown("")
    st.markdown("---")

#------------------------- 개인 이력 -------------------------
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
            st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
            if st.button("🗑 삭제", key=f"delete_{i}", use_container_width=True):
                to_delete = i
                
        # 삭제 예정이 아닌 항목만 업데이트
        if to_delete is None:
            st.session_state.histories[i] = {"year": year, "desc": desc}

    # 삭제 처리
    if to_delete is not None:
        del st.session_state.histories[to_delete]
        st.rerun()

    # ➕ 이력 추가
    col1, col2, col3 = st.columns([1.5, 4, 1])
    
    with col1 :
        if st.button("➕ 이력 추가", use_container_width=True):
            st.session_state.histories.append({"year": "", "desc": ""})
            st.rerun()

    # --- 저장 시 이력 포함 ---
    profile_data["histories"] = st.session_state.histories
    
    st.markdown("")
    st.markdown("---")

#------------------------- 프로필 사진 ------------------------- 
    def cropped_img_to_base64(img):
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
   
    # ✅ 세션 상태 초기화
    if "uploaded_now" not in st.session_state:
        st.session_state["uploaded_now"] = False
    if "just_saved" not in st.session_state:
        st.session_state["just_saved"] = False

    # 경로 설정
    profile_img_path = os.path.join(user_folder, "profile.jpg")

    # ✅ 파일 업로드
    st.markdown("")
    st.markdown("##### 📍 프로필 사진 업로드", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        # ✅ 업로더에 dynamic key 사용 (이미 적용되었을 것)
        uploader_key = "uploader"
        if st.session_state.get("force_clear_uploader"):
            uploader_key = str(uuid.uuid4())
            st.session_state["force_clear_uploader"] = False

        uploaded_img = st.file_uploader("이미지를 업로드하세요", type=["png", "jpg", "jpeg"], key=uploader_key)

    with col2:
        # ✅ 저장된 프로필 이미지가 있다면 표시
        if os.path.exists(profile_img_path):
            st.markdown(
                f"""
                <div style='
                    display: flex;
                    justify-content: center;
                    margin-top: 8px;
                    margin-right: 10px;
                '>
                    <img src="data:image/png;base64,{cropped_img_to_base64(Image.open(profile_img_path))}"
                        style="width: 100px; height: 100px; object-fit: cover; border-radius: 35%; border: 1px solid #ccc;" />
                </div>
                """,
                unsafe_allow_html=True
            )
    
    if uploaded_img:
        st.session_state["uploaded_now"] = True

    # ✅ 1. 이미지 업로드 → cropper 및 실시간 미리보기
    if uploaded_img and not st.session_state["just_saved"]:
        img = Image.open(uploaded_img)
        img_copy = img.copy()
        img_copy.thumbnail((300, 300))

        # ✅ 두 개의 열로 나누기
        col1, col2 = st.columns([3, 2])

        with col1:
            st.markdown("**🔍 자를 영역을 선택하세요 (1:1 비율)**")
            cropped_img = st_cropper(
                img_copy,
                aspect_ratio=(1, 1),
                box_color='#f79901',
                return_type='image',
                realtime_update=True
            )

        with col2:
            st.markdown(
                f"""
                <div style='display: flex; justify-content: center; margin-top: 60px; margin-bottom: 30px'>
                    <img src="data:image/png;base64,{cropped_img_to_base64(cropped_img)}"
                        style="width: 200px; height: 200px; object-fit: cover; border-radius: 50%; border: 2px solid #ccc;" />
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("💾 이미지 저장", use_container_width=True):
                if cropped_img.mode in ("RGBA", "P"):
                    cropped_img = cropped_img.convert("RGB")
                cropped_img.save(profile_img_path)
                st.session_state["uploaded_now"] = False
                st.session_state["just_saved"] = True
                st.session_state["force_clear_uploader"] = True
                st.rerun()

    # ✅ 2. 저장 직후: 메시지 + 저장된 이미지 즉시 보여주기
    elif st.session_state["just_saved"]:
        st.success("✅ 프로필 이미지가 저장되었습니다.")
        st.session_state["just_saved"] = False  # 다음 렌더링부터는 다시 일반 흐름
        
    st.markdown("")
    st.markdown("---")
    
# ------------------------- 갤러리 -------------------------
    st.markdown("")
    st.markdown("##### 📍 갤러리 이미지 업로드", unsafe_allow_html=True)

    photos_dir = os.path.join(user_folder, "photos")
    os.makedirs(photos_dir, exist_ok=True)

    # ✅ 저장 후 재렌더링 제어
    if "gallery_saved" not in st.session_state:
        st.session_state.gallery_saved = False
        
    uploaded_photo = st.file_uploader(
        "",
        type=["jpg", "jpeg", "png"],
        key=f"single_photo_{st.session_state.get('upload_key', 0)}"
    )
    
    if uploaded_photo and st.session_state.get("gallery_saved"):
        st.session_state.gallery_saved = False

    # ✅ 자르기 UI는 저장 후에만 숨김
    if uploaded_photo and not st.session_state.gallery_saved:
        img = Image.open(uploaded_photo)
        img_copy = img.copy()

        cropped_img = st_cropper(
            img_copy,
            aspect_ratio=(3, 4),
            box_color='#f79901',
            return_type='image',
            realtime_update=True
        )
        col1, col2, col3 = st.columns(3)
        with col2 :
            if st.button("💾 자른 이미지 저장", use_container_width = True):
                filename = f"{int(time.time())}.jpg"
                filepath = os.path.join(photos_dir, filename)
                
                if cropped_img.mode in ("RGBA", "P"):
                    cropped_img = cropped_img.convert("RGB")
                
                cropped_img.save(filepath)
                st.session_state.gallery_saved = True
                st.session_state.upload_key = st.session_state.get("upload_key", 0) + 1
                st.rerun()

    # ✅ 저장된 이미지 미리보기 + 삭제
    st.markdown("")
    photo_files = sorted([
        f for f in os.listdir(photos_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ])

    if photo_files:

        cols = st.columns(5)
        to_delete = None

        for i, file in enumerate(photo_files):
            path = os.path.join(photos_dir, file)
            with cols[i % 5]:
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-bottom: 15px;">
                        <img src="data:image/jpeg;base64,{base64.b64encode(open(path, "rb").read()).decode()}" width="100"/><br>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("🗑 삭제", use_container_width = True, key=f"del_{file}"):
                    to_delete = file

        if to_delete:
            os.remove(os.path.join(photos_dir, to_delete))
            st.rerun()

    st.markdown("")
    st.markdown("---")
    
#------------------------- 명함 배경 -------------------------        
    # 명함 배경 업로드
    st.markdown("")
    st.markdown("##### 📍 명함 배경 이미지 선택", unsafe_allow_html=True)
    
    # 현재 배경 이미지 목록 로딩
    bg_dir = "backgrounds"
    bg_files = sorted([f for f in os.listdir(bg_dir) if f.endswith((".png", ".jpg", ".jpeg"))])

    # ✅ profile.json에서 저장된 배경 이미지 불러와 인덱스 초기화
    profile_path = os.path.join(user_folder, "profile.json")
    default_bg_index = 0
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
            saved_bg = profile_data.get("background_image")
            if saved_bg in bg_files:
                default_bg_index = bg_files.index(saved_bg)
    if "bg_index" not in st.session_state:
        st.session_state.bg_index = default_bg_index
    if "nav_action" not in st.session_state:
        st.session_state.nav_action = None

    # 현재 선택된 배경 이미지 경로
    selected_bg = bg_files[st.session_state.bg_index]
    bg_path = os.path.join(bg_dir, selected_bg)

    # base64 인코딩 함수
    @st.cache_data
    def get_base64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    # base64 인코딩
    bg_base64 = get_base64(bg_path)
    card_base64 = get_base64("sample_card.png")  # <- 방금 업로드하신 오버레이 이미지로 경로 확인

    # 열 배치
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(
            f"""
            <div style="position: relative; width: 100%; padding-top: 71.43%; border-radius: 12px; overflow: hidden; margin-top: 12px; margin-bottom: 20px;">
                <!-- 비율 7:5 → padding-top: (5/7)*100% ≈ 71.43% -->
                <img src="data:image/png;base64,{bg_base64}"
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;" />
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            f"""
            <div style="position: relative; width: 100%; padding-top: 71.43%; border-radius: 12px; overflow: hidden; margin-top: 12px; margin-bottom: 20px;">
                <!-- 비율 7:5 → padding-top: (5/7)*100% ≈ 71.43% -->
                <img src="data:image/png;base64,{bg_base64}"
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;" />
                <img src="data:image/png;base64,{card_base64}"
                    style="position: absolute; top: 50%; left: 50%; width: 91%; aspect-ratio: 2 / 1;
                            transform: translate(-50%, -50%); object-fit: contain;" />
            </div>
            """,
            unsafe_allow_html=True
        )

    # 버튼 영역
    def go_prev():
        st.session_state.bg_index = (st.session_state.bg_index - 1) % len(bg_files)

    def go_next():
        st.session_state.bg_index = (st.session_state.bg_index + 1) % len(bg_files)

    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])

    with col2:
        st.button("◀ 이전", use_container_width=True, on_click=go_prev)

    with col3:
        st.markdown(
            f"<div style='text-align: center; padding-top: 10px; font-weight: 500;'>"
            f"{st.session_state.bg_index + 1} / {len(bg_files)}</div>",
            unsafe_allow_html=True
        )

    with col4:
        st.button("다음 ▶", use_container_width=True, on_click=go_next)

    # 선택 결과 저장
    profile_data["background_image"] = selected_bg

    # 저장용
    profile_data["background_image"] = selected_bg
    
    st.markdown("")
    st.markdown("---")
        
#------------------------- 테마 색상 선택 -------------------------                   
    st.markdown("")
    st.markdown("##### 📍 테마 및 배경 색상 선택", unsafe_allow_html=True)
    st.markdown("")

    col1, col2, col3 = st.columns([1, 1, 2])

    # 🎨 기존 수동 선택 유지
    with col1:
        st.markdown("###### 배경 색상 선택", unsafe_allow_html=True)
        background_color = st.color_picker("", value=st.session_state.get("background_color", "#fffcf7"))
        st.session_state["background_color"] = background_color

    with col2:
        st.markdown("###### 테마 색상 선택", unsafe_allow_html=True)
        theme_color = st.color_picker("", value=st.session_state.get("theme_color", "#f79901"))
        st.session_state["theme_color"] = theme_color

    # 🎯 추천 색상 조합 표시
    st.markdown("###### 🎨 추천 색상 조합", unsafe_allow_html=True)

    # 🎨 추천 색상 세트 정의
    COLOR_PAIRS = [
        {"bg": "#fff7e6", "theme": "#f79901"},
        {"bg": "#e8f9fd", "theme": "#4dabf7"},
        {"bg": "#fef6fb", "theme": "#e64980"},
        {"bg": "#f3fce8", "theme": "#2b8a3e"},
        {"bg": "#f0f0ff", "theme": "#5f3dc4"},
    ]

    # ✅ CSS 스타일: 팔레트용 div + 숨겨진 버튼
    st.markdown("""
        <style>
        .palette-box {
            width: 100%;
            height: 36px;
            border-radius: 8px;
            border: 1px solid #ccc;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .palette-box:hover {
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            border-color: #888;
        }
        .palette-button {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # ✅ 팔레트 구성: 버튼은 숨기고, div를 누르면 버튼 클릭 발생
    set_cols = st.columns(len(COLOR_PAIRS))
    for i, pair in enumerate(COLOR_PAIRS):
        with set_cols[i]:
            button_key = f"color_select_{i}"
            clicked = st.button("선택", key=button_key, use_container_width = True)

            st.markdown(f"""
                <div class="palette-box" onclick="document.querySelector('[data-testid={button_key}]').click()" 
                    style="background: linear-gradient(to right, {pair['bg']} 50%, {pair['theme']} 50%);">
                </div>
            """, unsafe_allow_html=True)

            if clicked:
                st.session_state["background_color"] = pair["bg"]
                st.session_state["theme_color"] = pair["theme"]
                st.rerun()

    # ✅ 색상 미리보기
    with col3:
        st.markdown("###### 색상 미리 보기", unsafe_allow_html=True)
        st.components.v1.html(f"""
            <div style="width: 90%; background-color: {st.session_state['background_color']}; padding: 20px; border-radius: 12px;">
                <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link href="https://fonts.googleapis.com/css2?family=Galada&display=swap" rel="stylesheet">
                <div style="
                    padding: 15px 0 15px 0;
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                    font-family: sans-serif;
                    overflow: auto;
                    text-align: center;
                ">
                    <div style="
                        font-family: 'Galada', cursive;
                        font-size: 20px;
                        color: {st.session_state['theme_color']};
                        margin-top: 10px;
                        margin-bottom: 25px;
                    ">
                        TEXT
                    </div>
                </div>
            </div>
        """, height=150)

    st.markdown("")
    st.markdown("---")   
#------------------------- 저장/전자명함 생성 -------------------------   
    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 저장하기", use_container_width=True):
            for key in fields:
                profile_data[key] = st.session_state.get(key, "")
            profile_data["histories"] = st.session_state.histories
            profile_data["background_image"] = selected_bg
            profile_data["theme_color"] = theme_color
            profile_data["background_color"] = background_color

            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
            st.success("✅ 프로필 정보가 저장되었습니다!")

    with col2:
        if st.button("▶️ 모바일 명함 생성하기", use_container_width=True):
            base_url = "https://goodrich-profile.onrender.com/view"
            session_id = st.session_state['session_id']
            timestamp = int(time.time())  # 초 단위 현재 시간
            view_url = f"{base_url}?session_id={session_id}&nocache={timestamp}"
            view_link = f"https://goodrich-profile.onrender.com/view?session_id={session_id}"
            
            try:
                preview_link = upload_to_github(session_id, view_url)
                st.session_state["preview_link"] = preview_link
                st.session_state["view_url"] = view_url
                st.session_state["link_ready"] = True
            except Exception as e:
                st.error("❌ 미리보기 링크 생성 실패")
                st.text(str(e))
                st.session_state["link_ready"] = False
        
        # 👉 생성 완료 후 UI 출력
        if st.session_state.get("link_ready", False):

            st.markdown("###### 공유용 링크(복사 후 붙여넣기)", unsafe_allow_html=True)
            # 공유용 링크 입력창
            st.text_input("🔗 공유용 링크", value=st.session_state["preview_link"], key="copy_link", label_visibility="collapsed")
        
            # 새 창에서 명함 보기
            st.markdown(
                f'<a href="{st.session_state["view_url"]}" target="_blank">🔗 👉 새 창에서 명함 보기</a>',
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
