@echo off
setlocal

echo.
echo [1/3] Installing project dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Dependency installation failed.
    pause
    exit /b 1
)

echo.
echo [2/3] Installing Resemblyzer without its source-only webrtcvad dependency...
python -m pip install --no-deps resemblyzer
if errorlevel 1 (
    echo.
    echo Resemblyzer installation failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Checking imports...
python -c "from resemblyzer import VoiceEncoder, preprocess_wav; import webrtcvad; import imageio_ffmpeg; print('SmartAttend voice dependencies OK')"
if errorlevel 1 (
    echo.
    echo Voice dependency check failed.
    pause
    exit /b 1
)

echo.
echo Installation complete.
echo Run the app with:
echo streamlit run app.py
echo.
pause
