import streamlit as st

from src.database.db import create_attendance


def show_attendance_result(df, logs, result_key="attendance_results"):

    if df is None or df.empty:
        st.warning("No attendance result available.")
        return

    total = len(df)
    present = int((df["Status"] == "✅ Present").sum())
    absent = total - present

    st.html(f"""
    <div style="
        padding:18px;
        border:1px solid #cfe0f5;
        border-radius:18px;
        background:linear-gradient(135deg,#f7fbff,#f4f7ff);
        margin-bottom:16px;
    ">
        <div style="
            font-size:20px;
            font-weight:800;
            color:#18375e;
            margin-bottom:12px;
        ">
            Attendance Result
        </div>

        <div style="
            display:flex;
            gap:10px;
            flex-wrap:wrap;
        ">
            <div style="
                padding:9px 14px;
                border-radius:10px;
                background:#e8f8ef;
                color:#18794e;
                font-weight:700;
            ">
                ✅ {present} Present
            </div>

            <div style="
                padding:9px 14px;
                border-radius:10px;
                background:#fff0f0;
                color:#c93636;
                font-weight:700;
            ">
                ❌ {absent} Absent
            </div>

            <div style="
                padding:9px 14px;
                border-radius:10px;
                background:#eef4ff;
                color:#315f9d;
                font-weight:700;
            ">
                👥 {total} Total
            </div>
        </div>
    </div>
    """)

    st.write("Please review attendance before confirming.")

    st.dataframe(
        df,
        hide_index=True,
        width="stretch"
    )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Discard",
            key=f"{result_key}_discard",
            width="stretch"
        ):
            st.session_state[f"{result_key}_results"] = None
            if result_key == "face_attendance":
                st.session_state["attendance_images"] = []
            st.rerun()

    with col2:
        if st.button(
            "Confirm & Save",
            key=f"{result_key}_confirm",
            width="stretch",
            type="primary"
        ):
            if not logs:
                st.error("No attendance data is available to save.")
                return

            try:
                create_attendance(logs)

                st.session_state[f"{result_key}_results"] = None
                if result_key == "face_attendance":
                    st.session_state["attendance_images"] = []
                st.session_state["attendance_save_success"] = (
                    f"Attendance saved successfully — "
                    f"{present} Present, {absent} Absent."
                )

                st.success(
                    st.session_state["attendance_save_success"]
                )

            except Exception as e:
                st.error(
                    f"Attendance could not be saved: {e}"
                )


@st.dialog("Attendance Reports")
def attendance_result_dialog(df, logs):
    show_attendance_result(
        df,
        logs,
        result_key="face_attendance"
    )
