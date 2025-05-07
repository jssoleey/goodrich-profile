import streamlit as st
import streamlit.components.v1 as components
import os
import re
import json
import base64
import textwrap

st.set_page_config(page_title="전자명함 보기", layout="wide")

st.markdown("""
    <style>
    /* 사이드바 숨기기 */
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    </style>
""", unsafe_allow_html=True)

query_params = st.query_params
session_id = query_params.get("session_id", [None])[0]

user_folder = None
if session_id:
    for folder in os.listdir("data"):
        if session_id in folder:
            user_folder = os.path.join("data", folder)
            break

def format_phone(number: str, type_: str) -> str:
    number = re.sub(r"\D", "", number)
    if type_ == "mobile" or len(number) == 11:
        return f"{number[:3]}.{number[3:7]}.{number[7:]}"
    elif type_ == "fax":
        return f"{number[:2]}.{number[2:6]}.{number[6:]}"
    else:
        return f"{number[:3]}.{number[3:7]}.{number[7:]}" if len(number) == 10 else number

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
                width: 700px;
                height: 500px;
                background-image: url('data:image/png;base64,{bg_base64}');
                background-size: cover;
                background-position: center;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .card {{
                width: 600px;
                height: 300px;
                padding: 25px 35px;
                box-sizing: border-box;
                background-color: #ffffff;
                border: 1px solid #ddd;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
                font-family: sans-serif;
            }}
            .card h2 {{
                font-size: 28px;
                margin: 7px 0 5px 0;
            }}
            .card h5 {{
                font-size: 18px;
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
                                <img src="https://github.com/jssoleey/goodrich-profile/blob/main/image/goodrich.png?raw=true" width="120" />
                            </div>
                        </div>
                        <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-between; font-size: 16px;">
                            <div style="text-align: left; line-height: 0.8;">
                                <p><strong>Mobile.</strong> {mobile}</p>
                                <p><strong>Tel.</strong> {phone}</p>
                                <p><strong>Fax.</strong> {fax}</p>
                                <p><strong>Email.</strong> {email}</p>
                                <p><a href="http://www.goodrich.kr" style="color: #d4922b; text-decoration: none;">www.goodrich.kr</a></p>
                            </div>
                            <div style="text-align: left; font-size: 16px; color: #555;">
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
        components.html(html, height=550)
        
        # 사용자 이름, 직급 정보 불러오기
        name = profile.get("name", "")
        position = profile.get("position", "")
        
        # 이름에 한 글자씩 공백 추가
        spaced_name = " ".join(name)

        st.components.v1.html(f"""
            <div style="display: flex; justify-content: center; margin-top: 50px;">
                <div style="width: 700px; font-family: sans-serif; text-align: center;">
                    <p style="font-size: 30px; margin-bottom: 5px;">안녕하세요.</p>
                    <p style="margin: 0;">
                        <span style="font-size: 36px; font-weight: bold;">{spaced_name} </span> 
                        <span style="font-size: 30px; font-weight: bold;">{position}</span> 
                        <span style="font-size: 30px;">입니다</span>
                    </p>
                </div>
            </div>
        """, height=200)

        
        # 프로필 이미지 표시 (있을 경우)
        img_path = os.path.join(user_folder, "profile.jpg")
        if os.path.exists(img_path):
            img_base64 = get_base64_img(img_path)
            components.html(f"""
                <div style="display: flex; justify-content: center; margin-top: 70px;">
                    <div style="
                        width: 300px; height: 300px;
                        border-radius: 50%;
                        overflow: hidden;
                        border: 2px solid #ddd;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    ">
                        <img src="data:image/png;base64,{img_base64}" style="width: 100%; height: 100%; object-fit: cover;" />
                    </div>
                </div>
            """, height=460)
            
        mobile = profile.get("mobile", "")
        email = profile.get("email", "")
        fax = profile.get("fax", "")

        st.components.v1.html(f"""
        <div style="display: flex; justify-content: center; margin-top: 47px;">
        <div style="width: 500px; font-family: sans-serif;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 28px; margin-right: 8px;">☎</span>
                <span style="font-size: 28px; color: #888;">phone</span>
            </div>
            <span style="font-size: 28px; color: #000;">{mobile}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 28px; margin-right: 8px;">✉</span>
                <span style="font-size: 28px; color: #888;">e-mail</span>
            </div>
            <span style="font-size: 28px; color: #000;">{email}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 28px; margin-right: 8px;">🖷</span>
                <span style="font-size: 28px; color: #888;">fax</span>
            </div>
            <span style="font-size: 28px; color: #000;">{fax}</span>
            </div>
        </div>
        </div>
        """, height=220)


        # 소개글 줄 수 계산 함수 (엔터 + 길이 기준 자동 줄바꿈 포함)
        def estimate_line_count(text, chars_per_line=45):
            lines = text.split("\n")
            count = 0
            for line in lines:
                wrapped = textwrap.wrap(line, width=chars_per_line)
                count += max(1, len(wrapped))
            return count

        line_count = estimate_line_count(introduction, chars_per_line=45)
        line_height_px = 80  # ← 폰트 크기에 맞춰 조정
        base_height = 250
        dynamic_height = base_height + (line_count * line_height_px)

        components.html(
            f"""
            <div style="display: flex; justify-content: center; margin-top: 100px;">
                <div style="width: 700px; padding: 30px; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-family: sans-serif;">
                    <link rel="preconnect" href="https://fonts.googleapis.com">
                    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                    <link href="https://fonts.googleapis.com/css2?family=Galada&display=swap" rel="stylesheet">
                    <div style="
                        font-family: 'Galada', cursive;
                        font-size: 40px;
                        text-align: center;
                        color: #f79901;
                        margin-top: 20px;
                        margin-bottom: 50px;
                    ">
                        INTRODUCTION
                    </div>
                    <p style="font-size: 30px; color: #333; text-align: center; line-height: 1.6; white-space: pre-wrap;">{introduction}</p>
                </div>
            </div>
            """,
            height=dynamic_height
        )
        
    histories = profile.get("histories", [])
    
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
        <div style="display: flex; justify-content: center; margin-top: 100px;">
            <div style="width: 700px; padding: 30px; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-family: sans-serif;">
                <link rel="preconnect" href="https://fonts.googleapis.com">
                    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                    <link href="https://fonts.googleapis.com/css2?family=Galada&display=swap" rel="stylesheet">
                    <div style="
                        font-family: 'Galada', cursive;
                        font-size: 40px;
                        text-align: center;
                        color: #f79901;
                        margin-top: 20px;
                        margin-bottom: 50px;
                    ">
                        CARRIER
                    </div>
                <div style="position: relative; padding-left: 28px; border-left: 4px solid #f79901;">
                    <style>
                        .item {{
                            position: relative;
                            margin-bottom: 40px;
                        }}
                        .dot {{
                            width: 14px;
                            height: 14px;
                            background: #f79901;
                            border-radius: 50%;
                            position: absolute;
                            left: -9px;
                            top: 6px;
                        }}
                        .content {{
                            margin-left: 50px;
                        }}
                        .year {{
                            font-weight: bold;
                            font-size: 30px;
                            color: #666;
                            margin-bottom: 6px;
                        }}
                        .desc {{
                            font-size: 30px;
                            color: #222;
                            line-height: 1.5;
                        }}
                    </style>
                    {timeline_items}
                </div>
            </div>
        </div>
        """, height=360 + len(histories) * 120)

        map_embed_code = """
        <div style="display: flex; justify-content: center; margin-top: 100px;">
            <div style="width: 700px; padding: 30px; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-family: sans-serif;">
                    <link rel="preconnect" href="https://fonts.googleapis.com">
                    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                    <link href="https://fonts.googleapis.com/css2?family=Galada&display=swap" rel="stylesheet">
                    <div style="
                        font-family: 'Galada', cursive;
                        font-size: 40px;
                        text-align: center;
                        color: #f79901;
                        margin-top: 20px;
                        margin-bottom: 50px;
                    ">
                        LOCATION
                    </div>
                <iframe 
                    width="700" 
                    height="400" 
                    frameborder="0" 
                    style="border:0" 
                    src="https://www.google.com/maps?q=서울시 중구 퇴계로36가길 10 402호&output=embed" 
                    allowfullscreen>
                </iframe>
        </div>
        """

        st.components.v1.html(map_embed_code, height=800)

    else:
        st.error("⚠️ 배경 이미지가 존재하지 않습니다.")
