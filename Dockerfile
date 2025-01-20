FROM python:3.10
EXPOSE 8080
WORKDIR /app
COPY requirements.txt .
COPY frontend.py /app/frontend.py
RUN pip install -r requirements.txt
CMD streamlit run --server.port 8080 --server.enableCORS false frontend.py 
