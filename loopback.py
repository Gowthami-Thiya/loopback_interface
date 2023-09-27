from netmiko import ConnectHandler
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
        command= "ip?"
        output=connectivity.send_config_set(command)
        connectivity.disconnect()
    except Exception as e:
        output="Unexpected error occured : {str(e)}"
    return output
output=connect_ciscobox()
print(output)