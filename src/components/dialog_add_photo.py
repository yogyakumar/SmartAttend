import streamlit as st
from PIL import Image


@st.dialog("Capture or upload photos")
def add_photos_dialog():

    if "photo_tab" not in st.session_state:
        st.session_state.photo_tab = "camera"

    if "dialog_camera_generation" not in st.session_state:
        st.session_state.dialog_camera_generation = 0

    st.write("Add classroom photos to scan for attendance")

    t1, t2 = st.columns(2)

    with t1:
        type_camera = "primary" if st.session_state.photo_tab == "camera" else "tertiary"
        if st.button("Camera", type=type_camera, width="stretch"):
            st.session_state.photo_tab = "camera"
            st.session_state.dialog_camera_generation += 1

    with t2:
        type_upload = "primary" if st.session_state.photo_tab == "upload" else "tertiary"
        if st.button("Upload photos", type=type_upload, width="stretch"):
            st.session_state.photo_tab = "upload"
            st.session_state.dialog_camera_generation += 1

    camera_slot = st.empty()

    if st.session_state.photo_tab == "camera":
        with camera_slot.container():
            cam_photo = st.camera_input(
                "Take Snapshot",
                key=f"dialog_cam_{st.session_state.dialog_camera_generation}"
            )

        if cam_photo:
            camera_slot.empty()
            st.session_state.attendance_images.append(
                Image.open(cam_photo).copy()
            )
            st.session_state.dialog_camera_generation += 1
            st.toast("Photo Captured")
            st.rerun()

    if st.session_state.photo_tab == "upload":
        uploaded_files = st.file_uploader(
            "choose image files",
            type=["jpg", "png", "jpeg"],
            accept_multiple_files=True,
            key="dialog_upload"
        )

        if uploaded_files:
            camera_slot.empty()

            for f in uploaded_files:
                st.session_state.attendance_images.append(
                    Image.open(f).copy()
                )

            st.toast("Photo Uploaded Successfully")
            st.rerun()

    st.divider()

    if st.button("Done", type="primary", width="stretch"):
        camera_slot.empty()
        st.session_state.pop("photo_tab", None)
        st.session_state.pop("dialog_camera_generation", None)
        st.rerun()
