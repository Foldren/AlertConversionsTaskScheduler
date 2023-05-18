FROM python:alpine 
WORKDIR /home
RUN apk update
COPY /source /source
WORKDIR /source
RUN pip install httpx emoji-country-flag
CMD ["python", "bot.py"]
