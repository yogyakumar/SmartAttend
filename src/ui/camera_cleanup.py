import streamlit as st

def stop_camera_streams():
    st.html("""
    <script>
    (() => {
        const stopCameras = () => {
            document.querySelectorAll('video').forEach(video => {
                try {
                    if (video.srcObject) {
                        video.srcObject.getTracks().forEach(track => {
                            track.stop();
                        });
                        video.srcObject = null;
                    }
                } catch (e) {}
            });
        };

        stopCameras();
    })();
    </script>
    """)