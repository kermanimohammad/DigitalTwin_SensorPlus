#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, argparse, json, math, random, signal, time
import paho.mqtt.client as mqtt

def now_ms(): return int(time.time()*1000)
def clamp(v, lo, hi): return max(lo, min(hi, v))

class RoomState:
    def __init__(self, room_id, temp, hum, co2):
        self.room_id=room_id; self.temp_c=temp; self.humidity=hum; self.co2=co2
        self.light_on=False; self.light_power_w=0.0; self.occupancy=0

class SolarState:
    def __init__(self): self.power_w=0.0; self.voltage=48.0; self.current=0.0

class MQTTSim:
    def __init__(self, broker, port, prefix, qos, interval_s):
        self.broker=broker; self.port=port; self.prefix=prefix.rstrip("/"); self.qos=qos; self.interval_s=interval_s
        self.client=mqtt.Client()
        self.client.on_connect=lambda c,u,f,rc: print(f"[MQTT] Connected rc={rc}")
        self.client.on_disconnect=lambda c,u,rc: print(f"[MQTT] Disconnected rc={rc}")
        self.rooms=[RoomState(f"room{i}", random.uniform(21,24), random.uniform(30,45), random.uniform(450,650)) for i in range(1,6)]
        self.solar=SolarState(); self.running=True

    def step_room(self,r,dt):
        r.temp_c += (22.0 - r.temp_c)*0.01*dt + 0.02*r.occupancy*dt + random.uniform(-0.02,0.02)
        r.temp_c = clamp(r.temp_c,16,32)
        target_h = 40 + min(15,2*r.occupancy)
        r.humidity += (target_h - r.humidity)*0.02*dt + random.uniform(-0.1,0.1)
        r.humidity = clamp(r.humidity,20,80)
        r.co2 += (420-r.co2)*0.02*dt + r.occupancy*8*dt + random.uniform(-2,2)
        r.co2 = clamp(r.co2,350,3000)
        r.light_power_w = 18+random.uniform(-1,1) if r.light_on else 0

    def step_solar(self, t):
        p = max(0, math.sin((t%120)/120*math.pi))*1000 + random.uniform(-20,20)
        self.solar.power_w = clamp(p,0,1100)
        self.solar.voltage = 48+random.uniform(-0.5,0.5)
        self.solar.current = self.solar.power_w/max(1,self.solar.voltage)

    def pub(self, topic, payload): self.client.publish(topic, json.dumps(payload), qos=self.qos)
    def publish_room(self,r):
        ts=now_ms(); base=f"{self.prefix}/{r.room_id}"; i=r.room_id[-1]
        self.pub(f"{base}/temperature",{"deviceId":f"temp-{i}","kind":"temperature","roomId":r.room_id,"ts":ts,"value":round(r.temp_c,2),"unit":"C"})
        self.pub(f"{base}/humidity",   {"deviceId":f"hum-{i}","kind":"humidity","roomId":r.room_id,"ts":ts,"value":round(r.humidity,1),"unit":"%"})
        self.pub(f"{base}/co2",        {"deviceId":f"co2-{i}","kind":"co2","roomId":r.room_id,"ts":ts,"value":int(r.co2),"unit":"ppm"})
        self.pub(f"{base}/light",      {"deviceId":f"light-{i}","kind":"light","roomId":r.room_id,"ts":ts,"on":r.light_on,"powerW":round(r.light_power_w,1)})
    def publish_solar(self):
        ts=now_ms(); self.pub(f"{self.prefix}/solar",{"deviceId":"solar-plant","kind":"solar","ts":ts,"powerW":round(self.solar.power_w,1),"voltage":round(self.solar.voltage,2),"current":round(self.solar.current,2)})

    def run(self, duration=None):
        # تنظیم احراز هویت فقط در صورت وجود
        mqtt_user = os.getenv("MQTT_USER", "")
        mqtt_pass = os.getenv("MQTT_PASS", "")
        if mqtt_user and mqtt_pass:
            self.client.username_pw_set(mqtt_user, mqtt_pass)
        
        # تنظیم SSL برای broker های خارجی
        if self.port == 8883:
            self.client.tls_set()
        
        self.client.connect(self.broker, self.port, keepalive=30)
        self.client.loop_start()
        t0=time.time(); last=t0
        try:
            while True:
                now=time.time(); dt=now-last; last=now; elapsed=now-t0
                for r in self.rooms: self.step_room(r,dt)
                self.step_solar(elapsed)
                for r in self.rooms: self.publish_room(r)
                self.publish_solar()
                time.sleep(self.interval_s)
                if duration and (now-t0)>=duration: break
        finally:
            self.client.loop_stop(); self.client.disconnect()

if __name__=="__main__":
    # اولویت با ENV برای داکر؛ CLI هم پشتیبانی می‌شود
    broker = os.getenv("BROKER", "broker")
    port   = int(os.getenv("PORT", "1883"))
    prefix = os.getenv("PREFIX", "building/demo")
    qos    = int(os.getenv("QOS", "0"))
    interval = float(os.getenv("INTERVAL", "10"))
    duration = os.getenv("DURATION", "")
    duration = int(duration) if duration else None
    sim = MQTTSim(broker, port, prefix, qos, interval)
    sim.run(duration)
