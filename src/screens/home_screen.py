import streamlit as st
from src.ui.base_layout import style_base_layout


def home_screen():
    style_base_layout()

    st.html("""
    <style>
        .smart-background {
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            pointer-events: none;
            z-index: 0;
        }

        .smart-bg-orbit {
            position: absolute;
            width: 365px;
            height: 345px;
            left: 57%;
            top: 55%;
            transform: translate(-50%, -50%) rotate(-23deg);
            border: 2px dashed rgba(54,119,220,.25);
            border-left-color: transparent;
            border-bottom-color: transparent;
            border-radius: 50%;
        }

        .smart-bg-robot {
            position: absolute;
            width: 330px;
            height: 365px;
            left: 57%;
            top: 55%;
            transform: translate(-50%, -50%);
            opacity: .92;
            filter: drop-shadow(0 20px 28px rgba(42,100,190,.13));
        }

        .smart-bg-book {
            position: absolute;
            left: 39%;
            bottom: 8%;
            font-size: 58px;
            opacity: .17;
            transform: rotate(-12deg);
        }

        .smart-bg-cap {
            position: absolute;
            left: 54%;
            top: 17%;
            font-size: 34px;
            opacity: .22;
            transform: rotate(-12deg);
        }

        .smart-bg-paper {
            position: absolute;
            left: 46%;
            top: 28%;
            font-size: 37px;
            opacity: .18;
            transform: rotate(15deg);
        }

        .smart-bg-star {
            position: absolute;
            color: #72a5eb;
            opacity: .28;
            font-size: 20px;
        }

        .smart-bg-star.one {
            left: 51%;
            top: 22%;
        }

        .smart-bg-star.two {
            left: 67%;
            top: 41%;
        }

        .smart-bg-star.three {
            left: 45%;
            top: 54%;
            font-size: 14px;
        }

        .smart-bg-note {
            position: absolute;
            color: rgba(65,96,140,.34);
            font-size: 13px;
            line-height: 1.25;
            font-style: italic;
        }

        .smart-bg-note.left {
            left: 39%;
            bottom: 20%;
            transform: rotate(-5deg);
        }

        .smart-bg-note.right {
            right: 9%;
            bottom: 24%;
            transform: rotate(4deg);
        }

        .smart-navbar {
            position: relative;
            z-index: 10;
            height: 62px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 25px;
        }

        .smart-logo {
            font-size: 27px;
            line-height: 1;
            font-weight: 850;
            letter-spacing: -1.2px;
            color: #172b4d;
        }

        .smart-logo span {
            color: #2d73e8;
        }

        .smart-nav {
            display: flex;
            align-items: center;
            gap: 34px;
        }

        .smart-nav-item {
            color: #64758e;
            font-size: 14px;
            font-weight: 650;
        }

        .smart-nav-item.active {
            color: #2d73e8;
        }

        .hero-area {
            position: relative;
            z-index: 5;
            min-height: calc(100vh - 125px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding-left: 5%;
            padding-bottom: 30px;
        }

        .ai-badge {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            width: fit-content;
            padding: 7px 14px;
            border: 1px solid #a8caff;
            border-radius: 30px;
            background: rgba(255,255,255,.56);
            color: #2d73e8;
            font-size: 11px;
            font-weight: 750;
            margin-bottom: 18px;
            box-shadow: 0 6px 20px rgba(66,116,180,.05);
        }

        .ai-badge span {
            color: #70829b;
            font-weight: 600;
        }

        .hero-title {
            max-width: 790px;
            color: #13284b;
            font-size: clamp(40px, 4.15vw, 65px);
            line-height: .99;
            letter-spacing: -3px;
            font-weight: 850;
        }

        .hero-title span {
            color: #2d73e8;
        }

        .hero-description {
            max-width: 550px;
            margin-top: 19px;
            color: #637996;
            font-size: 15px;
            line-height: 1.58;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(4, 140px);
            gap: 13px;
            margin-top: 25px;
        }

        .feature-item {
            min-height: 90px;
        }

        .feature-icon {
            width: 39px;
            height: 39px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #e4edff;
            font-size: 18px;
            margin-bottom: 8px;
        }

        .feature-item:nth-child(2) .feature-icon {
            background: #e4f6ff;
        }

        .feature-item:nth-child(3) .feature-icon {
            background: #eee8ff;
        }

        .feature-item:nth-child(4) .feature-icon {
            background: #ffedf2;
        }

        .feature-title {
            color: #20385a;
            font-size: 12px;
            font-weight: 750;
            white-space: nowrap;
        }

        .feature-text {
            color: #8596ad;
            font-size: 10px;
            margin-top: 4px;
            white-space: nowrap;
        }

        .portal-column {
            position: relative;
            z-index: 20;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: calc(100vh - 125px);
            padding-right: 0;
            transform: translateX(-45px);
        }

        .st-key-portal_card {
            width: 100%;
            max-width: 385px;
            padding: 30px !important;
            border-radius: 27px !important;
            background: rgba(255,255,255,.86) !important;
            border: 1px solid rgba(186,211,242,.7) !important;
            box-shadow: 0 24px 65px rgba(48,91,145,.14) !important;
            backdrop-filter: blur(17px);
        }

        .portal-title {
            color: #14284b;
            font-size: 30px;
            line-height: 1.06;
            font-weight: 850;
            letter-spacing: -1px;
        }

        .portal-title span {
            color: #2d73e8;
        }

        .portal-subtitle {
            color: #8192a8;
            font-size: 13px;
            margin-top: 9px;
            margin-bottom: 22px;
        }

        .portal-info {
            display: flex;
            align-items: center;
            gap: 11px;
            margin-top: 18px;
            padding: 14px;
            border-radius: 14px;
            background: #eef5ff;
        }

        .portal-info-icon {
            width: 36px;
            height: 36px;
            flex-shrink: 0;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #dceaff;
            font-size: 17px;
        }

        .portal-info strong {
            display: block;
            color: #294363;
            font-size: 12px;
        }

        .portal-info small {
            display: block;
            margin-top: 3px;
            color: #8193aa;
            font-size: 10px;
        }

        .st-key-home_teacher_portal button,
        .st-key-home_student_portal button {
            min-height: 51px !important;
            border-radius: 13px !important;
            font-size: 14px !important;
            font-weight: 700 !important;
        }

        .st-key-home_teacher_portal button {
            background: #2d73e8 !important;
            border-color: #2d73e8 !important;
            color: white !important;
            box-shadow: 0 10px 23px rgba(45,115,232,.22) !important;
        }

        .st-key-home_student_portal button {
            background: #f2f6fd !important;
            border: 1px solid #cfdef2 !important;
            color: #456488 !important;
        }

        .smart-footer {
            position: fixed;
            left: 42px;
            bottom: 13px;
            z-index: 20;
            color: #8a9bb1;
            font-size: 10px;
        }

        @media (max-height: 720px) and (min-width: 701px) {
            .smart-navbar {
                height: 52px;
            }

            .hero-area,
            .portal-column {
                min-height: calc(100vh - 105px);
            }

            .hero-title {
                font-size: 48px;
            }

            .hero-description {
                margin-top: 13px;
            }

            .feature-grid {
                margin-top: 17px;
            }

            .feature-item {
                min-height: 75px;
            }

            .st-key-portal_card {
                padding: 23px !important;
            }

            .portal-title {
                font-size: 25px;
            }

            .smart-bg-robot {
                width: 275px;
                height: 305px;
            }

            .smart-bg-orbit {
                width: 305px;
                height: 290px;
            }
        }

        @media (max-width: 1050px) {
            .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }

            .smart-navbar {
                padding: 0 14px;
            }

            .hero-area {
                padding-left: 2%;
            }

            .feature-grid {
                grid-template-columns: repeat(2, 140px);
            }

            .smart-bg-robot {
                left: 56%;
                opacity: .45;
            }

            .smart-bg-orbit {
                left: 56%;
            }

            .portal-column {
                padding-right: 1%;
            }

            .st-key-portal_card {
                max-width: 330px;
                padding: 24px !important;
            }
        }

        @media (max-width: 700px) {
            html,
            body {
                overflow-x: hidden !important;
                overflow-y: auto !important;
            }

            .block-container {
                padding: 0 12px 20px !important;
            }

            .smart-navbar {
                height: 58px;
                padding: 0 8px;
            }

            .smart-logo {
                font-size: 22px;
            }

            .smart-nav {
                gap: 11px;
            }

            .smart-nav-item {
                font-size: 10px;
            }

            .hero-area {
                min-height: auto;
                padding: 28px 4% 15px;
            }

            .hero-title {
                font-size: 40px;
                line-height: 1;
                letter-spacing: -2px;
            }

            .hero-description {
                font-size: 13px;
                margin-top: 16px;
            }

            .feature-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 15px;
                margin-top: 22px;
            }

            .feature-item {
                min-height: 78px;
            }

            .feature-title,
            .feature-text {
                white-space: normal;
            }

            .portal-column {
                min-height: auto;
                display: block;
                padding: 10px 4% 35px;
            }

            .st-key-portal_card {
                max-width: none;
                padding: 23px !important;
            }

            .smart-bg-robot {
                width: 250px;
                height: 280px;
                left: 79%;
                top: 31%;
                opacity: .13;
            }

            .smart-bg-orbit {
                width: 275px;
                height: 245px;
                left: 79%;
                top: 31%;
                opacity: .18;
            }

            .smart-bg-book,
            .smart-bg-cap,
            .smart-bg-paper,
            .smart-bg-note {
                opacity: .08;
            }

            .smart-footer {
                position: relative;
                left: auto;
                bottom: auto;
                padding: 0 4% 18px;
            }
        }
    </style>
    """)

    st.html("""
    <div class="smart-background">

        <div class="smart-bg-orbit"></div>

        <svg class="smart-bg-robot"
             viewBox="0 0 300 330"
             xmlns="http://www.w3.org/2000/svg">

            <ellipse cx="150" cy="310" rx="72" ry="14"
                     fill="rgba(40,90,180,.10)"/>

            <rect x="172" y="98" width="48" height="66" rx="16"
                  fill="#dceaff"
                  stroke="#78aefc"
                  stroke-width="3"/>

            <rect x="183" y="106" width="8" height="48" rx="4"
                  fill="#bcd8ff"/>

            <rect x="92" y="112" width="116" height="135" rx="42"
                  fill="#ffffff"
                  stroke="#78aefc"
                  stroke-width="4"/>

            <rect x="105" y="130" width="90" height="70" rx="30"
                  fill="#e9f4ff"/>

            <circle cx="130" cy="164" r="10" fill="#2d73e8"/>
            <circle cx="170" cy="164" r="10" fill="#2d73e8"/>

            <circle cx="127" cy="161" r="3" fill="#ffffff"/>
            <circle cx="167" cy="161" r="3" fill="#ffffff"/>

            <path d="M132 184 Q150 198 168 184"
                  fill="none"
                  stroke="#397bdc"
                  stroke-width="4"
                  stroke-linecap="round"/>

            <rect x="125" y="80" width="50" height="40" rx="18"
                  fill="#ffffff"
                  stroke="#78aefc"
                  stroke-width="4"/>

            <circle cx="150" cy="92" r="7" fill="#3b82f6"/>

            <line x1="150" y1="80"
                  x2="150" y2="62"
                  stroke="#4d8ff0"
                  stroke-width="4"
                  stroke-linecap="round"/>

            <circle cx="150" cy="57" r="6" fill="#70a7ff"/>

            <rect x="75" y="138" width="28" height="78" rx="14"
                  fill="#ffffff"
                  stroke="#78aefc"
                  stroke-width="4"/>

            <rect x="197" y="138" width="28" height="78" rx="14"
                  fill="#ffffff"
                  stroke="#78aefc"
                  stroke-width="4"/>

            <circle cx="89" cy="218" r="12" fill="#dbeaff"/>
            <circle cx="211" cy="218" r="12" fill="#dbeaff"/>

            <rect x="112" y="240" width="30" height="55" rx="15"
                  fill="#ffffff"
                  stroke="#78aefc"
                  stroke-width="4"/>

            <rect x="158" y="240" width="30" height="55" rx="15"
                  fill="#ffffff"
                  stroke="#78aefc"
                  stroke-width="4"/>

            <rect x="108" y="286" width="38" height="16" rx="8"
                  fill="#3d82e8"/>

            <rect x="154" y="286" width="38" height="16" rx="8"
                  fill="#3d82e8"/>

            <g transform="translate(184 204) rotate(-10)">

                <rect x="-5" y="7"
                      width="70"
                      height="46"
                      rx="5"
                      fill="#eaf3ff"
                      stroke="#a9cdfb"
                      stroke-width="2"/>

                <rect x="0" y="0"
                      width="70"
                      height="48"
                      rx="5"
                      fill="#ffffff"
                      stroke="#4b8ff0"
                      stroke-width="3"/>

                <line x1="35" y1="2"
                      x2="35" y2="46"
                      stroke="#8db9f8"
                      stroke-width="2"/>

                <line x1="10" y1="14"
                      x2="27" y2="14"
                      stroke="#72a6ed"
                      stroke-width="3"
                      stroke-linecap="round"/>

                <line x1="43" y1="14"
                      x2="60" y2="14"
                      stroke="#72a6ed"
                      stroke-width="3"
                      stroke-linecap="round"/>

                <line x1="10" y1="24"
                      x2="27" y2="24"
                      stroke="#b4cef3"
                      stroke-width="3"
                      stroke-linecap="round"/>

                <line x1="43" y1="24"
                      x2="60" y2="24"
                      stroke="#b4cef3"
                      stroke-width="3"
                      stroke-linecap="round"/>

            </g>

        </svg>

        <div class="smart-bg-book">📚</div>
        <div class="smart-bg-cap">🎓</div>
        <div class="smart-bg-paper">✈</div>

        <div class="smart-bg-star one">✦</div>
        <div class="smart-bg-star two">✦</div>
        <div class="smart-bg-star three">✧</div>

        <div class="smart-bg-note left">
            Better Students<br>
            Brighter Futures ♡
        </div>

        <div class="smart-bg-note right">
            Learning Today<br>
            A Smarter Tomorrow ♡
        </div>

    </div>
    """)

    st.html("""
    <div class="smart-navbar">

        <div class="smart-logo">
            Smart<span>Attend</span>
        </div>

        <div class="smart-nav">
            <div class="smart-nav-item active">Home</div>
        </div>

    </div>
    """)

    left_col, right_col = st.columns([1.55, 0.82], gap="large")

    with left_col:

        st.html("""
        <div class="hero-area">

            <div class="ai-badge">
                ✦ AI POWERED
                <span>For Smarter Classrooms</span>
            </div>

            <div class="hero-title">
                Smarter Attendance<br>
                for a <span>Brighter Tomorrow</span>
            </div>

            <div class="hero-description">
                Face and voice powered attendance system designed for modern classrooms.<br>
                Fast, simple and reliable attendance management in one place.
            </div>

            <div class="feature-grid">

                <div class="feature-item">
                    <div class="feature-icon">📷</div>
                    <div class="feature-title">Face Attendance</div>
                    <div class="feature-text">AI-based recognition</div>
                </div>

                <div class="feature-item">
                    <div class="feature-icon">🎙️</div>
                    <div class="feature-title">Voice Attendance</div>
                    <div class="feature-text">Voice-powered</div>
                </div>

                <div class="feature-item">
                    <div class="feature-icon">👥</div>
                    <div class="feature-title">Manage Students</div>
                    <div class="feature-text">Organize classroom</div>
                </div>

                <div class="feature-item">
                    <div class="feature-icon">📊</div>
                    <div class="feature-title">Attendance Reports</div>
                    <div class="feature-text">Track records</div>
                </div>

            </div>

        </div>
        """)

    with right_col:

        with st.container(key="portal_card"):

            st.html("""
            <div class="portal-title">
                Welcome to<br>
                <span>SmartAttend</span>
            </div>

            <div class="portal-subtitle">
                Choose your portal to continue
            </div>
            """)

            teacher_clicked = st.button(
                "🎓  Teacher / Admin  →",
                key="home_teacher_portal",
                type="primary",
                use_container_width=True
            )

            student_clicked = st.button(
                "👤  Student  →",
                key="home_student_portal",
                type="secondary",
                use_container_width=True
            )

            st.html("""
            <div class="portal-info">
                <div class="portal-info-icon">💡</div>

                <div>
                    <strong>Smart Classrooms. Smarter Futures.</strong>
                    <small>AI × Technology × Better Learning</small>
                </div>
            </div>
            """)

            if teacher_clicked:
                st.session_state["login_type"] = "teacher"
                st.session_state.pop("teacher_quick_action", None)
                st.rerun()

            if student_clicked:
                st.session_state["login_type"] = "student"
                st.rerun()

    st.html("""
    <div class="smart-footer">
        AI-powered attendance system using face and voice recognition
    </div>
    """)