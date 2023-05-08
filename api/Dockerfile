FROM python:3.11

COPY . .
RUN ./setup.sh
RUN export $(cat .env | xargs)
CMD ["python3", "main.py"]
EXPOSE 8000