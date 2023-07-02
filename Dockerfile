FROM python:3.11
EXPOSE 5000
WORKDIR /order_managment_app
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "--app", "/order_managment_app/app.py", "run", "--debug"]