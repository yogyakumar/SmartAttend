import streamlit as st
from streamlit_mic_recorder import mic_recorder
import numpy as np
import time
from PIL import Image

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.dialog_enroll import enroll_dialog
from src.database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    update_student_profile,
    get_student_biometrics,
    add_student_biometric,
    unenroll_student_to_subject,
)
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding


FACE_THRESHOLD = 0.60
VOICE_THRESHOLD = 0.60


def _as_array(value):
    if value is None:
        return None
    try:
        arr = np.asarray(value, dtype=np.float32)
        if arr.size == 0:
            return None
        return arr
    except Exception:
        return None


def _face_matches(candidate, reference):
    a = _as_array(candidate)
    b = _as_array(reference)
    if a is None or b is None or a.shape != b.shape:
        return False
    return float(np.linalg.norm(a - b)) <= FACE_THRESHOLD


def _voice_similarity(candidate, reference):
    a = _as_array(candidate)
    b = _as_array(reference)
    if a is None or b is None or a.shape != b.shape:
        return -1.0
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return -1.0
    return float(np.dot(a, b) / (na * nb))


def _voice_matches(candidate, reference):
    return _voice_similarity(candidate, reference) >= VOICE_THRESHOLD


def _student_biometrics(student):
    rows = get_student_biometrics(student["student_id"])
    faces = []
    voices = []

    if student.get("face_embedding") is not None:
        faces.append(student["face_embedding"])
    if student.get("voice_embedding") is not None:
        voices.append(student["voice_embedding"])

    for row in rows:
        if row.get("biometric_type") == "face":
            faces.append(row.get("embedding"))
        elif row.get("biometric_type") == "voice":
            voices.append(row.get("embedding"))

    return faces, voices


def _verify_new_face(student, candidate):
    own_faces, _ = _student_biometrics(student)
    if not own_faces:
        return False, "No registered face was found for verification."

    if not any(_face_matches(candidate, old) for old in own_faces):
        return False, "This face does not match your registered face."

    for other in get_all_students():
        if int(other["student_id"]) == int(student["student_id"]):
            continue
        other_faces, _ = _student_biometrics(other)
        if any(_face_matches(candidate, old) for old in other_faces):
            return False, "This face matches another student's profile."

    return True, "Face verified."


def _verify_new_voice(student, candidate):
    _, own_voices = _student_biometrics(student)

    if not own_voices:
        return False, "No registered voice was found for verification."

    best_score = -1.0

    for old in own_voices:
        score = _voice_similarity(candidate, old)
        best_score = max(best_score, score)

    if best_score < VOICE_THRESHOLD:
        return (
            False,
            f"This voice does not match your registered voice. "
            f"Similarity: {best_score:.3f}"
        )

    for other in get_all_students():
        if int(other["student_id"]) == int(student["student_id"]):
            continue

        _, other_voices = _student_biometrics(other)

        for old in other_voices:
            if _voice_similarity(candidate, old) >= VOICE_THRESHOLD:
                return False, "This voice matches another student's profile."

    return True, f"Voice verified. Similarity: {best_score:.3f}"


def _find_student_by_face(image, students):
    encodings = get_face_embeddings(image)

    if not encodings:
        return None, 0, "No face detected."

    if len(encodings) > 1:
        return None, len(encodings), "Multiple faces detected."

    candidate = _as_array(encodings[0])

    if candidate is None:
        return None, 1, "Face embedding could not be generated."

    best_student = None
    best_distance = float("inf")

    for student in students:
        own_faces, _ = _student_biometrics(student)

        for reference in own_faces:
            reference = _as_array(reference)

            if reference is None:
                continue

            if candidate.shape != reference.shape:
                continue

            distance = float(np.linalg.norm(candidate - reference))

            if distance < best_distance:
                best_distance = distance
                best_student = student

    if best_student is not None and best_distance <= FACE_THRESHOLD:
        return best_student, 1, None

    return None, 1, None

def _refresh_student_data():
    student_id = st.session_state["student_data"]["student_id"]
    student = next(
        (s for s in get_all_students() if int(s["student_id"]) == int(student_id)),
        None,
    )
    if student:
        st.session_state["student_data"] = student


def _logout_student():
    st.session_state["is_logged_in"] = False
    for key in [
        "student_data",
        "student_camera_active",
        "student_show_registration",
        "student_registration_image",
        "student_account_page",
        "student_biometric_mode",
    ]:
        st.session_state.pop(key, None)
    st.rerun()


def _student_css():
    st.html("""
    <style>
    html, body { margin:0 !important; padding:0 !important; overflow-x:hidden !important; }
    .stApp {
        min-height:100vh !important;
        background:
            radial-gradient(circle at 12% 12%, rgba(205,226,255,.48), transparent 28%),
            radial-gradient(circle at 88% 20%, rgba(213,211,255,.44), transparent 30%),
            linear-gradient(135deg,#fbfdff 0%,#eef5ff 52%,#f7f6ff 100%) !important;
    }
    .main .block-container {
        max-width:1180px !important;
        padding:.7rem 1rem 2rem !important;
    }
    .sa-student-top {
        display:flex; align-items:center; justify-content:space-between;
        gap:12px; margin-bottom:24px;
    }
    .sa-student-logo {
        color:#13284a; font-size:29px; font-weight:850; letter-spacing:-1.5px;
    }
    .sa-student-logo span { color:#3977eb; }
    .sa-portal-pill {
        padding:8px 15px; border-radius:999px; background:rgba(255,255,255,.86);
        border:1px solid #c9dcf5; color:#42648d; font-size:12px; font-weight:750;
    }
    .st-key-student_back_home { margin-bottom:12px; }
    .st-key-student_back_home button {
        min-height:38px !important; padding:4px 14px !important;
        border-radius:22px !important; color:#3168a8 !important;
        border:1px solid #b9d3f3 !important; background:rgba(255,255,255,.9) !important;
    }
    .sa-login-card {
        max-width:560px; margin:5vh auto 0; padding:30px 34px;
        border-radius:28px; background:rgba(255,255,255,.92);
        border:1px solid #c8dcf5; box-shadow:0 25px 65px rgba(62,91,145,.14);
    }
    .sa-login-icon {
        width:64px; height:64px; margin:0 auto 13px; display:flex; align-items:center;
        justify-content:center; border-radius:50%; background:#e5edff; font-size:29px;
    }
    .sa-login-title { text-align:center; color:#13284a; font-size:34px; font-weight:850; line-height:1.08; }
    .sa-login-title span { color:#3977eb; }
    .sa-login-sub { text-align:center; color:#7c90ad; font-size:13px; margin:10px auto 22px; }
    .sa-dashboard-card, .sa-account-card {
        background:rgba(255,255,255,.88); border:1px solid #cbdff6;
        border-radius:24px; padding:24px; box-shadow:0 15px 40px rgba(62,91,145,.08);
    }
    .sa-welcome { color:#7186a3; font-size:13px; }
    .sa-name { color:#16345d; font-size:30px; font-weight:850; margin-top:2px; }
    .sa-field-label { color:#7890ad; font-size:11px; font-weight:750; text-transform:uppercase; letter-spacing:.6px; }
    .sa-field-value { color:#18375e; font-size:18px; font-weight:800; margin-top:3px; }
    .sa-section-title { color:#18375e; font-size:23px; font-weight:850; margin:4px 0 3px; }
    .sa-section-sub { color:#7890ad; font-size:12px; margin-bottom:18px; }
    .sa-account-option {
        padding:17px; border:1px solid #d7e5f7; border-radius:17px;
        background:linear-gradient(135deg,#f6faff,#f5f4ff); margin-bottom:12px;
    }
    .sa-option-title { color:#28588f; font-size:14px; font-weight:800; }
    .sa-option-sub { color:#7a90ad; font-size:11px; margin-top:3px; }
    .sa-biometric-box {
        padding:20px; border:1px solid #d4e3f6; border-radius:18px;
        background:rgba(247,251,255,.88);
    }
    .sa-mobile-stack { width:100%; }
    @media (max-width:700px) {
        .main .block-container { padding:.45rem .7rem 1.5rem !important; }
        .sa-student-logo { font-size:23px; }
        .sa-portal-pill { font-size:10px; padding:7px 10px; }
        .sa-login-card { width:calc(100% - 8px); margin-top:4vh; padding:23px 16px; border-radius:23px; }
        .sa-login-title { font-size:28px; }
        .sa-login-sub { font-size:11px; }
        .sa-dashboard-card, .sa-account-card { padding:17px; border-radius:19px; }
        .sa-name { font-size:24px; }
        .sa-section-title { font-size:20px; }
        .st-key-student_account_btn button, .st-key-student_logout button,
        .st-key-student_enroll_btn button, .st-key-student_save_profile button,
        .st-key-student_update_face_button button, .st-key-student_update_voice_button button,
        .st-key-student_cancel_bio button, .st-key-student_save_face button,
        .st-key-student_save_voice button, .st-key-student_account_back button {
            width:100% !important;
        }
    }
    </style>
    """)


def student_dashboard():
    _student_css()
    student = st.session_state["student_data"]

    st.html(f"""
    <div class="sa-student-top">
        <div class="sa-student-logo">Smart<span>Attend</span></div>
        <div class="sa-portal-pill">👤 Student Portal</div>
    </div>
    """)

    top1, top2 = st.columns([1,1], vertical_alignment="center")
    with top1:
        st.html(f"""
        <div class="sa-dashboard-card">
            <div class="sa-welcome">Welcome back</div>
            <div class="sa-name">{student.get("name","Student")}</div>
        </div>
        """)
    with top2:
        a, b = st.columns(2)
        with a:
            if st.button("Account", key="student_account_btn", type="secondary", use_container_width=True):
                st.session_state["student_account_page"] = True
                st.rerun()
        with b:
            if st.button("Logout", key="student_logout", type="secondary", use_container_width=True):
                _logout_student()

    if st.session_state.get("student_account_page", False):
        _account_page()
        return

    st.write("")
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.html(f"""
        <div class="sa-dashboard-card">
            <div class="sa-field-label">Student Name</div>
            <div class="sa-field-value">{student.get("name","—")}</div>
        </div>
        """)
    with c2:
        st.html(f"""
        <div class="sa-dashboard-card">
            <div class="sa-field-label">Enrollment / Roll No.</div>
            <div class="sa-field-value">{student.get("enrollment_number") or "Not added"}</div>
        </div>
        """)

    st.write("")

    enrolled_subjects = get_student_subjects(student["student_id"])

    st.html("""
    <div class="sa-dashboard-card">
        <div class="sa-section-title">Course Enrollment</div>
        <div class="sa-section-sub">Your enrolled courses and subjects.</div>
    </div>
    """)

    if enrolled_subjects:
        for item in enrolled_subjects:
            subject = item.get("subjects") or {}

            subject_name = subject.get("name") or "Unnamed Subject"
            subject_code = subject.get("subject_code") or "N/A"
            section = subject.get("section") or "N/A"

            st.html(f"""
            <div class="sa-dashboard-card" style="margin-top:12px;">
                <div class="sa-field-label">SUBJECT</div>
                <div class="sa-field-value">{subject_name}</div>
                <div style="margin-top:8px;color:#7890ad;font-size:12px;">
                    Code: <b>{subject_code}</b>
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    Section: <b>{section}</b>
                </div>
            </div>
            """)
    else:
        st.html("""
        <div class="sa-dashboard-card" style="margin-top:12px;">
            <div class="sa-option-title">No course enrolled yet</div>
            <div class="sa-option-sub">
                Enroll in a subject to see it here.
            </div>
        </div>
        """)

    st.write("")

    if st.button(
        "📚  Enroll in Course",
        key="student_enroll_btn",
        type="primary",
        use_container_width=True
    ):
        enroll_dialog()


def _account_page():
    student = st.session_state["student_data"]

    st.html("""
    <div class="sa-account-card">
        <div class="sa-section-title">Account</div>
        <div class="sa-section-sub">Manage your personal details and biometric profile.</div>
    </div>
    """)
    st.write("")

    if st.session_state.get("student_biometric_mode") is None:
        st.html("""
        <div class="sa-account-card">
            <div class="sa-option-title">👤 Personal Details</div>
            <div class="sa-option-sub">Change your name and enrollment number.</div>
        </div>
        """)
        name = st.text_input("Full Name", value=student.get("name", ""), key="student_profile_name")
        enrollment = st.text_input(
            "Enrollment / Roll No.",
            value=student.get("enrollment_number") or "",
            key="student_profile_enrollment",
        )
        if st.button("Save Changes", key="student_save_profile", type="primary", use_container_width=True):
            name = name.strip()
            enrollment = enrollment.strip()
            if not name or not enrollment:
                st.error("Name and enrollment number are required.")
            else:
                try:
                    updated = update_student_profile(student["student_id"], name, enrollment)
                    if updated:
                        _refresh_student_data()
                        st.success("Profile updated successfully.")
                        time.sleep(.5)
                        st.rerun()
                    else:
                        st.error("Profile could not be updated.")
                except Exception as e:
                    if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                        st.error("This enrollment number is already registered.")
                    else:
                        st.error("Profile update failed.")

        st.write("")
        st.html("""
        <div class="sa-account-card">
            <div class="sa-option-title">🔐 Face & Voice</div>
            <div class="sa-option-sub">Add another face or voice after identity verification.</div>
        </div>
        """)
        f, v = st.columns(2, gap="small")
        with f:
            if st.button("Update Face", key="student_update_face_button", type="secondary", use_container_width=True):
                st.session_state["student_biometric_mode"] = "face"
                st.rerun()
        with v:
            if st.button("Update Voice", key="student_update_voice_button", type="secondary", use_container_width=True):
                st.session_state["student_biometric_mode"] = "voice"
                st.rerun()

    elif st.session_state["student_biometric_mode"] == "face":
        _add_face_page()
    elif st.session_state["student_biometric_mode"] == "voice":
        _add_voice_page()

    if st.session_state.get("student_biometric_mode") is None:
        if st.button("← Back to Dashboard", key="student_account_back", type="secondary", use_container_width=True):
            st.session_state["student_account_page"] = False
            st.rerun()


def _add_face_page():
    student = st.session_state["student_data"]
    st.html("""
    <div class="sa-account-card">
        <div class="sa-section-title">Update Face</div>
        <div class="sa-section-sub">Your existing face will be verified first. The new face is saved only if it belongs to you.</div>
    </div>
    """)
    photo = st.camera_input("Capture your new face", key="student_new_face_camera")
    c1, c2 = st.columns(2)
    with c1:
        save = st.button("Verify & Update Face", key="student_save_face", type="primary", use_container_width=True)
    with c2:
        cancel = st.button("Cancel", key="student_cancel_bio", type="secondary", use_container_width=True)

    if cancel:
        st.session_state["student_biometric_mode"] = None
        st.rerun()

    if save:
        if photo is None:
            st.warning("Please capture a face first.")
            return
        with st.spinner("Verifying your face..."):
            image = np.array(Image.open(photo).convert("RGB"))
            encodings = get_face_embeddings(image)
            if not encodings:
                st.error("No clear face was detected. Please try again.")
                return
            if len(encodings) != 1:
                st.error("Please capture exactly one face.")
                return
            candidate = encodings[0].tolist()
            ok, message = _verify_new_face(student, candidate)
            if not ok:
                st.error(message)
                return
            try:
                added = add_student_biometric(student["student_id"], "face", candidate)
                if added:
                    train_classifier()
                    st.success("Face updated successfully.")
                    st.session_state["student_biometric_mode"] = None
                    _refresh_student_data()
                    time.sleep(.5)
                    st.rerun()
                else:
                    st.error("Face could not be saved.")
            except Exception:
                st.error("Face could not be saved.")


def _add_voice_page():
    student = st.session_state["student_data"]
    st.html("""
    <div class="sa-account-card">
        <div class="sa-section-title">Update Voice</div>
        <div class="sa-section-sub">Verify your existing voice first. The updated voice is saved only if it belongs to you.</div>
    </div>
    """)

    recorded_voice = mic_recorder(
        start_prompt="🎙️ Start Voice Recording",
        stop_prompt="⏹️ Stop Voice Recording",
        just_once=True,
        use_container_width=True,
        key="student_update_voice_recorder",
    )

    if recorded_voice:
        st.session_state["student_update_voice_bytes"] = recorded_voice["bytes"]

    audio_bytes = st.session_state.get("student_update_voice_bytes")

    if audio_bytes:
        st.success("Voice recorded successfully. Click Verify & Update Voice to continue.")
        st.audio(audio_bytes, format="audio/wav")

    c1, c2 = st.columns(2)
    with c1:
        save = st.button("Verify & Update Voice", key="student_save_voice", type="primary", use_container_width=True)
    with c2:
        cancel = st.button("Cancel", key="student_cancel_bio", type="secondary", use_container_width=True)

    if cancel:
        st.session_state.pop("student_update_voice_bytes", None)
        st.session_state["student_biometric_mode"] = None
        st.rerun()

    if save:
        if not audio_bytes:
            st.warning("Please record your voice first.")
            return

        with st.spinner("Verifying your voice..."):
            try:
                candidate = get_voice_embedding(audio_bytes)
            except Exception as e:
                st.error(f"Voice processing failed: {e}")
                return

            if candidate is None:
                st.error("Voice embedding could not be generated. Please record again.")
                return

            if hasattr(candidate, "tolist"):
                candidate = candidate.tolist()

            ok, message = _verify_new_voice(student, candidate)
            if not ok:
                st.error(message)
                return

            try:
                added = add_student_biometric(student["student_id"], "voice", candidate)
                if added:
                    st.success("Voice updated successfully.")
                    st.session_state.pop("student_update_voice_bytes", None)
                    st.session_state["student_biometric_mode"] = None
                    _refresh_student_data()
                    time.sleep(.5)
                    st.rerun()
                else:
                    st.error("Voice could not be updated.")
            except Exception as e:
                st.error(f"Voice could not be updated: {e}")


def student_login_page():
    _student_css()

    if "student_show_registration" not in st.session_state:
        st.session_state["student_show_registration"] = False

    st.html("""
    <div class="sa-student-top">
        <div class="sa-student-logo">Smart<span>Attend</span></div>
        <div class="sa-portal-pill">👤 Student Portal</div>
    </div>
    """)

    if st.button("← Back to Home", key="student_back_home", type="secondary"):
        for key in [
            "student_show_registration",
            "student_registration_image",
            "student_new_name",
            "student_new_enrollment",
            "student_voice_enrollment",
            "student_registration_voice_bytes",
            "student_update_voice_bytes",
        ]:
            st.session_state.pop(key, None)
        st.session_state["login_type"] = None
        st.rerun()

    if st.session_state.get("student_show_registration"):
        _student_registration()
        return

    st.html("""
    <div class="sa-login-card">
        <div class="sa-login-icon">👤</div>
        <div class="sa-login-title">Welcome,<br><span>Student</span></div>
        <div class="sa-login-sub">Capture your face. If you are new, SmartAttend will automatically open first-time registration.</div>
    </div>
    """)

    photo = st.camera_input(
        "📷 Capture Face",
        key="student_login_camera"
    )

    st.html("""
    <div class="sa-account-option">
        <div class="sa-option-title">📷 FaceID Login / First-Time Registration</div>
        <div class="sa-option-sub">Registered students are logged in automatically. A new face opens the required Face + Voice registration.</div>
    </div>
    """)

    if photo is None:
        return

    try:
        image = np.array(Image.open(photo).convert("RGB"))
    except Exception as e:
        st.error(f"Captured image could not be read: {e}")
        return

    all_students = get_all_students()

    if not all_students:
        st.session_state["student_registration_image"] = image
        st.session_state["student_show_registration"] = True
        st.rerun()
        return

    with st.spinner("AI is scanning your face..."):
        try:
            student, num_faces, error_message = _find_student_by_face(
                image,
                all_students
            )
        except Exception as e:
            st.error(f"Face recognition failed: {e}")
            return

    if error_message:
        st.warning(error_message)
        return

    if num_faces == 0:
        st.warning("No face detected. Please capture your face again.")
        return

    if num_faces > 1:
        st.warning("Multiple faces detected. Please capture only your face.")
        return

    if student:
        st.session_state["student_data"] = student
        st.session_state["is_logged_in"] = True
        st.session_state["user_role"] = "student"

        st.toast(f"Welcome back, {student['name']}")

        time.sleep(.5)
        st.rerun()
        return

    st.session_state["student_registration_image"] = image
    st.session_state["student_show_registration"] = True
    st.rerun()

def _student_registration():
    st.html("""
    <div class="sa-login-card">
        <div class="sa-login-icon">📚</div>
        <div class="sa-login-title">Create your<br><span>Student Profile</span></div>
        <div class="sa-login-sub">First-time registration requires both Face + Voice biometrics.</div>
    </div>
    """)

    image = st.session_state.get("student_registration_image")

    if image is None:
        st.error("Face capture is missing. Please go back and capture your face again.")
        return

    st.success("Face captured successfully. Now complete your profile and voice enrollment.")

    name = st.text_input(
        "Full Name",
        placeholder="Enter your full name",
        key="student_new_name"
    )
    enrollment = st.text_input(
        "Enrollment / Roll No.",
        placeholder="Enter your enrollment number",
        key="student_new_enrollment"
    )

    st.html("""
    <div class="sa-account-card" style="margin:14px 0;">
        <div class="sa-section-title">🎙️ Voice Enrollment</div>
        <div class="sa-section-sub">Click the recording button once to start. Click it again to stop. Say a clear phrase such as “I am present”.</div>
    </div>
    """)

    recorded_voice = mic_recorder(
        start_prompt="🎙️ Start Voice Recording",
        stop_prompt="⏹️ Stop Voice Recording",
        just_once=True,
        use_container_width=True,
        key="student_registration_voice_recorder",
    )

    if recorded_voice:
        st.session_state["student_registration_voice_bytes"] = recorded_voice["bytes"]

    audio_bytes = st.session_state.get("student_registration_voice_bytes")

    if audio_bytes:
        st.success("Voice recorded successfully. Both biometrics are ready for submission.")
        st.audio(audio_bytes, format="audio/wav")

    if st.button(
        "Create Student Account →",
        key="student_create_account",
        type="primary",
        use_container_width=True,
    ):
        name = name.strip()
        enrollment = enrollment.strip()

        if not name:
            st.warning("Please enter your name.")
            return
        if not enrollment:
            st.warning("Please enter your enrollment number.")
            return
        if not audio_bytes:
            st.warning("Please record your voice first. Face + voice are required for initial registration.")
            return

        if not audio_bytes:
            st.warning("Voice recording is empty. Please record again.")
            return

        with st.spinner("Creating your Face + Voice profile..."):
            encodings = get_face_embeddings(image)
            if not encodings:
                st.error("Could not capture facial features. Please try another face photo.")
                return
            if len(encodings) != 1:
                st.error("Please register with exactly one face in the photo.")
                return

            face = encodings[0].tolist()

            try:
                voice = get_voice_embedding(audio_bytes)
            except Exception as e:
                st.error(f"Voice processing failed: {e}")
                return

            if voice is None:
                st.error("Voice embedding could not be generated. Please record your voice again.")
                return

            if hasattr(voice, "tolist"):
                voice = voice.tolist()

            try:
                response = create_student(
                    name,
                    enrollment_number=enrollment,
                    face_embedding=face,
                    voice_embedding=voice,
                )
            except Exception as e:
                if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                    st.error("This enrollment number is already registered.")
                else:
                    st.error(f"Student account could not be created: {e}")
                return

            if not response:
                st.error("Student account could not be created.")
                return

            train_classifier()
            st.session_state["student_data"] = response[0]
            st.session_state["is_logged_in"] = True
            st.session_state["user_role"] = "student"

            for key in [
                "student_show_registration",
                "student_registration_image",
                "student_new_name",
                "student_new_enrollment",
                "student_voice_enrollment",
            "student_registration_voice_bytes",
            "student_update_voice_bytes",
            ]:
                st.session_state.pop(key, None)

            st.success("Student profile created successfully with Face + Voice biometrics.")
            time.sleep(.7)
            st.rerun()

def student_screen():
    if "student_data" in st.session_state:
        student_dashboard()
        return
    style_base_layout()
    student_login_page()
