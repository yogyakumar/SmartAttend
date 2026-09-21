import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import check_teacher_exists, create_teacher, teacher_login, get_teacher_subjects, get_attendance_for_teacher
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog

from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
import numpy as np

from datetime import datetime

import pandas as pd

from src.database.config import supabase


from src.components.dialog_voice_attendance import voice_attendance_dialog

def teacher_screen():
    style_background_dashboard()
    style_base_layout()
    teacher_ui_style()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()




def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    teacher_id = teacher_data['teacher_id']

    st.html("""
    <div class="dashboard-topbar">
        <div class="dashboard-logo">Smart<span>Attend</span></div>
        <div class="dashboard-portal">🎓 Teacher / Admin Portal</div>
    </div>
    """)

    subjects = get_teacher_subjects(teacher_id)
    records = get_attendance_for_teacher(teacher_id)
    subject_count = len(subjects) if subjects else 0
    session_count = len({r.get('timestamp', '').split('.')[0] for r in records if r.get('timestamp')}) if records else 0

    with st.container(key="teacher_dashboard_hero"):
        c1, c2 = st.columns([5, 1], vertical_alignment='center')
        with c1:
            st.html(f"""
            <div class="dashboard-kicker">SMARTATTEND • CLASSROOM CONTROL</div>
            <div class="dashboard-title">Welcome, <span>{teacher_data['name']}</span> 👋</div>
            <div class="dashboard-subtitle">Manage your classes, run AI attendance and review attendance records from one place.</div>
            """)
        with c2:
            if st.button("Logout", key="teacher_dashboard_logout", type="secondary", use_container_width=True):
                st.session_state['is_logged_in'] = False
                st.session_state.pop('teacher_data', None)
                st.session_state.pop('current_teacher_tab', None)
                st.rerun()

    st.html(f"""
    <div class="dashboard-stats">
        <div class="dashboard-stat">
            <div class="stat-icon">📚</div>
            <div><div class="stat-value">{subject_count}</div><div class="stat-label">Active Subjects</div></div>
        </div>
        <div class="dashboard-stat">
            <div class="stat-icon">📊</div>
            <div><div class="stat-value">{session_count}</div><div class="stat-label">Attendance Sessions</div></div>
        </div>
        <div class="dashboard-stat dashboard-stat-ai">
            <div class="stat-icon">🤖</div>
            <div><div class="stat-value">AI</div><div class="stat-label">Face + Voice Enabled</div></div>
        </div>
    </div>
    """)

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'

    st.html('<div class="dashboard-section-label">Classroom Tools</div>')

    tab1, tab2, tab3 = st.columns(3, gap='medium')

    with tab1:
        active = st.session_state.current_teacher_tab == 'take_attendance'
        if st.button('📷  Take Attendance', type='primary' if active else 'secondary', width='stretch', key='teacher_tab_attendance'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        active = st.session_state.current_teacher_tab == 'manage_subjects'
        if st.button('📚  Manage Subjects', type='primary' if active else 'secondary', width='stretch', key='teacher_tab_subjects'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:
        active = st.session_state.current_teacher_tab == 'attendance_records'
        if st.button('📊  Attendance Records', type='primary' if active else 'secondary', width='stretch', key='teacher_tab_records'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()

    st.html('<div class="dashboard-divider"></div>')

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    elif st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    elif st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()

    st.html("""
    <div class="dashboard-footer">
        AI-powered attendance system using face and voice recognition
    </div>

    <div style="text-align:center;margin-top:4px;padding:10px 0 8px;color:#18365c;font-size:13px;font-weight:750;">
        Created with ❤️ by <strong style="color:#3977eb;">SmartAttend</strong>
    </div>
    """)


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header('Take AI Attendance')


    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning('You havent created any subjects yet! Please create one to begin!')
        return
    
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1], vertical_alignment='bottom')

    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))

    with col2:
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4 ]:
                st.image(img, width='stretch', caption=f'Photo {idx+1}')
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear all photos', width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()


    with c2:
        
        if st.button('Run Face Analysis', width='stretch', type='secondary', icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)


                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")

                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id',selected_subject_id ).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students enrolled in this course')
                else:

                    results, attendance_to_log  = [], []

                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present= len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Use Voice Attendance', type='primary', width='stretch', icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)












def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data["teacher_id"]

    st.html('''
    <style>
        .manage-subjects-title {
            color: #18365c !important;
            font-size: 30px !important;
            font-weight: 850 !important;
            letter-spacing: -1px;
            margin: 0 0 16px;
        }

        .manage-subject-card {
            padding: 24px;
            margin-bottom: 8px;
            border-radius: 22px;
            background: rgba(255,255,255,.90);
            border: 1px solid #c7dcef;
            box-shadow: 0 14px 34px rgba(57,96,143,.09);
        }

        .manage-subject-name {
            color: #18365c !important;
            font-size: 24px;
            font-weight: 850;
            margin-bottom: 13px;
        }

        .manage-subject-meta {
            color: #426587 !important;
            font-size: 14px;
            margin-bottom: 18px;
        }

        .manage-subject-code {
            display: inline-block;
            padding: 5px 10px;
            margin: 0 4px;
            border-radius: 8px;
            background: #e8f0ff;
            color: #426de3 !important;
            font-weight: 800;
        }

        .manage-stats {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .manage-stat {
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 145px;
            padding: 10px 13px;
            border-radius: 13px;
            background: #f4f8fd;
            border: 1px solid #dce7f3;
        }

        .manage-stat-icon {
            width: 35px;
            height: 35px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            background: #e8f1ff;
            font-size: 17px;
        }

        .manage-stat-value {
            color: #18365c !important;
            font-size: 17px;
            line-height: 1;
            font-weight: 850;
        }

        .manage-stat-label {
            color: #7187a2 !important;
            font-size: 10px;
            margin-top: 4px;
            font-weight: 650;
        }

        [class*="st-key-teacher_share_"] button {
            min-height: 40px !important;
            margin-top: 9px !important;
            padding: 5px 15px !important;
            border-radius: 11px !important;
            background: #ffffff !important;
            border: 1px solid #b9d1eb !important;
            color: #315f91 !important;
            font-size: 12px !important;
            font-weight: 750 !important;
            box-shadow: 0 6px 16px rgba(52,96,151,.07) !important;
        }

        [class*="st-key-teacher_share_"] button:hover {
            background: #edf5ff !important;
            border-color: #75a7df !important;
            color: #245b96 !important;
        }

        .manage-empty {
            padding: 28px;
            border-radius: 20px;
            background: rgba(255,255,255,.88);
            border: 1px solid #d5e2f0;
            color: #607b9a !important;
            text-align: center;
        }

        @media (max-width: 700px) {
            .manage-subjects-title {
                font-size: 26px !important;
            }

            .manage-subject-card {
                padding: 20px;
            }

            .manage-stat {
                width: 100%;
            }
        }
    </style>
    ''')

    c1, c2 = st.columns([1.4, 1], vertical_alignment="center")

    with c1:
        st.html('''
        <div class="manage-subjects-title">
            Manage Subjects
        </div>
        ''')

    with c2:
        if st.button(
            "Create New Subject",
            width="stretch",
            key="teacher_create_subject",
            icon=":material/add:"
        ):
            create_subject_dialog(teacher_id)

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.html('''
        <div class="manage-empty">
            No subjects created yet. Create your first subject to get started.
        </div>
        ''')
        return

    cols = st.columns(2, gap="large")

    for i, sub in enumerate(subjects):
        total_students = sub.get("total_students", 0)
        total_classes = sub.get("total_classes", 0)

        with cols[i % 2]:
            st.html(f'''
            <div class="manage-subject-card">
                <div class="manage-subject-name">
                    {sub["name"]}
                </div>

                <div class="manage-subject-meta">
                    Code:
                    <span class="manage-subject-code">{sub["subject_code"]}</span>
                    <span>•</span>
                    Section: <strong>{sub["section"]}</strong>
                </div>

                <div class="manage-stats">
                    <div class="manage-stat">
                        <div class="manage-stat-icon">👥</div>
                        <div>
                            <div class="manage-stat-value">{total_students}</div>
                            <div class="manage-stat-label">Students enrolled</div>
                        </div>
                    </div>

                    <div class="manage-stat">
                        <div class="manage-stat-icon">📚</div>
                        <div>
                            <div class="manage-stat-value">{total_classes}</div>
                            <div class="manage-stat-label">Classes conducted</div>
                        </div>
                    </div>
                </div>
            </div>
            ''')

            with st.container(key=f"teacher_share_{i}"):
                if st.button(
                    f"Share Code: {sub['subject_code']}",
                    key=f"teacher_share_button_{i}",
                    icon=":material/share:",
                    width="content"
                ):
                    share_subject_dialog(
                        sub["name"],
                        sub["subject_code"]
                    )

def teacher_tab_attendance_records():
    st.header('Attendance Records')

    teacher_id = st.session_state.teacher_data['teacher_id']

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        return
    
    data = []

    for r in records:
        ts = r.get('timestamp')

        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N'A",
            "Subject": r['subjects']['name'],
            "Subject Code":r['subjects']['subject_code'],
            "is_present": bool(r.get('is_present', False))
        })


    df = pd.DataFrame(data)



    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
        .agg(
            Present_Count = ('is_present', 'sum'),
            Total_Count =('is_present', 'count')
        ).reset_index()

    )

    summary['Attendance Stats'] = (
        "✅ " + summary['Present_Count'].astype(str) + " /"
        + summary['Total_Count'].astype(str) + ' Students'
    )

    display_df = ( summary.sort_values(by='ts_group' ,ascending=False)
                  [['Time', 'Subject', 'Subject Code', 'Attendance Stats']]
                  )
    
    st.dataframe(display_df, width='stretch', hide_index=True)


def login_teacher(username, password):
    if not username or not password:
        return False
    
    teacher = teacher_login(username, password)

    if teacher:
        st.session_state.user_role ='teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    

    return False
def teacher_screen_login():

    st.html("""
    <div class="teacher-background">
        <svg class="teacher-line-art" viewBox="0 0 1440 900" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 640 C190 380 330 300 560 270 C790 240 900 80 1190 130 C1360 160 1430 270 1440 360" fill="none" stroke="#8db9f5" stroke-width="2" stroke-dasharray="9 9" opacity=".42"/>
            <path d="M0 760 C180 700 300 760 430 850" fill="none" stroke="#8db9f5" stroke-width="2" stroke-dasharray="9 9" opacity=".35"/>
            <g transform="translate(930 110)" opacity=".5">
                <path d="M0 42 L32 0 L64 42" fill="none" stroke="#79a9ee" stroke-width="3"/>
                <path d="M8 42 L56 42" fill="none" stroke="#79a9ee" stroke-width="3"/>
                <path d="M16 42 L48 18" fill="none" stroke="#79a9ee" stroke-width="2"/>
            </g>
            <g transform="translate(120 170)" opacity=".38">
                <rect x="0" y="0" width="62" height="82" rx="7" fill="none" stroke="#78aaf0" stroke-width="3"/>
                <line x1="15" y1="22" x2="48" y2="22" stroke="#78aaf0" stroke-width="3"/>
                <line x1="15" y1="39" x2="48" y2="39" stroke="#78aaf0" stroke-width="3"/>
                <line x1="15" y1="56" x2="40" y2="56" stroke="#78aaf0" stroke-width="3"/>
            </g>
            <g transform="translate(1080 455)" opacity=".45">
                <line x1="0" y1="95" x2="0" y2="10" stroke="#78aaf0" stroke-width="4"/>
                <line x1="28" y1="95" x2="28" y2="42" stroke="#78aaf0" stroke-width="4"/>
                <line x1="56" y1="95" x2="56" y2="0" stroke="#78aaf0" stroke-width="4"/>
                <line x1="-8" y1="95" x2="70" y2="95" stroke="#78aaf0" stroke-width="4"/>
            </g>
            <g transform="translate(1110 690)" opacity=".42">
                <rect x="0" y="0" width="190" height="105" rx="12" fill="none" stroke="#78aaf0" stroke-width="3"/>
                <path d="M-15 108 L205 108" stroke="#78aaf0" stroke-width="4" stroke-linecap="round"/>
                <path d="M35 25 L155 25" stroke="#9fc4f4" stroke-width="2"/>
                <path d="M35 45 L145 45" stroke="#9fc4f4" stroke-width="2"/>
                <path d="M35 65 L125 65" stroke="#9fc4f4" stroke-width="2"/>
            </g>
            <g transform="translate(130 680) rotate(-12)" opacity=".42">
                <path d="M0 35 L92 0 L65 70 Z" fill="none" stroke="#78aaf0" stroke-width="3"/>
                <path d="M35 28 L65 70" stroke="#78aaf0" stroke-width="3"/>
                <path d="M35 28 L92 0" stroke="#78aaf0" stroke-width="3"/>
            </g>
            <g transform="translate(720 115)" opacity=".42">
                <path d="M0 38 L35 0 L70 38" fill="none" stroke="#78aaf0" stroke-width="3"/>
                <path d="M9 38 L61 38" stroke="#78aaf0" stroke-width="3"/>
                <path d="M20 38 L50 15" stroke="#78aaf0" stroke-width="2"/>
            </g>
            <g fill="none" stroke="#78aaf0" stroke-width="3" opacity=".42">
                <path d="M850 560 q18 -18 36 0 q-18 18 -36 0"/>
                <path d="M1280 380 l12 12 l-12 12 l-12 -12 z"/>
            </g>
            <g fill="#78aaf0" opacity=".42">
                <path d="M610 115 l5 12 l12 5 l-12 5 l-5 12 l-5 -12 l-12 -5 l12 -5 z"/>
                <path d="M1240 520 l4 9 l9 4 l-9 4 l-4 9 l-4 -9 l-9 -4 l9 -4 z"/>
                <path d="M270 520 l4 9 l9 4 l-9 4 l-4 9 l-4 -9 l-9 -4 l9 -4 z"/>
            </g>
        </svg>
        <div class="teacher-note note-top">Teach<br>Track<br>Transform</div>
        <div class="teacher-note note-left">Better Teachers<br>Brighter Futures ♡</div>
        <div class="teacher-note note-bottom">A Smarter<br>Classroom<br>Today</div>
    </div>
    """)

    st.html("""
    <div class="teacher-topbar">
        <div class="teacher-logo">Smart<span>Attend</span></div>
        <div class="teacher-badge">🎓 Teacher / Admin Portal</div>
    </div>
    """)

    back_clicked = st.button("←  Back to Home", key="teacher_back_btn", type="secondary")
    if back_clicked:
        st.session_state["login_type"] = None
        st.session_state.pop("teacher_login_type", None)
        st.rerun()

    with st.container(key="teacher_login_card"):
        st.html("""
        <div class="teacher-icon">🎓</div>
        <div class="teacher-login-title">Welcome back,<br><span>Teacher</span></div>
        <div class="teacher-login-subtitle">Sign in to manage attendance, subjects and students.</div>
        """)

        teacher_username = st.text_input("Username", placeholder="Enter your username", key="teacher_username_login")
        teacher_pass = st.text_input("Password", type="password", placeholder="Enter your password", key="teacher_password_login")

        login_clicked = st.button("🎓  Login to Teacher Portal  →", key="teacher_login_btn", type="primary", use_container_width=True)
        register_clicked = st.button("Create Teacher Account", key="teacher_register_btn", type="secondary", use_container_width=True)

        if login_clicked:
            if login_teacher(teacher_username, teacher_pass):
                st.toast("Welcome back! 👋")
                import time
                time.sleep(0.7)
                st.rerun()
            else:
                st.error("Invalid username and password.")

        if register_clicked:
            st.session_state.teacher_login_type = "register"
            st.rerun()

        st.html("""
        <div class="teacher-bottom-info">SmartAttend · AI-powered attendance management</div>
        """)

    st.html("""
    <div class="teacher-footer">AI-powered attendance system using face and voice recognition</div>
    """)


def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All Fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username already taken"
    if teacher_pass != teacher_pass_confirm:
        return False, "Password doesn't match"
    
    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Sucessfully Created! Login Now"
    except Exception as e:
        return False, "Unexpected Error!"
    

def teacher_screen_register():

    st.html("""
    <div class="teacher-background">
        <svg class="teacher-line-art" viewBox="0 0 1440 900" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 640 C190 380 330 300 560 270 C790 240 900 80 1190 130 C1360 160 1430 270 1440 360" fill="none" stroke="#8db9f5" stroke-width="2" stroke-dasharray="9 9" opacity=".42"/>
            <path d="M0 760 C180 700 300 760 430 850" fill="none" stroke="#8db9f5" stroke-width="2" stroke-dasharray="9 9" opacity=".35"/>
            <g transform="translate(120 170)" opacity=".38">
                <rect x="0" y="0" width="62" height="82" rx="7" fill="none" stroke="#78aaf0" stroke-width="3"/>
                <line x1="15" y1="22" x2="48" y2="22" stroke="#78aaf0" stroke-width="3"/>
                <line x1="15" y1="39" x2="48" y2="39" stroke="#78aaf0" stroke-width="3"/>
                <line x1="15" y1="56" x2="40" y2="56" stroke="#78aaf0" stroke-width="3"/>
            </g>
            <g transform="translate(1080 455)" opacity=".45">
                <line x1="0" y1="95" x2="0" y2="10" stroke="#78aaf0" stroke-width="4"/>
                <line x1="28" y1="95" x2="28" y2="42" stroke="#78aaf0" stroke-width="4"/>
                <line x1="56" y1="95" x2="56" y2="0" stroke="#78aaf0" stroke-width="4"/>
                <line x1="-8" y1="95" x2="70" y2="95" stroke="#78aaf0" stroke-width="4"/>
            </g>
            <g transform="translate(1110 690)" opacity=".42">
                <rect x="0" y="0" width="190" height="105" rx="12" fill="none" stroke="#78aaf0" stroke-width="3"/>
                <path d="M-15 108 L205 108" stroke="#78aaf0" stroke-width="4" stroke-linecap="round"/>
                <path d="M35 25 L155 25" stroke="#9fc4f4" stroke-width="2"/>
                <path d="M35 45 L145 45" stroke="#9fc4f4" stroke-width="2"/>
                <path d="M35 65 L125 65" stroke="#9fc4f4" stroke-width="2"/>
            </g>
            <g transform="translate(130 680) rotate(-12)" opacity=".42">
                <path d="M0 35 L92 0 L65 70 Z" fill="none" stroke="#78aaf0" stroke-width="3"/>
                <path d="M35 28 L65 70" stroke="#78aaf0" stroke-width="3"/>
                <path d="M35 28 L92 0" stroke="#78aaf0" stroke-width="3"/>
            </g>
            <g fill="#78aaf0" opacity=".42">
                <path d="M610 115 l5 12 l12 5 l-12 5 l-5 12 l-5 -12 l-12 -5 l12 -5 z"/>
                <path d="M1240 520 l4 9 l9 4 l-9 4 l-4 9 l-4 -9 l-9 -4 l9 -4 z"/>
                <path d="M270 520 l4 9 l9 4 l-9 4 l-4 9 l-4 -9 l-9 -4 l9 -4 z"/>
            </g>
        </svg>
        <div class="teacher-note note-top">Learn<br>Lead<br>Inspire</div>
        <div class="teacher-note note-left">Better Teachers<br>Brighter Futures ♡</div>
        <div class="teacher-note note-bottom">Build a<br>Smarter<br>Classroom</div>
    </div>
    """)

    st.html("""
    <div class="teacher-topbar">
        <div class="teacher-logo">Smart<span>Attend</span></div>
        <div class="teacher-badge">🎓 Teacher / Admin Portal</div>
    </div>
    """)

    back_clicked = st.button("←  Back to Home", key="teacher_back_btn", type="secondary")
    if back_clicked:
        st.session_state["login_type"] = None
        st.session_state.pop("teacher_login_type", None)
        st.rerun()

    with st.container(key="teacher_login_card"):
        st.html("""
        <div class="teacher-icon teacher-education-icon">
            <svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 29 L40 16 L70 29 L40 42 Z" fill="#2d73e8"/>
                <path d="M19 34 V52 Q40 65 61 52 V34" fill="#dceaff" stroke="#5d95e8" stroke-width="3"/>
                <path d="M40 42 V61" stroke="#2d73e8" stroke-width="3"/>
                <path d="M67 31 V50" stroke="#2d73e8" stroke-width="3" stroke-linecap="round"/>
                <circle cx="67" cy="53" r="4" fill="#2d73e8"/>
            </svg>
        </div>
        <div class="teacher-login-title">Create your<br><span>Teacher Account</span></div>
        <div class="teacher-login-subtitle">Set up your SmartAttend teacher profile.</div>
        """)

        with st.form("teacher_register_form", clear_on_submit=False):
            teacher_username = st.text_input("Username", placeholder="Choose a username", key="teacher_username_register")
            teacher_name = st.text_input("Full Name", placeholder="Enter your name", key="teacher_name_register")
            teacher_pass = st.text_input("Password", type="password", placeholder="Create a password", key="teacher_password_register")
            teacher_pass_confirm = st.text_input("Confirm Password", type="password", placeholder="Enter password again", key="teacher_password_confirm_register")
            register_clicked = st.form_submit_button("📚  Create Teacher Account  →", key="teacher_register_btn", type="primary", use_container_width=True)

        login_clicked = st.button("Already have an account? Login", key="teacher_login_btn", type="secondary", use_container_width=True)

        if register_clicked:
            success, message = register_teacher(
                teacher_username.strip(),
                teacher_name.strip(),
                teacher_pass,
                teacher_pass_confirm
            )
            if success:
                st.success(message)
                import time
                time.sleep(1.2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)

        if login_clicked:
            st.session_state.teacher_login_type = "login"
            st.rerun()

        st.html("""
        <div class="teacher-bottom-info">Your account will be used to manage your SmartAttend classroom.</div>
        """)

    st.html("""
    <div class="teacher-footer">AI-powered attendance system using face and voice recognition</div>
    """)


def teacher_ui_style():
    st.html("""
    <style>
        .stApp {
            background:
                radial-gradient(circle at 12% 18%, rgba(222,239,255,.72), transparent 28%),
                radial-gradient(circle at 82% 20%, rgba(198,224,255,.62), transparent 30%),
                radial-gradient(circle at 52% 78%, rgba(224,239,255,.66), transparent 34%),
                linear-gradient(135deg, #fbfdff 0%, #eef6ff 48%, #f8fbff 100%) !important;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .main .block-container {
            position: relative;
            z-index: 2;
            max-width: 1280px !important;
            padding-top: .35rem !important;
            padding-bottom: .75rem !important;
        }

        .teacher-background {
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            pointer-events: none;
            z-index: 0;
        }

        .teacher-background::before {
            content: "";
            position: absolute;
            width: 620px;
            height: 620px;
            left: 50%;
            top: 48%;
            transform: translate(-50%, -50%);
            border-radius: 50%;
            background: radial-gradient(circle, rgba(194,222,255,.35), rgba(194,222,255,.08) 48%, transparent 72%);
        }

        .teacher-line-art {
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
        }

        .teacher-note {
            position: absolute;
            color: rgba(74,121,187,.55);
            font-size: 16px;
            line-height: 1.28;
            font-style: italic;
            font-weight: 500;
        }

        .note-top { right: 8%; top: 14%; transform: rotate(3deg); }
        .note-left { left: 7%; bottom: 22%; transform: rotate(-5deg); }
        .note-bottom { right: 8%; bottom: 16%; transform: rotate(2deg); }

        .teacher-topbar {
            position: relative;
            z-index: 20;
            height: 58px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 8px;
        }

        .teacher-logo {
            font-size: 27px;
            line-height: 1;
            font-weight: 850;
            letter-spacing: -1.3px;
            color: #172b4d;
        }

        .teacher-logo span { color: #2d73e8; }

        .teacher-badge {
            display: inline-flex;
            align-items: center;
            padding: 7px 13px;
            border-radius: 20px;
            background: rgba(255,255,255,.58);
            border: 1px solid rgba(184,211,242,.8);
            color: #52729a;
            font-size: 11px;
            font-weight: 650;
        }

        .st-key-teacher_back_btn {
            position: fixed !important;
            z-index: 100 !important;
            top: 76px !important;
            left: 28px !important;
            margin: 0 !important;
        }

        .st-key-teacher_back_btn button {
            min-height: 40px !important;
            padding: 5px 17px !important;
            border-radius: 22px !important;
            background: rgba(255,255,255,.94) !important;
            border: 1px solid #a9c9ef !important;
            color: #2f659d !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            box-shadow: 0 8px 24px rgba(52,96,151,.12) !important;
            transition: all .2s ease !important;
        }

        .st-key-teacher_back_btn button:hover {
            background: #edf5ff !important;
            border-color: #6fa4ed !important;
            color: #2464ad !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 10px 27px rgba(52,96,151,.18) !important;
        }

        .st-key-teacher_login_card input::placeholder,
        .st-key-teacher_login_card input::-webkit-input-placeholder,
        .st-key-teacher_login_card input::-moz-placeholder {
            color: #8a9db5 !important;
            opacity: 1 !important;
            -webkit-text-fill-color: #8a9db5 !important;
        }

        .st-key-teacher_login_card input {
            color: #263f61 !important;
            -webkit-text-fill-color: #263f61 !important;
        }

        .st-key-teacher_login_card {
            position: relative;
            z-index: 30;
            width: 100%;
            max-width: 470px;
            margin: 2vh auto 0 !important;
            padding: 29px 34px 24px !important;
            border-radius: 27px !important;
            background: rgba(255,255,255,.84) !important;
            border: 1px solid rgba(185,212,244,.75) !important;
            box-shadow: 0 25px 70px rgba(52,91,140,.14) !important;
            backdrop-filter: blur(18px);
        }

        .teacher-icon {
            width: 52px;
            height: 52px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #e4efff;
            font-size: 24px;
            margin-bottom: 15px;
        }

        .teacher-education-icon svg {
            width: 40px;
            height: 40px;
        }

        .teacher-login-title {
            color: #14284b;
            font-size: 29px;
            font-weight: 850;
            letter-spacing: -1px;
            line-height: 1.05;
        }

        .teacher-login-title span { color: #2d73e8; }

        .teacher-login-subtitle {
            color: #7c8fa9;
            font-size: 13px;
            line-height: 1.45;
            margin-top: 9px;
            margin-bottom: 17px;
        }

        .st-key-teacher_login_card label {
            color: #526b8b !important;
            font-size: 12px !important;
            font-weight: 650 !important;
        }

        .st-key-teacher_login_card input {
            border-radius: 12px !important;
            border: 1px solid #cbdcf2 !important;
            background: rgba(248,251,255,.92) !important;
            color: #263f61 !important;
        }

        .st-key-teacher_login_card input:focus {
            border-color: #78aaf0 !important;
            box-shadow: 0 0 0 2px rgba(45,115,232,.10) !important;
        }

        .st-key-teacher_login_btn button,
        .st-key-teacher_register_btn button {
            min-height: 49px !important;
            border-radius: 13px !important;
            font-size: 13px !important;
            font-weight: 700 !important;
        }

        .st-key-teacher_login_btn button {
            background: #2d73e8 !important;
            border-color: #2d73e8 !important;
            color: white !important;
            box-shadow: 0 10px 25px rgba(45,115,232,.20) !important;
        }

        .st-key-teacher_register_btn button {
            background: #edf4ff !important;
            border: 1px solid #c9dcf6 !important;
            color: #416488 !important;
        }

        .teacher-bottom-info {
            text-align: center;
            color: #8a9bb1;
            font-size: 10px;
            line-height: 1.4;
            margin-top: 17px;
        }

        .teacher-footer {
            position: relative;
            z-index: 20;
            text-align: center;
            color: #8b9bb0;
            font-size: 10px;
            padding: 8px 0 4px;
        }


        .dashboard-topbar {
            position: relative;
            z-index: 20;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 2px 14px;
        }

        .dashboard-logo {
            font-size: 28px;
            line-height: 1;
            font-weight: 850;
            letter-spacing: -1.4px;
            color: #172b4d;
        }

        .dashboard-logo span { color: #2d73e8; }

        .dashboard-portal {
            padding: 8px 14px;
            border-radius: 20px;
            background: rgba(255,255,255,.76);
            border: 1px solid #c8dcf4;
            color: #52729a;
            font-size: 11px;
            font-weight: 700;
            box-shadow: 0 8px 22px rgba(52,96,151,.07);
        }

        .st-key-teacher_dashboard_hero {
            position: relative;
            z-index: 10;
            padding: 27px 30px !important;
            border: 1px solid rgba(187,213,241,.78) !important;
            border-radius: 25px !important;
            background: rgba(255,255,255,.72) !important;
            box-shadow: 0 18px 50px rgba(57,96,143,.10) !important;
            backdrop-filter: blur(15px);
        }

        .dashboard-kicker {
            color: #5b8bc7;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.6px;
            margin-bottom: 8px;
        }

        .dashboard-title {
            color: #14284b;
            font-size: 31px;
            line-height: 1.1;
            font-weight: 850;
            letter-spacing: -1.2px;
        }

        .dashboard-title span { color: #2d73e8; }

        .dashboard-subtitle {
            color: #7287a3;
            font-size: 13px;
            line-height: 1.55;
            margin-top: 9px;
            max-width: 650px;
        }

        .st-key-teacher_dashboard_logout button {
            min-height: 42px !important;
            border-radius: 12px !important;
            background: #f5f9ff !important;
            border: 1px solid #c8dcf4 !important;
            color: #3e648e !important;
            font-weight: 700 !important;
        }

        .dashboard-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin: 18px 0 23px;
        }

        .dashboard-stat {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 17px;
            border-radius: 18px;
            background: rgba(255,255,255,.64);
            border: 1px solid rgba(192,215,240,.72);
            box-shadow: 0 10px 30px rgba(57,96,143,.07);
        }

        .stat-icon {
            width: 39px;
            height: 39px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
            background: #eaf3ff;
            font-size: 19px;
        }

        .stat-value {
            color: #19365d;
            font-size: 19px;
            font-weight: 850;
            line-height: 1;
        }

        .stat-label {
            color: #8093ac;
            font-size: 10px;
            margin-top: 5px;
        }

        .dashboard-section-label {
            color: #31557f;
            font-size: 14px;
            font-weight: 800;
            margin: 2px 0 10px;
        }

        .stApp:has(.st-key-teacher_dashboard_hero) h1,
        .stApp:has(.st-key-teacher_dashboard_hero) h2,
        .stApp:has(.st-key-teacher_dashboard_hero) h3,
        .stApp:has(.st-key-teacher_dashboard_hero) label,
        .stApp:has(.st-key-teacher_dashboard_hero) p {
            color: #18365c !important;
        }

        .st-key-teacher_tab_attendance button,
        .st-key-teacher_tab_subjects button,
        .st-key-teacher_tab_records button,
        .st-key-teacher_create_subject button {
            min-height: 49px !important;
            border-radius: 14px !important;
            font-size: 12px !important;
            font-weight: 750 !important;
            border-color: #c8dcf4 !important;
        }

        .st-key-teacher_tab_attendance button[kind="secondary"],
        .st-key-teacher_tab_subjects button[kind="secondary"],
        .st-key-teacher_tab_records button[kind="secondary"],
        .st-key-teacher_create_subject button {
            background: rgba(255,255,255,.82) !important;
            color: #315b87 !important;
            border-color: #c8dcf4 !important;
            box-shadow: 0 7px 18px rgba(52,96,151,.08) !important;
        }

        .st-key-teacher_tab_attendance button[kind="primary"],
        .st-key-teacher_tab_subjects button[kind="primary"],
        .st-key-teacher_tab_records button[kind="primary"] {
            background: #2d73e8 !important;
            color: #fff !important;
            border-color: #2d73e8 !important;
            box-shadow: 0 10px 25px rgba(45,115,232,.17) !important;
        }

        .dashboard-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, #cbdff5, transparent);
            margin: 23px 0 25px;
        }

        .dashboard-footer {
            text-align: center;
            color: #8295ad;
            font-size: 10px;
            padding: 24px 0 8px;
        }

        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input {
            color: #294766 !important;
            -webkit-text-fill-color: #294766 !important;
            background: #f8fbff !important;
            border-color: #cbdcf2 !important;
        }

        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder,
        .stNumberInput input::placeholder {
            color: #8a9db5 !important;
            opacity: 1 !important;
            -webkit-text-fill-color: #8a9db5 !important;
        }

        .stTextInput input:-webkit-autofill,
        .stTextInput input:-webkit-autofill:hover,
        .stTextInput input:-webkit-autofill:focus,
        .stTextArea textarea:-webkit-autofill,
        .stNumberInput input:-webkit-autofill {
            -webkit-text-fill-color: #294766 !important;
            -webkit-box-shadow: 0 0 0 1000px #f8fbff inset !important;
            box-shadow: 0 0 0 1000px #f8fbff inset !important;
            caret-color: #294766 !important;
        }

        @media (max-height: 760px) and (min-width: 701px) {
            .teacher-topbar { height: 50px; }
            .st-key-teacher_login_card { margin-top: 0 !important; padding: 22px 30px 19px !important; }
            .teacher-icon { width: 45px; height: 45px; margin-bottom: 10px; }
            .teacher-login-title { font-size: 26px; }
            .teacher-login-subtitle { margin-bottom: 11px; }
            .st-key-teacher_login_card input { min-height: 38px !important; }
            .st-key-teacher_login_btn button, .st-key-teacher_register_btn button { min-height: 43px !important; }
        }

        @media (max-width: 700px) {
            html, body { overflow-x: hidden !important; overflow-y: auto !important; }
            .dashboard-topbar { padding: 5px 1px 12px; }
            .dashboard-logo { font-size: 23px; }
            .dashboard-portal { padding: 6px 9px; font-size: 9px; }
            .st-key-teacher_dashboard_hero { padding: 21px 17px !important; border-radius: 21px !important; }
            .dashboard-title { font-size: 25px; }
            .dashboard-subtitle { font-size: 12px; }
            .dashboard-stats { grid-template-columns: 1fr; gap: 9px; margin: 13px 0 18px; }
            .dashboard-stat { padding: 12px 14px; }
            .dashboard-section-label { font-size: 13px; }
            .st-key-teacher_tab_attendance button,
            .st-key-teacher_tab_subjects button,
            .st-key-teacher_tab_records button { min-height: 45px !important; font-size: 11px !important; }
            .main .block-container { max-width: 100% !important; padding: .15rem 12px 15px !important; }
            .teacher-topbar { height: 52px; padding: 0 3px; }
            .teacher-logo { font-size: 22px; }
            .teacher-badge { padding: 6px 9px; font-size: 9px; }
            .st-key-teacher_back_btn {
                top: 63px !important;
                left: 12px !important;
            }

            .st-key-teacher_back_btn button {
                min-height: 36px !important;
                padding: 4px 13px !important;
                font-size: 11px !important;
            }
            .teacher-note { font-size: 11px; opacity: .65; }
            .st-key-teacher_login_card { max-width: none; margin-top: 3vh !important; padding: 23px 19px 19px !important; border-radius: 22px !important; }
            .teacher-login-title { font-size: 26px; }
            .teacher-login-subtitle { font-size: 12px; }
            .teacher-line-art { opacity: .62; }
        }

        @media (max-width: 390px) {
            .teacher-badge { max-width: 145px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .teacher-login-title { font-size: 24px; }
            .st-key-teacher_login_card { padding: 21px 16px 17px !important; }
        }
    </style>
    """)
