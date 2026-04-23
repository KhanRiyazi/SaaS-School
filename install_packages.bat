@echo off
echo Installing packages with retry logic...

pip install --default-timeout=100 fastapi
if errorlevel 1 (
    echo Retrying fastapi...
    timeout /t 5
    pip install --default-timeout=100 fastapi
)

pip install --default-timeout=100 uvicorn
if errorlevel 1 (
    echo Retrying uvicorn...
    timeout /t 5
    pip install --default-timeout=100 uvicorn
)

pip install --default-timeout=100 streamlit
if errorlevel 1 (
    echo Retrying streamlit...
    timeout /t 5
    pip install --default-timeout=100 streamlit
)

pip install --default-timeout=100 qrcode
pip install --default-timeout=100 Pillow
pip install --default-timeout=100 shortuuid
pip install --default-timeout=100 pydantic
pip install --default-timeout=100 redis
pip install --default-timeout=100 python-dotenv
pip install --default-timeout=100 validators
pip install --default-timeout=100 streamlit-option-menu
pip install --default-timeout=100 requests
pip install --default-timeout=100 python-multipart

echo Installation complete!
pause