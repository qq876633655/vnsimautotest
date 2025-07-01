import json
import paho.mqtt.client as mqtt

def publish_reset_localization(payload: dict):
    broker = "localhost"
    port = 1883
    topic = "agv/v1/s/localization/resetLocalization"

    client = mqtt.Client()
    client.connect(broker, port, 60)

    client.publish(topic, json.dumps(payload))
    client.disconnect()

if __name__ == "__main__":
    reset_loc_data = {
        "method": "resetLocalization",
        "srcAddr": "c1",
        "seq": "123456",
        "version": "1.0.1",
        "timestamp": "2014-04-05T12:30:00.12Z",
        "payload": {
            "timestamp": "2014-04-05T12:30:00.12Z",
            "seeds": [
                {
                    "pos": {
                        "x": 0,
                        "y": 0,
                        "z": 0,
                        "roll": 0,
                        "yaw": 0,
                        "pitch": 0,
                    },
                    "error": {
                        "x": 0.1,
                        "y": 0.1,
                        "z": 0.1,
                        "roll": 0.1,
                        "yaw": 0.1,
                        "pitch": 0.1,
                    }
                }
            ]
        }
    }
    switch_map_data = {
        "method": "switchMap",
        "srcAddr": "c1",
        "seq": "123456",
        "version": "1.0.1",
        "timestamp": "2014-04-05T12:30:00.12Z",
        "payload": {
            "timestamp": "2014-04-05T12:30:00.12Z",
            "mapName": "floor1",
        }
    }

    publish_reset_localization(data)