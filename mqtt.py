import paho.mqtt.client as mqtt
import json

'''
Discovery:
    <discovery_prefix>/<component>/[node_id]/<object_id>/config

    homeassistant/sensor/pi-data/srv-docker_cpu_temp_deg/config
    {
        "name": "CPU Temp",
        "unique_id": "pi_data_srv_docker_cpu_temp_deg",
        "state_topic": "pi-data/srv-docker/state",
        "value_template": "{{ value_json.cpu_temp_deg }}",

        "availability_topic": "pi-data/srv-docker/availability",
        "payload_available": "online",
        "payload_not_available": "offline",

        "device": {
            "identifiers": ["pi_data_srv_docker"],
            "name": "srv-docker",
            "manufacturer": "PI-DATA",
            "model": "Linux Host"
        }
    }

    homeassistant/sensor/pi-data/srv-docker_mem_used_gb/config
    {
        "name": "Memory Used",
        "unique_id": "pi_data_srv_docker_mem_used_gb",
        "state_topic": "pi-data/srv-docker/state",
        "value_template": "{{ value_json.mem_used_gb }}",

        "availability_topic": "pi-data/srv-docker/availability",
        "payload_available": "online",
        "payload_not_available": "offline",

        "device": {
            "identifiers": ["pi_data_srv_docker"],
            "name": "srv-docker",
            "manufacturer": "PI-DATA",
            "model": "Linux Host"
        }
    }

    homeassistant/binary_sensor/pi-data/srv-docker_online/config
    {
        "name": "Online",
        "unique_id": "pi_data_srv_docker_online",
        "state_topic": "pi-data/srv-docker/availability",
        "payload_on": "online",
        "payload_off": "offline",
        "device_class": "connectivity",

        "device": {
            "identifiers": ["pi_data_srv_docker"],
            "name": "srv-docker",
            "manufacturer": "PI-DATA",
            "model": "Linux Host"
        }
    }



Data:
    pi-data/<host_slug>/state

    pi-data/srv-docker/state -> json payload
    {
    "hostname": "srv-docker",
    "architecture": "arm64",
    "kernel": "Linux 7.0.0-1011-raspi",
    "etc": "etc"
    }

    Availibility
    pi-data/srv-docker/availability -> str( "online" or "offline" )

###############################################################################################################
Example flow:

# make payload
payload = {
    "name": "CPU Temp",
    "unique_id": "pi_data_srv_docker_cpu_temp_deg",
    "state_topic": "pi-data/srv-docker/state",
    "value_template": "{{ value_json.cpu_temp_deg }}",
    "availability_topic": "pi-data/srv-docker/availability",
    "payload_available": "online",
    "payload_not_available": "offline",
    "device": {
        "identifiers": ["pi_data_srv_docker"],
        "name": "srv-docker",
        "manufacturer": "PI-DATA",
        "model": "Linux Host"
    }
}

#convert to json and send it
payload_json = json.dumps(payload)
slug = "homeassistant/sensor/pi-data/srv-docker_cpu_temp_deg/config"
client.publish(slug, payload_json)


# State payload for the WHOLE device
payload = parsed_dict()
state_json = json.dumps(payload)

slug = "pi-data/srv-docker/state"
client.publish(slug, state_json)
state_json = json.dumps(payload)


state = isHostOnline()
slug = "pi-data/srv-docker/availability"
client.publish(slug, state)

'''

class MqttClient():
    
    def __init__(self, mqtt_config):
        self.client = None
        self.config = mqtt_config
        

    def generate_discovery_data(self,dict_data):
        
        NAME_OVERRIDES = {
            "hostname": "Hostname",
            "architecture": "Architecture",
            "kernel": "Kernel",
            "os": "Operating System",
            "uptime": "Uptime",
            "mem_total_gb": "Memory Total",
            "mem_available_gb": "Memory Available",
            "mem_used_gb": "Memory Used",
            "disk_total_gb": "Disk Total",
            "disk_free_gb": "Disk Free",
            "disk_used_gb": "Disk Used",
            "nw_ip": "Network IP",
            "nw_interface": "Network Interface",
            "nw_total_tx_mb": "Network TX Total",
            "nw_total_rx_mb": "Network RX Total",
            "nw_total_error_pkt": "Network Errors Total",
            "nw_total_drop_pkt": "Network Drops Total",
            "load_avg_percent": "Load Average",
            "cpu_temp_deg": "CPU Temperature",
            "last_collection": "Last Collection",
        }

        config = self.config
        discovery_dict = {}

        def make_name(key):
            return NAME_OVERRIDES.get(key, key.replace("_", " ").title())

        for entity in dict_data:

            if entity == "online":
                #homeassistant/binary_sensor/pi-data/srv-docker_online/config
                slug = f'{config["discovery_prefix"]}/binary_sensor/{config["app_prefix"]}/{dict_data["hostname"]}_{entity}/config'
                u_id = f'{config["app_prefix"]}_{dict_data["hostname"]}_{entity}'.replace("-","_")
                state_topic = f'{config["app_prefix"]}/{dict_data["hostname"]}/availability'

                data = {
                    "name": "Online",
                    "unique_id": u_id,
                    "state_topic": state_topic,
                    "payload_on": "online",
                    "payload_off": "offline",
                    "device_class": "connectivity",
                    "device": {
                        "identifiers": [ f'{config["app_prefix"]}_{dict_data["hostname"]}'.replace("-","_") ],
                        "name": dict_data["hostname"],
                        "manufacturer": f'{config["app_prefix"]}'.upper(),
                        "model": "Linux Host"
                    }
                }
                payload_json = json.dumps(data)
                discovery_dict[slug] = payload_json
                continue

            slug = f'{config["discovery_prefix"]}/sensor/{config["app_prefix"]}/{dict_data["hostname"]}_{entity}/config'
            u_id = f'{config["app_prefix"]}_{dict_data["hostname"]}_{entity}'.replace("-","_")
            state_topic = f'{config["app_prefix"]}/{dict_data["hostname"]}/state'
            availability_topic = f'{config["app_prefix"]}/{dict_data["hostname"]}/availability'

            data = {
                "name": make_name(entity),
                "unique_id": u_id,
                "state_topic": state_topic,
                "value_template": f"{{{{ value_json.{entity} }}}}",
            
                "availability_topic": availability_topic,
                "payload_available": "online",
                "payload_not_available": "offline",

                "device": {
                    "identifiers": [ f'{config["app_prefix"]}_{dict_data["hostname"]}'.replace("-","_") ],
                    "name": dict_data["hostname"],
                    "manufacturer": f'{config["app_prefix"]}'.upper(),
                    "model": "Linux Host"
                    }
            }
            payload_json = json.dumps(data)
            discovery_dict[slug] = payload_json

        return discovery_dict
            
        '''
            Discovery example:
            <discovery_prefix>/<component>/[node_id]/<object_id>/config

            homeassistant/sensor/pi-data/srv-docker_cpu_temp_deg/config
            {
                "name": "CPU Temp",
                "unique_id": "pi_data_srv_docker_cpu_temp_deg",
                "state_topic": "pi-data/srv-docker/state",
                "value_template": "{{ value_json.cpu_temp_deg }}",

                "availability_topic": "pi-data/srv-docker/availability",
                "payload_available": "online",
                "payload_not_available": "offline",

                "device": {
                    "identifiers": ["pi_data_srv_docker"],
                    "name": "srv-docker",
                    "manufacturer": "PI-DATA",
                    "model": "Linux Host"
                }
            }
        '''    

    def generate_packet_data(self):
        pass

    def transmit(self, tx_dict):
        pass
        for topic, payload in tx_dict.items():
            self.client.publish(topic, payload, retain=True)

    def connect(self):
        config = self.config

        if not config["enabled"]:
            print("MQTT disabled in config")
            return False

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=config["app_prefix"]
        )

        self.client.username_pw_set(
            username=config["user"],
            password=config["pass"]
        )

        result = self.client.connect(
            host=config["host"],
            port=config["port"],
            keepalive=60
        )

        self.client.loop_start()

        if result == mqtt.MQTT_ERR_SUCCESS:
            print("MQTT connect started")
            return True

        print(f"MQTT connect failed: {result}")
        return False

    def disconnect(self):
        if self.client is None:
            print("MQTT client not created")
            return

        self.client.disconnect()
        self.client.loop_stop()

        print("MQTT disconnected")
        self.client = None
