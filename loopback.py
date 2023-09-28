#############################################################################################################################
# Author : Gowthami Thiyagarajan                                                                                            #
# Created Date : 27.09.2023                                                                                                 #
# Description : This Application has been developed to connect with cisco sandbox and cofigure loopback and delete the same #
# Packages : Flask, netmiko, logging                                                                                        #
#############################################################################################################################

# Import required packages
from flask import Flask, request, jsonify
from netmiko import ConnectHandler
import logging

# Creating a flask application
app = Flask(__name__)

# Connection string
login_configs = {
    "device_type":"cisco_xr",
    "ip":"sandbox-iosxr-1.cisco.com",
    "username":"admin",
    "password":"C1sco12345",
    "port":22,
    "verbose":True,
}

# Module to connect with cisco sandbox
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

# Module to list available interfaces
def show_intefaces():
    try:
        connectivity=connect_ciscobox()

        # command to list interfaces
        com="show interfaces"
        output=connectivity.send_command(com)
        connectivity.disconnect()
        logging.basicConfig(filename='app.log',filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)
        logging.info('listed available interfaces')
    except Exception as e:
        error=f"unable to connect due to this error : {e}"
        output = error
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(error)
    return output

# Module to create Loopback in cisco device
def create_loopback(interface_number,desc,ipaddress):
    try:
        connectivity=connect_ciscobox()

        # commands to create loopback
        command= [
            f"interface {interface_number}",
            f"description {desc}"
            f"ip address {ipaddress}",
            "commit",
            "exit"
        ]
        response=connectivity.send_config_set(command)
        connectivity.disconnect()
        logging.basicConfig(filename='app.log',filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)
        logging.info('Loopback configured succssfully')
        return {'message': 'Configuration done successfully:', 'response': response}, 200
    except Exception as e:
        error=f"unable to connect due to this error : {e}"
        response=error
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(error)
        return {'message': str(e)}, 500
    
# Module to delete the created loopback
def delete_loopback(interface_number):
    try:
        connectivity=connect_ciscobox()
        
        # Commands to delete the loopback
        delete_interface=[f"no interface {interface_number}",
            "commit",
            "exit"]
        response=connectivity.send_config_set(delete_interface)
        print(response)
        logging.basicConfig(filename='app.log',filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)
        logging.info('Loopback deleted successfully')
        return {'message': 'Loopback Configuration deleted successfully:', 'response': response}, 200
    except Exception as e:
        error=f"unable to connect due to this error : {e}"
        response=error
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(error)
        return {'message': str(e)}, 500

###############
#   Enpoints  #
###############

# Route to configure loopback with the passed payload
@app.route('/loopback_configuration', methods=['POST'])
def loopback_configuration():
    payload = request.json
    #device_params=connectionstring(data)
    ipaddress = payload.get('loopback_ip')
    interface_number = payload.get('interface_number')
    desc=payload.get('description')
    
    response = create_loopback(interface_number,desc,ipaddress)

    return jsonify({'response': response})

# Route to List all the interfaces
@app.route('/list_interfaces', methods=['GET'])
def list_interfaces():
    
    result = show_intefaces()

    return jsonify({'result': result})

# Route to delete the loopback based on passed payload
@app.route('/remove_loopback', methods=['POST'])
def remove_loopback():
    payload = request.json
    #device_params=connectionstring(data)
    interface_number = payload.get('interface_number')
    
    response = delete_loopback(interface_number)

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
