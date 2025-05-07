import streamlit as st
import view
import streamlit.components.v1 as components
import os
import json
import uuid

# ----------------- 설정 -------------------
URLS = {
    "page_icon": "https://github.com/jssoleey/goodrich-chatbot-prevent/blob/main/image/logo.png?raw=true"
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
    </style>
""", unsafe_allow_html=True)

# ----------------- 세션 상태 초기화 -------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

query_params = st.experimental_get_query_params()
if query_params.get("page") == "view":
    import view  # 또는 render_view(session_id)
else :
    # ----------------- 로그인 화면 -------------------
    if st.session_state.page == "login":
        st.title("🔐 온라인 전자명함 생성")
    
        name = st.text_input("ID (이름)", placeholder="예: 홍길동")
        emp_id = st.text_input("Password (휴대폰 끝자리)", placeholder="예: 1234", type="password")
    
        if st.button("로그인"):
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
                st.warning("이름과 휴대폰 번호를 모두 입력해 주세요.")
    
    # ----------------- 입력 화면 -------------------
    elif st.session_state.page == "input":
        st.markdown(f"<h3>📇 {st.session_state['user_name']}님의 전자명함 등록</h3>", unsafe_allow_html=True)
    
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
        st.markdown("### ✏️ 기본 정보 입력")
        fields = {
            "name": "이름", "department": "부서", "position": "직급",
            "mobile": "핸드폰번호", "phone": "전화번호", "fax": "팩스번호",
            "email": "이메일", "introduction": "자기 소개"
        }
    
        profile_data = {}
        for key, label in fields.items():
            placeholder = f"예: {'홍길동' if key == 'name' else '010-1234-5678' if key == 'mobile' else '02-1234-5678' if key == 'phone' else 'example@company.com' if key == 'email' else ''}"
            if key == "introduction":
                profile_data[key] = st.text_area(label, value=default_data.get(key, ""), height=120, placeholder="자유롭게 작성해 주세요.")
            else:
                profile_data[key] = st.text_input(label, value=default_data.get(key, ""), placeholder=placeholder)
    
        # 세션 상태 초기화
        if "histories" not in st.session_state:
            st.session_state.histories = default_data.get("histories", []).copy()
    
        st.markdown("### 🕓 개인 이력 입력")
    
        # 현재 이력 항목 렌더링
        to_delete = None  # 삭제할 인덱스 추적용
        for i, item in enumerate(st.session_state.histories):
            col1, col2, col3 = st.columns([1.5, 4, 1])
            with col1:
                year = st.text_input(f"연도 {i+1}", value=item["year"], key=f"year_{i}")
            with col2:
                desc = st.text_input(f"이력 설명 {i+1}", value=item["desc"], key=f"desc_{i}")
            with col3:
                if st.button("🗑 삭제", key=f"delete_{i}"):
                    to_delete = i
    
            # 업데이트 반영
            st.session_state.histories[i] = {"year": year, "desc": desc}
    
        # 삭제 처리
        if to_delete is not None:
            del st.session_state.histories[to_delete]
            st.experimental_rerun()
    
        # ➕ 이력 추가
        if st.button("➕ 이력 추가"):
            st.session_state.histories.append({"year": "", "desc": ""})
            st.experimental_rerun() 
    
        # --- 저장 시 이력 포함 ---
        profile_data["histories"] = st.session_state.histories
        
        # 📸 프로필 사진 업로드
        st.markdown("")
        st.markdown("###### 📸 프로필 사진 업로드 (정사각형 권장)", unsafe_allow_html=True)
        uploaded_img = st.file_uploader("프로필 사진 선택", type=["png", "jpg", "jpeg"])
    
        if uploaded_img is not None:
            img_save_path = os.path.join(user_folder, "profile.jpg")
            with open(img_save_path, "wb") as f:
                f.write(uploaded_img.read())
            st.success("✅ 프로필 사진이 업로드되었습니다.")
    
        st.markdown("")
        st.markdown("###### 🖼️ 배경화면 선택", unsafe_allow_html=True)
        
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
    
        # 저장 버튼
        if st.button("💾 저장하기"):
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
            st.success("✅ 프로필 정보가 저장되었습니다!")
    
        # 미리보기 버튼
        if st.button("명함 미리보기"):
            session_id = st.session_state['session_id']
            view_url = f"https://goodrich-profile.onrender.com/?page=view&session_id={session_id}"
        
            st.markdown(f"🔗 [👉 새 창에서 명함 보기]({view_url})", unsafe_allow_html=True)
            st.markdown(f"<script>window.open('{view_url}');</script>", unsafe_allow_html=True)
