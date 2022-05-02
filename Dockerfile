FROM node AS build
WORKDIR /my-app
COPY code/frontend/ .
RUN npm install
RUN npm run build


FROM debian

LABEL maintainer="rgreaves@google.com"

RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev

COPY /code /app
COPY --from=build /my-app/build /app/frontend/build

WORKDIR /app
RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD ["python3", "main.py"]