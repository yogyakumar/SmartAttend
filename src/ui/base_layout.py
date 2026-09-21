import streamlit as st


def style_base_layout():
    st.html("""
    <style>
        #MainMenu,
        header,
        footer {
            visibility: hidden;
        }

        html,
        body,
        [class*="css"] {
            font-family: "Segoe UI", Arial, sans-serif !important;
        }

        .block-container {
            max-width: 1400px !important;
            padding-top: 0.4rem !important;
            padding-bottom: 0 !important;
        }

        .stApp {
            min-height: 100vh;
            background:
                radial-gradient(
                    circle at 82% 12%,
                    rgba(184, 215, 255, 0.52),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 8% 82%,
                    rgba(217, 234, 255, 0.48),
                    transparent 30%
                ),
                linear-gradient(
                    135deg,
                    #fbfdff 0%,
                    #eef6ff 52%,
                    #f8fbff 100%
                );
        }

        .smart-navbar {
            height: 78px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 25px;
        }

        .smart-logo {
            color: #091a3b;
            font-size: 30px;
            font-weight: 800;
            letter-spacing: -1.4px;
        }

        .smart-logo span {
            color: #246cf0;
        }

        .smart-nav-links {
            display: flex;
            align-items: center;
            gap: 7px;
        }

        .smart-nav-item {
            padding: 10px 19px;
            border-radius: 24px;
            color: #506483;
            font-size: 14px;
            font-weight: 650;
        }

        .smart-nav-item.active {
            background: #e1ecff;
            color: #246cf0;
        }

        .smart-home {
            position: relative;
        }

        .classroom-glow {
            position: absolute;
            left: -120px;
            bottom: 20px;
            width: 680px;
            height: 250px;
            border-radius: 50%;
            background:
                radial-gradient(
                    ellipse,
                    rgba(188, 220, 255, 0.38),
                    transparent 68%
                );
            filter: blur(8px);
            pointer-events: none;
            z-index: 0;
        }

        .classroom-floor {
            position: absolute;
            left: -30px;
            bottom: 0;
            width: 760px;
            height: 105px;
            border-radius: 50% 50% 0 0;
            background:
                linear-gradient(
                    180deg,
                    rgba(221, 234, 248, 0.55),
                    rgba(240, 247, 253, 0.08)
                );
            transform: perspective(350px) rotateX(8deg);
            pointer-events: none;
        }

        .hero-content {
            position: relative;
            z-index: 5;
            padding-top: 38px;
        }

        .ai-badge {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 9px 17px;
            border-radius: 24px;
            background: rgba(239, 246, 255, 0.92);
            border: 1px solid #a9caff;
            color: #2168ed;
            font-size: 12px;
            font-weight: 800;
        }

        .ai-badge span {
            color: #647797;
            font-weight: 500;
        }

        .hero-title {
            margin-top: 27px;
            color: #081a3c;
            font-size: clamp(42px, 4.2vw, 61px);
            line-height: 1.04;
            letter-spacing: -2.8px;
            font-weight: 800;
        }

        .hero-title span {
            color: #2168ed;
        }

        .hero-description {
            max-width: 600px;
            margin-top: 23px;
            color: #566d91;
            font-size: 17px;
            line-height: 1.55;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            max-width: 660px;
            margin-top: 31px;
        }

        .feature-item {
            text-align: center;
            padding: 9px 5px;
            background: transparent;
        }

        .feature-icon {
            width: 48px;
            height: 48px;
            margin: 0 auto 10px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 23px;
        }

        .feature-face .feature-icon {
            background: #e4edff;
        }

        .feature-voice .feature-icon {
            background: #e4f5ff;
        }

        .feature-student .feature-icon {
            background: #eee7ff;
        }

        .feature-report .feature-icon {
            background: #ffedf1;
        }

        .feature-title {
            color: #142543;
            font-size: 13px;
            line-height: 1.25;
            font-weight: 800;
        }

        .feature-description {
            margin-top: 5px;
            color: #7788a5;
            font-size: 10.5px;
            line-height: 1.3;
        }

        .robot-area {
            position: relative;
            height: 345px;
            margin-top: -4px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .robot-orbit {
            position: absolute;
            width: 270px;
            height: 265px;
            border: 2px dashed rgba(52, 113, 226, 0.35);
            border-left-color: transparent;
            border-bottom-color: transparent;
            border-radius: 50%;
            transform: rotate(-25deg);
        }

        .robot-svg {
            position: relative;
            z-index: 3;
            width: 245px;
            height: 300px;
        }

        .robot-doodle {
            position: absolute;
            color: #637594;
            font-size: 11px;
            line-height: 1.35;
            font-family: "Comic Sans MS", cursive;
            opacity: 0.72;
            z-index: 4;
        }

        .robot-doodle.left {
            left: 5%;
            top: 22%;
            transform: rotate(-5deg);
        }

        .robot-doodle.right {
            right: 2%;
            top: 14%;
            transform: rotate(4deg);
        }

        .robot-book {
            position: absolute;
            left: 5%;
            bottom: 20px;
            width: 120px;
            height: 55px;
            border-radius: 50%;
            background:
                linear-gradient(
                    145deg,
                    rgba(224, 235, 245, 0.85),
                    rgba(246, 250, 253, 0.45)
                );
            transform: rotate(-9deg);
            opacity: 0.85;
        }

        .highlights {
            display: flex;
            gap: 45px;
            margin-top: 4px;
            padding: 18px 5px 0;
            border-top: 1px solid rgba(174, 198, 228, 0.55);
        }

        .highlight {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .highlight-icon {
            width: 34px;
            height: 34px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            background: #e5efff;
            font-size: 16px;
        }

        .highlight-title {
            color: #152542;
            font-size: 12px;
            font-weight: 800;
        }

        .highlight-text {
            color: #7a8ba7;
            font-size: 10px;
            margin-top: 2px;
        }

        .st-key-portal_card {
            position: relative;
            z-index: 20;
            margin-top: 38px;
            padding: 39px 35px 32px !important;
            min-height: 520px;
            box-sizing: border-box;
            border-radius: 27px;
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid #cbdcf5;
            box-shadow:
                0 24px 60px rgba(43, 91, 151, 0.15);
            backdrop-filter: blur(12px);
        }

        .portal-title {
            color: #07183b;
            font-size: 31px;
            line-height: 1.12;
            font-weight: 800;
            letter-spacing: -1px;
        }

        .portal-subtitle {
            color: #6c81a2;
            font-size: 15px;
            margin-top: 10px;
            margin-bottom: 27px;
        }

        .st-key-home_teacher_portal button,
        .st-key-home_student_portal button {
            width: 100% !important;
            min-height: 67px !important;
            border-radius: 17px !important;
            font-size: 16px !important;
            font-weight: 750 !important;
            text-align: left !important;
            padding: 0 21px !important;
            transition: 0.18s ease !important;
        }

        .st-key-home_teacher_portal button {
            background: linear-gradient(
                135deg,
                #2879ff,
                #1764eb
            ) !important;
            color: white !important;
            border: 1px solid #2472f7 !important;
            box-shadow:
                0 11px 24px rgba(31, 105, 239, 0.22) !important;
        }

        .st-key-home_student_portal button {
            background: #eef4ff !important;
            color: #526b94 !important;
            border: 1px solid #d1e0f7 !important;
        }

        .st-key-home_teacher_portal button:hover,
        .st-key-home_student_portal button:hover {
            transform: translateY(-2px);
        }

        .portal-info {
            display: flex;
            align-items: center;
            gap: 13px;
            margin-top: 28px;
            padding: 15px 16px;
            border-radius: 17px;
            background: #edf5ff;
        }

        .portal-info-icon {
            width: 40px;
            height: 40px;
            min-width: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background: #dceaff;
            font-size: 20px;
        }

        .portal-info-title {
            color: #10203f;
            font-size: 13px;
            font-weight: 800;
        }

        .portal-info-text {
            margin-top: 3px;
            color: #7486a4;
            font-size: 11px;
        }

        .smart-footer {
            position: relative;
            z-index: 5;
            margin-top: 26px;
            padding: 19px 10px 23px;
            text-align: center;
            border-top: 1px solid rgba(177, 202, 234, 0.6);
        }

        .footer-brand {
            color: #536b92;
            font-size: 16px;
            font-weight: 800;
        }

        .footer-text {
            margin-top: 4px;
            color: #7a8ca8;
            font-size: 12px;
        }

        @media (max-width: 1050px) {
            .hero-title {
                font-size: 46px;
            }

            .feature-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .robot-area {
                height: 290px;
            }

            .robot-svg {
                width: 205px;
            }
        }

        @media (max-width: 700px) {
            .smart-navbar {
                padding: 0 8px;
            }

            .smart-logo {
                font-size: 25px;
            }

            .smart-nav-links {
                gap: 0;
            }

            .smart-nav-item {
                padding: 8px 7px;
                font-size: 11px;
            }

            .hero-content {
                padding-top: 20px;
            }

            .hero-title {
                font-size: 38px;
                letter-spacing: -1.7px;
            }

            .hero-description {
                font-size: 15px;
            }

            .feature-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .robot-area {
                height: 250px;
            }

            .robot-svg {
                width: 175px;
            }

            .robot-doodle,
            .robot-book {
                display: none;
            }

            .highlights {
                gap: 18px;
                flex-wrap: wrap;
            }

            .st-key-portal_card {
                margin-top: 20px;
                padding: 30px 22px 27px !important;
            }
        }
    </style>
    """)


def style_background_dashboard():
    st.html("""
    <style>
        .stApp {
            background:
                radial-gradient(
                    circle at 85% 15%,
                    rgba(205, 228, 255, 0.35),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 10% 80%,
                    rgba(225, 239, 255, 0.40),
                    transparent 30%
                ),
                linear-gradient(
                    135deg,
                    #f8fbff 0%,
                    #eef5ff 50%,
                    #f9fcff 100%
                );
        }

        .block-container {
            max-width: 1400px !important;
            padding-top: 1rem !important;
        }
    </style>
    """)