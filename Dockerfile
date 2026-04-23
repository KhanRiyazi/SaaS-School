FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Use mirror for faster download
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY main.py frontend.py ./

EXPOSE 8000 8501

CMD uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0