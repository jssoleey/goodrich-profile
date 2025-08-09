import streamlit as st
import streamlit.components.v1 as components
import os
import re
import json
import base64
import textwrap
import qrcode
from io import BytesIO

st.set_page_config(page_title="전자명함 보기", layout="wide")

# session_id 처리 및 경로 설정
session_id = st.query_params.get("session_id")
if not session_id:
    st.error("session_id가 포함되지 않았습니다.")
    st.stop()

DATA_DIR = "/data"
user_folder = os.path.join(DATA_DIR, session_id)
profile_path = os.path.join(user_folder, "profile.json")

if not os.path.exists(profile_path):
    st.error("⚠️ 아직 명함 정보가 저장되지 않았습니다.")
    st.stop()

# profile.json 로드
with open(profile_path, "r", encoding="utf-8") as f:
    profile_data = json.load(f)

background_color = profile_data.get("background_color", "#ffffff")

st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-color: {background_color} !important;
    }}
    /* 사이드바 숨기기 */
    [data-testid="stSidebar"] {{display: none;}}
    [data-testid="collapsedControl"] {{display: none;}}
    </style>
""", unsafe_allow_html=True)

query_params = st.query_params
session_id = st.query_params.get("session_id")
if not session_id:
    st.error("session_id가 URL에 포함되지 않았습니다.")
    st.stop()

user_folder = None
if session_id:
    user_folder = os.path.join("/data", session_id)
    if not os.path.exists(user_folder):
        st.error("❌ 존재하지 않는 session_id입니다.")
        st.stop()

# (아래에 profile.json 체크도 같이)
profile_path = os.path.join(user_folder, "profile.json")
if not os.path.exists(profile_path):
    st.error("⚠️ 아직 명함 정보가 저장되지 않았습니다.")
    st.stop()

def format_phone(number: str, type_: str) -> str:
    number = re.sub(r"\D", "", number)
    length = len(number)

    if type_ == "mobile" or length == 11:
        # 11자리 → 3.4.4
        return f"{number[:3]}.{number[3:7]}.{number[7:]}"
    elif length == 10:
        # 10자리 → 2.4.4
        return f"{number[:2]}.{number[2:6]}.{number[6:]}"
    else:
        return number  # 형식 정의 외의 경우 원본 반환

def get_base64_img(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

if user_folder and os.path.exists(os.path.join(user_folder, "profile.json")):
    with open(os.path.join(user_folder, "profile.json"), encoding="utf-8") as f:
        profile = json.load(f)

    name = profile.get("name", "")
    department = profile.get("department", "")
    position = profile.get("position", "")
    mobile = format_phone(profile.get("mobile", ""), "mobile")
    phone = format_phone(profile.get("phone", ""), "phone")
    fax = format_phone(profile.get("fax", ""), "fax")
    email = profile.get("email", "")
    introduction = profile.get("introduction", "")
    # ✅ 테마 색상 불러오기 (기본값 유지)
    theme_color = profile.get("theme_color", "#f79901")

    bg_file = profile.get("background_image", "bg1.png")  # profile.json의 키 이름을 정확히
    background_img_path = os.path.join("backgrounds", bg_file)

    
    if os.path.exists(background_img_path):
        bg_base64 = get_base64_img(background_img_path)

        # 명함 영역만 HTML로 구성
        html = f"""
        <html>
        <head>
        <style>
            body {{
                margin: 0;
                width: 100vw;
                height: 100vh;
                background-color: transparent;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .wrapper {{
                width: 400px;
                height: 250px;
                background-image: url('data:image/png;base64,{bg_base64}');
                background-size: cover;
                background-position: center;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .card {{
                width: 300px;
                height: 150px;
                padding: 10px 15px;
                box-sizing: border-box;
                background-color: #ffffff;
                border: 1px solid #ddd;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
                font-family: sans-serif;
            }}
            .card h2 {{
                font-size: 13px;
                margin: 2px 0 0 0;
            }}
            .card h5 {{
                font-size: 8px;
                margin: 0;
                color: gray;
            }}
        </style>
        </head>
        <body>
            <div class="wrapper">
                <div class="card">
                    <div style="display: flex; justify-content: space-between; height: 100%;">
                        <div style="flex: 1.1; display: flex; flex-direction: column; justify-content: space-between;">
                            <div>
                                <h2>{name}</h2>
                                <h5>{department} | {position}</h5>
                            </div>
                            <div>
                                <img src="https://github.com/jssoleey/goodrich-profile/blob/main/image/goodrich.png?raw=true" width="50" />
                            </div>
                        </div>
                        <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-between; font-size: 8px;">
                            <div style="text-align: left; line-height: 0.5;">
                                <p><strong>Mobile.</strong> {mobile}</p>
                                <p><strong>Tel.</strong> {phone}</p>
                                <p><strong>Fax.</strong> {fax}</p>
                                <p><strong>Email.</strong> {email}</p>
                                <p><a href="http://www.goodrich.kr" style="color: #d4922b; text-decoration: none;">www.goodrich.kr</a></p>
                            </div>
                            <div style="text-align: left; font-size: 8px; color: #555;">
                                <p>서울시 중구 퇴계로36가길 10, 402호</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        # 명함(배경 포함)은 고정 영역
        components.html(html, height=300)
        
        # 사용자 이름, 직급 정보 불러오기
        name = profile.get("name", "")
        position = profile.get("position", "")
        
        # 이름에 한 글자씩 공백 추가
        spaced_name = " ".join(name)

        st.components.v1.html(f"""
            <div style="display: flex; justify-content: center; margin-top: 0;">
                <div style="width: 350px; font-family: sans-serif; text-align: center;">
                    <p style="font-size: 20px; margin-bottom: 5px;">안녕하세요.</p>
                    <p style="margin: 0;">
                        <span style="font-size: 24px; font-weight: bold;">{spaced_name} </span> 
                        <span style="font-size: 20px; font-weight: bold;">{position}</span> 
                        <span style="font-size: 20px;">입니다.</span>
                    </p>
                </div>
            </div>
        """, height=120)

        
        # -------------------- 프로필 이미지 --------------------
        img_path = os.path.join(user_folder, "profile.jpg")
        if os.path.exists(img_path):
            img_base64 = get_base64_img(img_path)
            components.html(f"""
                <div style="display: flex; justify-content: center; margin-top: 0;">
                    <div style="
                        width: 150px; height: 150px;
                        border-radius: 35%;
                        overflow: hidden;
                        border: 2px solid #ddd;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    ">
                        <img src="data:image/png;base64,{img_base64}" style="width: 100%; height: 100%; object-fit: cover;" />
                    </div>
                </div>
            """, height=200) 
            
        # -------------------- 전화/문자 버튼 --------------------
        clean_mobile = re.sub(r"\D", "", profile.get("mobile", ""))  # 숫자만 추출

        st.components.v1.html(f"""
            <div style="display: flex; justify-content: center; gap: 30px; margin-top: 0;">
                <a href="tel:{clean_mobile}" style="
                    background-color: {theme_color};
                    width: 55px;
                    height: 50px;
                    color: white;
                    text-decoration: none;
                    padding-bottom: 4px;
                    border-radius: 50%;
                    font-weight: bold;
                    font-size: 35px;
                    align-items: center;
                    justify-content: center;
                    display: flex;
                    line-height: 5;
                ">
                    ✆
                </a>
                <a href="sms:{clean_mobile}" style="
                    background-color: #888888;
                    width: 55px;
                    height: 50px;
                    color: white;
                    text-decoration: none;
                    padding-bottom: 4px;
                    border-radius: 50%;
                    font-size: 30px;
                    align-items: center;
                    justify-content: center;
                    display: flex;
                    line-height: 0;
                ">
                    ✉
                </a>
            </div>
        """, height=65)  
            
        # -------------------- 전화번호, 이메일, 팩스 --------------------
        mobile = format_phone(profile.get("mobile", ""), "mobile")
        email = profile.get("email", "")
        fax = format_phone(profile.get("fax", ""), "fax")

        st.components.v1.html(f"""
        <div style="display: flex; justify-content: center; margin-top: 0;">
        <div style="width: 240px; font-family: sans-serif;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 14px; margin-right: 8px; font-weight: bold;">☎</span>
                <span style="font-size: 14px; color: #888; font-weight: bold;">Mobile</span>
            </div>
            <span style="font-size: 14px; color: #000; font-weight: bold;">{mobile}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 14px; margin-right: 8px; font-weight: bold;">✉</span>
                <span style="font-size: 14px; color: #888; font-weight: bold;">E-mail</span>
            </div>
            <span style="font-size: 14px; color: #000; font-weight: bold;">{email}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 14px; margin-right: 8px; font-weight: bold;">🖷</span>
                <span style="font-size: 14px; color: #888; font-weight: bold;">Fax</span>
            </div>
            <span style="font-size: 14px; color: #000; font-weight: bold;">{fax}</span>
            </div>
        </div>
        </div>
        """, height=130)

    # -------------------- INTRODUCTION --------------------
        def get_wrapped_text_and_line_count(text: str, chars_per_line: int = 20):
            wrapped_lines = []
            for line in text.split("\n"):
                wrapped = textwrap.wrap(line, width=chars_per_line)
                wrapped_lines.extend(wrapped if wrapped else [""])  # 빈 줄 유지
            return "\n".join(wrapped_lines), len(wrapped_lines)

        # 자동 줄바꿈 적용
        wrapped_intro, line_count = get_wrapped_text_and_line_count(introduction, chars_per_line=20)

        # 동적 높이 계산 (기본 149 + 줄 수 당 +23)
        dynamic_height = 149 + (line_count - 1) * 24

        # 컴포넌트 출력
        components.html(
            f"""
            <div style="display: flex; justify-content: center; margin-top: 0;">
                <div style="width: 350px; padding: 15px 0 15px 0; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-family: sans-serif; overflow: auto;">
                    <link rel="preconnect" href="https://fonts.googleapis.com">
                    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                    <link href="https://fonts.googleapis.com/css2?family=Galada&display=swap" rel="stylesheet">
                    <div style="
                        font-family: 'Galada', cursive;
                        font-size: 20px;
                        text-align: center;
                        color: {theme_color};
                        margin-top: 10px;
                        margin-bottom: 25px;
                    ">
                        INTRODUCTION
                    </div>
                    <p style="font-size: 15px; color: #333; text-align: center; line-height: 1.6; white-space: pre-wrap;">{wrapped_intro}</p>
                </div>
            </div>
            """,
            height=dynamic_height + 40
        )
    
    
    # -------------------- CAREER --------------------    
    histories = profile.get("histories", [])
    
    num_items = len(histories)
    dynamic_timeline_height = 177 + (num_items - 1) * 78
    
    if histories:
        timeline_items = ""
        for item in histories:
            timeline_items += f"""
            <div class="item">
                <div class="dot"></div>
                <div class="line"></div>
                <div class="content">
                    <div class="year">{item['year']}</div>
                    <div class="desc">{item['desc']}</div>
                </div>
            </div>
            """

        components.html(f"""
        <div style="display: flex; justify-content: center; margin-top: 0;">
            <div style="width: 350px; padding: 15px 0 0 0; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-family: sans-serif;">
                <link rel="preconnect" href="https://fonts.googleapis.com">
                    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                    <link href="https://fonts.googleapis.com/css2?family=Galada&display=swap" rel="stylesheet">
                    <div style="
                        font-family: 'Galada', cursive;
                        font-size: 20px;
                        text-align: center;
                        color: {theme_color};
                        margin-top: 10px;
                        margin-bottom: 25px;
                    ">
                        CAREER
                    </div>
                <div style="position: relative; padding-left: 14px; border-left: 4px solid {theme_color}; margin-left: 30px;">
                    <style>
                        .item {{
                            position: relative;
                            margin-bottom: 40px;
                        }}
                        .dot {{
                            width: 7px;
                            height: 7px;
                            background: {theme_color};
                            border-radius: 50%;
                            position: absolute;
                            left: -9px;
                            top: 6px;
                        }}
                        .content {{
                            margin-left: 25px;
                        }}
                        .year {{
                            font-weight: bold;
                            font-size: 13px;
                            color: #666;
                            margin-bottom: 4px;
                        }}
                        .desc {{
                            font-size: 13px;
                            color: #222;
                            line-height: 1.5;
                        }}
                    </style>
                    {timeline_items}
                </div>
            </div>
        </div>
        """, height=dynamic_timeline_height+40)
        
        # -------------------- GALLERY --------------------
        photos_dir = os.path.join(user_folder, "photos")
        photo_files = sorted([
            f for f in os.listdir(photos_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]) if os.path.exists(photos_dir) else []

        if photo_files:
            slide_items = ""
            for file in photo_files:
                img_path = os.path.join(photos_dir, file)
                img_base64 = get_base64_img(img_path)
                slide_items += f"""
                <div class="swiper-slide">
                    <div style="text-align: center;">
                        <img src="data:image/png;base64,{img_base64}" style="width: 90%; border-radius: 10px;" />
                    </div>
                </div>
                """

            gallery_html = f"""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css"/>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Galada&display=swap" rel="stylesheet">
            
            <div style="display: flex; justify-content: center; margin: 0;">
                <div style="width: 100%; max-width: 350px; padding: 15px 0 15px 0; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-family: sans-serif;">
                    <div style="font-family: 'Galada', cursive; font-size: 20px; text-align: center; color: {theme_color}; margin-top: 10px; margin-bottom: 25px;">
                        GALLERY
                    </div>
                    <div class="swiper mySwiper">
                        <div class="swiper-wrapper">
                            {slide_items}
                        </div>
                        <div class="swiper-pagination"></div>
                    </div>
                </div>
            </div>
            <style>
            .swiper-pagination {{
                position: relative !important;
                margin-top: 15px !important;
                text-align: center;
            }}
            .swiper-slide {{
                box-sizing: border-box;
                overflow: visible !important;
            }}
            .swiper {{
                overflow: visible !important;
            }}
            </style>
            <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
            <script>
            const swiper = new Swiper('.mySwiper', {{
                loop: true,
                pagination: {{
                el: '.swiper-pagination',
                clickable: true,
                }},
            }});
            </script>
            """

            components.html(gallery_html, height=530)
        
        # -------------------- LOCATION --------------------
        map_embed_code_1 = f"""
        <div style="display: flex; justify-content: center; margin-top: 20px;">
            <div style="width: 350px; padding: 15px 0 15px 0; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-family: sans-serif;">        
                    <link rel="preconnect" href="https://fonts.googleapis.com">
                    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                    <link href="https://fonts.googleapis.com/css2?family=Galada&display=swap" rel="stylesheet">
                    <div style="
                        font-family: 'Galada', cursive;
                        font-size: 20px;
                        text-align: center;
                        color: {theme_color};
                        margin-top: 10px;
                        margin-bottom: 25px;
                    ">
                        LOCATION
                    </div>
                <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                    <iframe 
                        src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3162.7931805361027!2d126.99256707537455!3d37.55993622450737!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x357ca2fd321494bd%3A0xf5909385d0ea334a!2z7ISc7Jq47Yq567OE7IucIOykkeq1rCDth7Tqs4TroZwzNuqwgOq4uCAxMCA0MDLtmLg!5e0!3m2!1sko!2skr!4v1746646834956!5m2!1sko!2skr" 
                        width="280" 
                        height="280" 
                        style="border:0;" 
                        allowfullscreen="" 
                        loading="lazy" 
                        referrerpolicy="no-referrer-when-downgrade">
                    </iframe>
                </div>
        </div>
        """

        st.components.v1.html(map_embed_code_1, height=450)
        
        map_embed_code_2 = f"""
        <div style="display: flex; justify-content: center; margin-top: 20px;">
            <div style="width: 350px; padding: 15px 0 15px 0; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-family: sans-serif;">        
                    <link rel="preconnect" href="https://fonts.googleapis.com">
                    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                    <link href="https://fonts.googleapis.com/css2?family=Galada&display=swap" rel="stylesheet">
                    <div style="
                        font-family: 'Galada', cursive;
                        font-size: 20px;
                        text-align: center;
                        color: {theme_color};
                        margin-top: 10px;
                        margin-bottom: 25px;
                    ">
                        LOCATION
                    </div>
                <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                    <iframe 
                        src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3161.3754490458277!2d126.67243081174992!3d37.59332192247461!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x357c81755bc22b71%3A0xa77f2b563324335b!2z7J247LKc6rSR7Jet7IucIOyEnOq1rCDsm5Dri7nrjIDroZwgNjY0!5e0!3m2!1sko!2skr!4v1754748227822!5m2!1sko!2skr" 
                        width="280" 
                        height="280" 
                        style="border:0;" 
                        allowfullscreen="" 
                        loading="lazy" 
                        referrerpolicy="no-referrer-when-downgrade">
                    </iframe>
                </div>
        </div>
        """

        st.components.v1.html(map_embed_code_2, height=450)
        
        # -------------------- QR code --------------------
        def generate_qr_code(url: str):
            qr = qrcode.QRCode(box_size=3, border=2)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buf = BytesIO()
            img.save(buf, format="PNG")
            img_base64 = base64.b64encode(buf.getvalue()).decode()
            return img_base64

        # 명함 링크 생성
        base_url = "https://goodrich-profile.onrender.com/view"  # ← 배포된 주소에 맞게 수정!
        qr_url = f"{base_url}?session_id={session_id}"

        # QR 이미지 생성
        qr_base64 = generate_qr_code(qr_url)

        # 하단에 표시
        st.markdown("")
        st.components.v1.html(f"""
            <div style="display: flex; justify-content: center; margin-top: 0;">
                <div style="text-align: center;">
                    <img src="data:image/png;base64,{qr_base64}" width="60" />
                </div>
            </div>
        """, height=100)
        
        # -------------------- 보험사 연락처 --------------------
        st.markdown("<hr style='margin-top: 30px; margin-bottom: 10px;'>", unsafe_allow_html=True)

        st.components.v1.html("""
            <div style="font-size: 11px; color: #666; text-align: center; font-family: sans-serif; line-height: 1.5;">
                <div style="font-weight: bold; margin-bottom: 6px;">[손해보험]</div>
                <div>메리츠화재 1566-7711&nbsp;&nbsp;&nbsp;&nbsp;KB손해 1544-0114</div>
                <div>현대해상 1588-5656&nbsp;&nbsp;&nbsp;&nbsp;DB손해보험 1588-0100</div>
                <div>롯데손해보험 1588-3344&nbsp;&nbsp;&nbsp;&nbsp;MG손해보험 1588-5959</div>
                <div>삼성화재 1588-5114&nbsp;&nbsp;&nbsp;&nbsp;한화손해보험 1566-8000</div>

                <div style="margin-top: 10px; font-weight: bold; margin-bottom: 6px;">[생명보험]</div>
                <div>메트라이프 1588-9600&nbsp;&nbsp;&nbsp;&nbsp;AIA생명 1588-9898</div>
                <div>동양생명 1577-1004&nbsp;&nbsp;&nbsp;&nbsp;라이나생명 1588-0058</div>
                <div>삼성생명 1588-3114&nbsp;&nbsp;&nbsp;&nbsp;처브라이프 1566-5860</div>
                <div>한화생명 1588-6363&nbsp;&nbsp;&nbsp;&nbsp;흥국생명 1588-2288</div>
                <div>DB생명 1588-3131</div>
            </div>
        """, height=210)


    else:
        st.error("⚠️ 배경 이미지가 존재하지 않습니다.")

