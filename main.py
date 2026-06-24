from parser import ParseData
from collector import CollectOutput
from mqtt import MqttClient
from config import ReadConfig
import threading, time

print("Program Init")
config = ReadConfig()

host_objects = []
for host_name, option in config.hosts.items():
    obj = CollectOutput(option["ip"], option["user"], int(option["port"]), option["key"], option["command"])
    obj.print_output = config.collector_print_output
    host_objects.append(obj)

mqtt = MqttClient(config.mqtt_config)


if config.mqtt_en:
    mqtt.connect()

run_once = False
if config.mqtt_discovery:
    run_once = True

if config.mqtt_print_output:
    mqtt.print_output = True

print("Begin Main()")

def run_cycle():
    global run_once
    try:
        print("-------------- Collection Cycle: Start -----------------")
        for host in host_objects:
            
            print(f"Collecting from -> Host: [{host.host}]")
            data = host.run_collection()
            
            contents = []
            output = {}
            if data:
                data = data.split("\n")  
                for entry in data:
                    contents.append(entry.strip())
                
                pd = ParseData()
                pd.parse_data(contents)
                
                output = pd.parse_to_dict()
                host.host_name = output["hostname"]
            
            if output:
                output["online"] = host.online
            else:
                output["host_name"] = host.host_name
                output["host"] = host.host
                output["online"] = host.online
            
            if config.mqtt_en:
                if run_once:
                    mqtt.transmit(mqtt.generate_discovery_data(output))
                mqtt.transmit(mqtt.generate_state_packet(output))
                mqtt.transmit(mqtt.generate_availability_packet(output))
        if run_once:
            run_once = False




        
        print("-------------- Collection Cycle: Complete --------------\n")
    
    finally:
        schedule_next()


def schedule_next():
    timer = threading.Timer(config.collector_poll_interval, run_cycle)
    timer.daemon = True
    timer.start()




#Program start
run_cycle()
try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nKeyboard interrupt received. Exiting...")
    
    if config.mqtt_en:
        mqtt.disconnect()
