import streamlit as st
from streamlit_mic_recorder import mic_recorder
import pandas as pd

from datetime import datetime

from src.pipelines.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from src.database.db import get_student_biometrics
from src.components.dialog_attendance_results import show_attendance_result


@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):
    if st.session_state.get("voice_attendance_subject_id") != selected_subject_id:
        st.session_state.pop("voice_attendance_results", None)
        st.session_state["voice_attendance_subject_id"] = selected_subject_id

    st.html("""
    <div style="padding:18px 20px;border:1px solid #cfe0f5;border-radius:18px;background:linear-gradient(135deg,#f7fbff,#f5f6ff);margin-bottom:16px;">
        <div style="font-size:20px;font-weight:800;color:#18375e;margin-bottom:6px;">🎙️ Voice Attendance</div>
        <div style="font-size:13px;color:#7186a3;line-height:1.6;">
            Students should say <b>"I am present"</b> one after another.
            AI will identify registered student voices and mark attendance.
        </div>
    </div>
    """)

    st.info(
        "🎙️ Use the button below. One click starts recording and the same button click stops it. "
        "After all students speak, stop the recording and then analyze it."
    )

    recorded_voice = mic_recorder(
        start_prompt="🎙️ Start Classroom Recording",
        stop_prompt="⏹️ Stop Classroom Recording",
        just_once=True,
        use_container_width=True,
        key=f"voice_classroom_recorder_{selected_subject_id}",
    )

    if recorded_voice:
        st.session_state[f"voice_classroom_audio_{selected_subject_id}"] = recorded_voice["bytes"]

    audio_bytes = st.session_state.get(f"voice_classroom_audio_{selected_subject_id}")

    if audio_bytes:
        st.success("Classroom audio recorded successfully. You can now analyze it.")
        st.audio(audio_bytes, format="audio/wav")

    if st.button("🤖 Analyze Voice Attendance", width="stretch", type="primary", key="analyze_voice_attendance"):
        if not audio_bytes:
            st.warning("Please record classroom audio first.")
            return

        if not audio_bytes:
            st.warning("The recording is empty. Please record again.")
            return

        with st.spinner("AI is analyzing classroom voices..."):
            enrolled_res = (
                supabase
                .table("subject_students")
                .select("*, students(*)")
                .eq("subject_id", selected_subject_id)
                .execute()
            )
            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning("No students are enrolled in this course.")
                return

            candidates_dict = {}

            for node in enrolled_students:
                student = node.get("students") or {}
                student_id = int(student["student_id"])
                embeddings = []

                if student.get("voice_embedding") is not None:
                    embeddings.append(student["voice_embedding"])

                try:
                    biometric_rows = get_student_biometrics(student_id, "voice")
                except Exception:
                    biometric_rows = []

                for row in biometric_rows or []:
                    if row.get("embedding") is not None:
                        embeddings.append(row["embedding"])

                if embeddings:
                    candidates_dict[student_id] = embeddings[0]

            if not candidates_dict:
                st.error("No enrolled students have registered voice profiles.")
                return

            try:
                detected_scores = process_bulk_audio(audio_bytes, candidates_dict)
            except Exception as e:
                st.error(f"Voice processing failed: {e}")
                return

            if detected_scores is None:
                st.error("No voice recognition result was returned.")
                return

            results = []
            attendance_to_log = []
            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for node in enrolled_students:
                student = node["students"]
                student_id = int(student["student_id"])
                score = detected_scores.get(student_id, 0.0)
                is_present = bool(score > 0)

                results.append({
                    "Name": student["name"],
                    "Enrollment No.": student.get("enrollment_number") or "-",
                    "Source": round(float(score), 3) if is_present else "-",
                    "Status": "✅ Present" if is_present else "❌ Absent"
                })

                attendance_to_log.append({
                    "student_id": student_id,
                    "subject_id": selected_subject_id,
                    "timestamp": current_timestamp,
                    "is_present": is_present
                })

            st.session_state.voice_attendance_results = (
                pd.DataFrame(results),
                attendance_to_log
            )

    if st.session_state.get("voice_attendance_results"):
        st.divider()
        df_results, logs = st.session_state.voice_attendance_results

        present_count = int(df_results["Status"].str.contains("Present").sum())
        total_count = len(df_results)

        st.markdown(
            f"**Attendance Result:** {present_count} Present · "
            f"{total_count - present_count} Absent · {total_count} Total"
        )

        show_attendance_result(df_results, logs, result_key="voice_attendance")
