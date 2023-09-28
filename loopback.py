from netmiko import ConnectHandler
import logging
login_configs = {
    "device_type":"cisco_xr",
    "ip":"sandbox-iosxr-1.cisco.com",
    "username":"admin",
    "password":"C1sco12345",
    "port":22,
    "verbose":True,
}
def connect_ciscobox():
    try:
        connectivity=ConnectHandler(**login_configs)
        connectivity.enable()
        logging.basicConfig(filename='app.log',filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)
        logging.info('Admin logged in')
    except Exception as e:
        error=f"unable to connect due to this error : {e}"
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(error)
    return connectivity

def show_intefaces():
    try:
        connectivity=connect_ciscobox()
        com="show interfaces"
        output=connectivity.send_command(com)
        logging.basicConfig(filename='app.log',filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)
        logging.info('listed available interfaces')
    except Exception as e:
        error=f"unable to connect due to this error : {e}"
        output = error
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(error)
    return output

def create_loopback():
    try:
        connectivity=connect_ciscobox()
        command= [
            "interface Loopback50",
            "description test loopback config"
            "ip address 10.0.0.1/28",
            "commit",
            "exit"
        ]
        response=connectivity.send_config_set(command)
        logging.basicConfig(filename='app.log',filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)
        logging.info('Loopback configured succssfully')
        print(response)
    except Exception as e:
        error=f"unable to connect due to this error : {e}"
        response=error
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(error)
    return response

def delete_loopback():
    try:
        connectivity=connect_ciscobox()
        delete_interface=["no interface Loopback50",
            "commit",
            "exit"]
        response=connectivity.send_config_set(delete_interface)
        print(response)
        logging.basicConfig(filename='app.log',filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)
        logging.info('Loopback deleted successfully')
    except Exception as e:
        error=f"unable to connect due to this error : {e}"
        response=error
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(error)
    return response

display=show_intefaces()
print(display)
configinterface=create_loopback()
print(configinterface)
deleteinterface=delete_loopback()
print(deleteinterface)
