from pathlib import Path
import yaml

class ReadConfig():
    def __init__(self, f_path="config.yaml"):

        self.hosts = {}
        self.collector_en = None
        self.collector_ssh_timeout = None
        self.collector_poll_interval = None
        self.collector_print_output = None

        self.mqtt_en = None
        self.mqtt_discovery = None
        self.mqtt_print_output = None
        self.mqtt_server_ip = None
        self.mqtt_server_port = None
        self.mqtt_server_user = None
        self.mqtt_server_pass = None

        self.f_path = Path(f_path)
        self.config = self.read_config()
        self.parse_config()


    def read_config(self):
        if not self.f_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.f_path}")
        
        with self.f_path.open("r", encoding="utf-8") as f:
            print(f"Config file read : {self.f_path}")
            return yaml.safe_load(f)


    def parse_config(self):
        for heading, contents in self.config.items():
            if heading == "host":
                for host_name, host_config in contents.items():
                    self.hosts[host_name] = host_config
                    

            elif heading == "collector":
                r_collector = contents

            elif heading == "mqtt":
                r_mqtt = contents

            else:
                print(f"Config Warning: Ignoring unrelated section - [ {heading} ]")
        
        for entity in r_collector:
            if entity == "enanled":
                self.collector_en = r_collector[entity]
            elif entity == "ssh_timeout":
                self.collector_ssh_timeout = r_collector[entity]
            elif entity == "poll_interval":
                self.collector_poll_interval = r_collector[entity]
            elif entity == "print_output":
                self.collector_print_output = r_collector[entity]
            else:
                continue

        for entity in r_mqtt:
            if entity == "enanled":
                self.mqtt_en = r_mqtt[entity]
            elif entity == "discovery":
                self.mqtt_discovery = r_mqtt[entity]
            elif entity == "print_output":
                self.mqtt_print_output = r_mqtt[entity]
            elif entity == "host":
                self.mqtt_server_ip = r_mqtt[entity]
            elif entity == "port":
                self.mqtt_server_port = r_mqtt[entity]
            elif entity == "user":
                self.mqtt_server_user = r_mqtt[entity]
            elif entity == "pass":
                self.mqtt_server_pass = r_mqtt[entity]
            else:
                continue


    def print_config(self):
        print(f"Config headings in {self.f_path}")

        for heading, contents in self.config.items():
            print(f"\n[ {heading} ]")
            for key,val in contents.items():
                print(f"\tⱶ-→ {key} : {val}")
