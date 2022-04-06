FROM python:3.8-alpine as get-your-vpn-config-build
COPY requirements.txt .
RUN pip3 install --no-cache-dir --user --no-warn-script-location  -r requirements.txt

FROM python:3.8-alpine
WORKDIR /app
COPY --from=get-your-vpn-config-build /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH
RUN apk add --no-cache make

COPY . /app

# manager port
EXPOSE 8080

CMD ["make", "up"]