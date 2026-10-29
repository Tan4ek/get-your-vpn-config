FROM python:3.13.18-slim-bookworm AS get-your-vpn-config-build
COPY requirements.txt .
RUN pip3 install --no-cache-dir --user --no-warn-script-location -r requirements.txt

FROM python:3.13.18-slim-bookworm
WORKDIR /app
COPY --from=get-your-vpn-config-build /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

COPY . /app

# manager port
EXPOSE 8080

CMD ["gunicorn", "wsgi:app", "--preload", "--bind", "0.0.0.0:8080"]
