FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY mqtt_simulator.py ./
ENV BROKER=broker PORT=1883 PREFIX=building/demo QOS=0 INTERVAL=10 DURATION=
ENV MQTT_USER=demo_user MQTT_PASS=demo_pass
CMD python mqtt_simulator.py --broker ${BROKER} --port ${PORT} --prefix ${PREFIX} --qos ${QOS} --interval ${INTERVAL} ${DURATION:+--duration ${DURATION}}
