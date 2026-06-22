import paramiko
from datetime import datetime

class CollectOutput():
    def __init__(self, r_host, r_user, r_port, r_key, r_command):
        self.host_name = "Unresolved"
        self.host = r_host
        self.user = r_user
        self.port = r_port
        self.key = r_key
        self.command = r_command
        self.print_output = False
        self.online = False

        if self.print_output:
            print(f"{self.host}@{datetime.now()}: Host object created")

    def run_collection(self):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
        try:
            if self.print_output:
                print(f"{self.host}@{datetime.now()}: Attempting SSH connection")
            ssh.connect(hostname=self.host, port=self.port, username=self.user,key_filename=self.key,timeout=10)
            # Run the command, capture output, exit code, and any error data

            if self.print_output:
                print(f"{self.host}@{datetime.now()}: Running comand [{self.command}]")
            stdin, stdout, stderr = ssh.exec_command(self.command, timeout=10)

            output = stdout.read().decode("utf-8", errors="replace")
            error = stderr.read().decode("utf-8", errors="replace")
            exit_code = stdout.channel.recv_exit_status()

            # Check for clean command exec
            if exit_code !=0:
                raise RuntimeError(f"\n\nCommand failed with exit code {exit_code}: {error.strip()}\n\n")
                self.online = False

            if error.strip():
                print(f"Warning from server: {error.strip()}")
            
            if output:
                if self.print_output:
                    print(f"{self.host}@{datetime.now()}: Data Collected")
                self.online = True
                return output
            else:
                self.online = False
                return 0
        
        except TimeoutError:
            print(f"{self.host}@{datetime.now()}: Timeout Error on host")
            self.online = False
            return None
        
        except paramiko.ssh_exception.AuthenticationException:
            self.online = False
            print(f"{self.host}@{datetime.now()}: Authentication Error")
            return None
        
        except paramiko.ssh_exception.SSHException as e:
            self.online = False
            print(f"{self.host}@{datetime.now()}: SSH Error: {e}")
            return None
                
        finally:
            ssh.close()

