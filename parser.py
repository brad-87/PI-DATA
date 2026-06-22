from datetime import datetime 

class ParseData():
    
    def __init__(self):
        self.sections = {}

        # HOSTNAMECTL
        self.hostname = ""
        self.architecture = ""
        self.kernel = ""

        # OS_RELEASE
        self.os_prettyname = ""

        # UPTIME_PRETTY
        self.uptime = ""
        
        # MEM_FREE
        self.mem_total = ""
        self.mem_available = ""
        self.mem_used = ""

        # DISK_FREE
        self.disk_total = ""
        self.disk_free = ""
        self.disk_used = ""

        # IP_ROUTE_GET
        self.nw_ip = ""
        self.nw_interface = ""

        # NET_DEV
        self.nw_tx = ""
        self.nw_rx = ""
        self.nw_error = ""
        self.nw_drop = ""

        # LOAD_AVG
        self.load_avg = ""

        # CPU_TEMP
        self.cpu_temp = ""

    ## DATA ENTRY POINT
    def parse_data(self, raw_data):
        self.sections = self.parse_sections(raw_data)
        try:
            self.parse_hostnamectl()
            self.parse_os()
            self.parse_network()
            self.parse_uptime()
            self.parse_cpu()
            self.parse_memory()
            self.parse_storage()
        except:
            print("General Parsing Error")
    
    def parse_to_dict(self):
        output = {}

        output["hostname"] = self.hostname
        output["architecture"] = self.architecture
        output["kernel"] = self.kernel

        output["os"] = self.os_prettyname

        output["uptime"] = self.uptime
        
        output["mem_total_gb"] = float(self.mem_total)
        output["mem_available_gb"] = float(self.mem_available)
        output["mem_used_gb"] = float(self.mem_used)
        
        output["disk_total_gb"] = float(self.disk_total)
        output["disk_free_gb"] = float(self.disk_free)
        output["disk_used_gb"] = float(self.disk_used)
        
        output["nw_ip"] = self.nw_ip
        output["nw_interface"] = self.nw_interface

        output["nw_total_tx_mb"] = int(self.nw_tx)
        output["nw_total_rx_mb"] = int(self.nw_rx)
        output["nw_total_error_pkt"] = int(self.nw_error)
        output["nw_total_drop_pkt"] = int(self.nw_drop)

        output["load_avg_percent"] = float(self.load_avg)

        output["cpu_temp_deg"] = float(self.cpu_temp)

        output["last_collection"] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        return output

    def parse_storage(self):
        data = self.sections["DISK_ROOT_B"]
        storage = []
        # Filesystem        1B-blocks       Used        Avail Use% Mounted on
        # /dev/mmcblk0p2 251311718400 4133232640 236909363200   2% /
        #      0               1           2           3         4    5
        if data:
            data = data[1].split(" ")
            for chunk in data:
                if chunk:
                    storage.append(chunk)
            self.disk_total = f"{(int(storage[1]) / 1024 **3):.2f}"
            self.disk_used = f"{(int(storage[2]) / 1024 **3):.2f}"
            self.disk_free = f"{(int(storage[3]) / 1024 **3):.2f}"
        else:
            self.disk_total = "Unavailable"
            self.disk_used = "Unavailable"
            self.disk_free = "Unavailable"

    def parse_memory(self):

        #               total        used        free      shared  buff/cache   available
        #Mem:      1922924544   746508288   191365120     1441792  1155059712  1176416256
        # 0              1            2           3           4         5          6

        mem_raw = self.sections["MEMORY_FREE_B"]
        mem = []

        if mem_raw:
            mem_raw = mem_raw[1].split(" ")
            for chunk in mem_raw:
                if chunk:
                    mem.append(chunk)

            self.mem_total = f"{float(int(mem[1]) / 1024 ** 3):.2f}"
            self.mem_available = f"{float(int(mem[6]) / 1024 ** 3):.2f}"
            self.mem_used = f"{float(int(mem[2]) / 1024 ** 3):.2f}"
        else:
            self.mem_total = "Unavailable"
            self.mem_available = "Unavailable"
            self.mem_used = "Unavailable"
            
    def parse_cpu(self):
        temp = self.sections["CPU_TEMP"]
        avg = self.sections["LOADAVG"]
        cores = self.sections["CPU_CORES"]


        if temp:
            self.cpu_temp = int(temp[0]) / 1000
            self.cpu_temp = f"{self.cpu_temp:.1f}"
        else:
            self.cpu_temp = "Unavailable"
        
        if avg:
            avg = avg[0].split(" ")
            self.load_avg = f"{(float(avg[1]) / int(cores[0]) * 100):.1f}"
        else:
            self.load_avg = "Unavailable"

    def parse_uptime(self):
        uptime = self.sections["UPTIME_PRETTY"]
        if uptime:
            self.uptime = uptime[0]
        else:
            self.uptime = "Unavailable"

    def parse_network(self):
        # Inter-|   Receive                                                              |  Transmit
        #  face |  bytes     packets   errs   drop   fifo   frame compressed multicast   |bytes      packets   errs  drop fifo colls carrier compressed
        #  eth0 '144621465', '747611', '0', '257833', '0',   '0',    '0',     '141805', '24583273',  '79578',   '0', '0', '0', '0',    '0',     '0']
        #   0      1            2       3      4       5      6       7           8         9          10       11   12    13   14      15       16

        ip_data = self.sections.get("IP_ROUTE_GET")
                
        if ip_data:
            ip_data = ip_data[0]
            ip_data = ip_data.split(" ")
            self.nw_ip = ip_data[6]
            self.nw_interface = ip_data[4]
        else:
            self.nw_ip = "Unavailable"
            self.nw_interface = "Unavailable" 

        ip_data = self.sections.get("NETWORK_DEV")
        if ip_data:
            for entry in ip_data:
                if self.nw_interface in entry:
                    raw_line_data = entry.split(" ")
                    
                    line_data = []
                    for item in raw_line_data:
                        if item:
                            line_data.append(item)
                    self.nw_rx = f"{int(int(line_data[1]) / 1024 ** 2)}"
                    self.nw_tx = f"{int(int(line_data[9]) / 1024 ** 2)}"
                    self.nw_error = int(line_data[3]) + int(line_data[11])
                    self.nw_drop = int(line_data[4]) + int(line_data[12])
        else:
            self.nw_tx = "Unavailable"
            self.nw_rx = "Unavailable"
            self.nw_error = "Unavailable"
            self.nw_drop = "Unavailable"    

    def parse_os(self):
        os_data = self.sections.get("OS_RELEASE")
        if os_data:
            self.os_prettyname = os_data[0]
            self.os_prettyname = self.os_prettyname.split("=")[1]
            self.os_prettyname = self.os_prettyname.strip("\"")
        else:
            self.os_prettyname = "Unavailable"

    def parse_hostnamectl(self):
        # ['Static hostname: srv-docker', 'Icon name: computer', 'Machine ID: b2bf83b6f8ec4ee0938e7d47db7d33c6', 'Boot ID: 52f437f4bd7c4ad2b268e10bea95bfcf', 'Operating System: Ubuntu 26.04 LTS', 'Kernel: Linux 7.0.0-1011-raspi', 'Architecture: arm64', 'Hardware Serial: 100000004e5dd0b1']
        #          0                              1                            2                                                   3                                               4                             5                           6                           7
        hostnamectl_data = self.sections.get("HOSTNAMECTL")
        
        if hostnamectl_data:
            hn = hostnamectl_data[0].split(":")
            self.hostname = hn[1]
            self.hostname = self.hostname.strip()

            k = hostnamectl_data[5].split(":")
            self.kernel = k[1]
            self.kernel = self.kernel.strip()

            a = hostnamectl_data[6].split(":")
            self.architecture = a[1]
            self.architecture = self.architecture.strip()
        else:
            self.hostname = "Unavailable"
            self.kernel = "Unavailable"
            self.kernel = "Unavailable"

    def parse_sections(self, input_data):
        output = {}

        current_section = None
        current_data = []

        for entry in input_data:
            if entry:
                if entry.startswith("==="):

                    if current_section:
                        output[current_section] = current_data
                        current_data =[]
                        current_section = entry.strip(" =")
                    else:
                        current_section = entry.strip(" =")

                else:
                    current_data.append(entry)

        if current_section:
            output[current_section] = current_data

        return output

    def print_values(self):
        print("System")
        print(f"\tHost name: {self.hostname}")
        print(f"\tArchitecture: {self.architecture}")
        print(f"\tKernel: {self.kernel}")
        print(f"\tOS: {self.os_prettyname}")
        print(f"\tUptime: {self.uptime}")
        print(f"\n\tMemory total: {self.mem_total}gb")
        print(f"\tMemory used: {self.mem_used}gb")
        print(f"\tMemory avail: {self.mem_available}gb")
        print(f"\n\tDisk total: {self.disk_total}gb")
        print(f"\tDisk used: {self.disk_used}gb")
        print(f"\tDisk free: {self.disk_free}gb\n")


        print("Network")
        print(f"\tInterface: {self.nw_interface}")
        print(f"\tIP: {self.nw_ip}")
        print(f"\n\tTx: {self.nw_tx}mb")
        print(f"\tRx: {self.nw_rx}mb")
        print(f"\tErr: {self.nw_error}")
        print(f"\tDrop: {self.nw_drop}\n")

        print("CPU")
        print(f"\tAVG %(5min): {self.load_avg}%")
        print(f"\tTemp: {self.cpu_temp}deg")
