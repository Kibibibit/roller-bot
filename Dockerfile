FROM python:3.12.1
ADD main.py .
ADD .env .
RUN pip install python-dotenv discord.py

CMD ["python", "./main.py"]