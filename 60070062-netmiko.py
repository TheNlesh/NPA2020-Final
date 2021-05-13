from netmiko import NetMikoAuthenticationException, NetmikoAuthError, NetmikoTimeoutError, NetMikoTimeoutException
from netmiko import ConnectHandler
from secret import *

class Manager:
    def __init__(self, ip, username, password, device_type):
        self.__ip = ip
        self.__username = username
        self.__password = password
        self.__device_type = device_type

    def create_connection(self):
        """ Create connection to device """
        device = {
            'ip' : self.__ip,
            'username' : self.__username,
            'password' : self.__password,
            'device_type' : self.__device_type
        }
        try:
            connection = ConnectHandler(**device)
        except (NetMikoTimeoutException, NetmikoTimeoutError):
            print("error: connection timeout to device = " + device['ip'])
            return False
        except (NetmikoAuthError, NetMikoAuthenticationException):
            print("error: Authentication failed to device = " + device['ip'])
            return False
        return connection

    def save_config(self):
        """ Save configuration into flash """
        connection = self.create_connection()
        if not connection:
            return False
        try:
            wr = connection.send_command(command_string="write mem", expect_string=r"#")
        except Exception as e:
            return False
        else:
            return True
        finally:
            connection.disconnect()


    def create_loopback(self, number, ip, mask):
        """ Create loopback from loopback number, ip, and subnet mask """
        connection = self.create_connection()
        if not connection:
            return False
        try:
            loopbackcmd = ["conf t", "int lo{}".format(str(number)), "ip add {} {}".format(ip, mask), "end"]
            for cmd in loopbackcmd:
                connection.send_command(cmd, expect_string=r"#")
        except Exception as e:
            return False
        else:
            return True
        finally:
            connection.disconnect()

    def show_interface(self):
        connection = self.create_connection()
        if not connection:
            return False

        try:
            interfaces = connection.send_command("sh ip int br", expect_string=r"#")
        except Exception as e:
            return False
        else:
            return interfaces
        finally:
            connection.disconnect()

if __name__ == '__main__':
    manageObj = Manager(ip=host, username=username, password=password, device_type=device_type)
    manageObj.create_loopback(number="60070062", ip="192.168.1.1", mask="255.255.255.0")
    manageObj.save_config()
    print(manageObj.show_interface())