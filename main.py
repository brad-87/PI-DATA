from parser import ParseData
from collector import CollectOutput
from config import ReadConfig
import threading, time

config = ReadConfig("my_config.yaml")

host_objects = []
for host_name, option in config.hosts.items():
    obj = CollectOutput(option["ip"], option["user"], int(option["port"]), option["key"], option["command"])
    obj.print_output = config.collector_print_output
    host_objects.append(obj)

def run_cycle():
    
    try:
        print("----------------------------------------------------------------------------------------------------")
        for host in host_objects:
            
            print(f"\nCollecting from -> Host: [{host.host}]")
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
            print(output)
    
    finally:
        schedule_next()


def schedule_next():
    timer = threading.Timer(config.collector_poll_interval, run_cycle)
    timer.daemon = True
    timer.start()

run_cycle()

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nKeyboard interrupt received. Exiting...")
