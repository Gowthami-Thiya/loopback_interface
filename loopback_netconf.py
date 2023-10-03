###########################################################################################################################################
# Author : Gowthami Thiyagarajan                                                                                                          #
# Created Date : 01.10.2023                                                                                                               #
# Description : This Application has been developed to connect with cisco sandbox and cofigure loopback and delete the same using netconf #
# Packages : Flask, ncclient, logging, xml                                                                                                      #
###########################################################################################################################################

import os
from ncclient import manager
from ncclient.xml_ import *
from flask import Flask, request, jsonify
import logging
import xml.etree.ElementTree as ET

# Creating a flask application
app = Flask(__name__)

# access github secrets
devicetype = os.environ.get('DEVICE_TYPE')
ip = os.environ.get('IP')
username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')

DRY_RUN = False

# Define device information
router = {
    f"ip":{ip},
    f"username":{username},
    f"password":{password},
    'port': 830,
}

# Module to connect with cisco sandbox
def connect_cisco_via_netconf():
    try:
        session = manager.connect(host=router['ip'], port=router['port'], username=router['username'],
                    password=router['password'],device_params={'name':'iosxr'} ,hostkey_verify=False)
        logging.basicConfig(filename='app.log',filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)
        logging.info('Admin logged in')
        return session
        
    except Exception as e:
        error=f"unable to connect to cisco via netconf due to this error : {e}"
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(error)
        return {'message': str(e)}, 500

# Module to create Loopback in cisco device
def netconf_config_loopback(interface_number,description,ip_address,subnet_mask):
    session=connect_cisco_via_netconf()

    # Define the XML payload for configuring the loopback interface
    try:
        configure_loopback = """
        <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
        <interfaces xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
            <interface>
            <name>Loopback{interface_number}</name>
            <interface-name>Loopback{interface_number}</interface-name>
            <description>{description}</description>
            <interface-type>software-loopback</interface-type>
            <shutdown>false</shutdown>
            <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
                <addresses>
                <primary>
                    <address>{ip_address}</address>
                    <netmask>{subnet_mask}</netmask>
                </primary>
                </addresses>
            </ipv4-network>
            </interface>
        </interfaces>
        </config>
        """
        configure_loopback = configure_loopback.format(
                        interface_number=interface_number,
                        description=description,
                        ip_address=ip_address,
                        subnet_mask=subnet_mask
                    )
        # configure the loopback interface
        response = session.edit_config(target='running', config=configure_loopback)

        if '<ok/>' in ET.tostring(response.data):
            logging.basicConfig(filename='app.log',filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)
            logging.info('Loopback interface configured successfully.')
            return response
        else:
            logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
            logging.info('Failed to configure loopback interface.')
            return {'message': 'Failed to configure loopback interface'}, 500
        
    except Exception as error:
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(error)
        e=f'unable to configure interface due to this error {str(error)}'
        return {'message': e}, 500

# Module to delete the created loopback
def delete_loopback_via_netconf(interface_number):
    session=connect_cisco_via_netconf()

    try:
        delete_loopback = """
        <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
        <interfaces xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
            <interface operation="delete">
            <name>Loopback{interface_number}</name>
            </interface>
        </interfaces>
        </config>
        """
        delete_loopback = delete_loopback.format(
                        interface_number=interface_number
                    )
        response = session.edit_config(target='running', config=delete_loopback)

        if '<ok/>' in ET.tostring(response.data):
            logging.basicConfig(filename='app.log',filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)
            logging.info('Loopback interface deleted successfully.')
            return response
        else:
            logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
            logging.info('Failed to delete configured loopback interface.')
            return {'message': 'Failed to delete configured loopback interface'}, 500
    except Exception as error:
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(error)
        e=f'unable to delete interface due to this error {str(error)}'
        return {'message': e}, 500
    
# Module to list configured interface
def show_loopback_via_netconf(interface_number):
    session=connect_cisco_via_netconf(interface_number)

    try:
        show_loopback = """
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <interfaces xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
                <interface>
                    <name>Loopback{interface_number}</name>
                </interface>
            </interfaces>
        </filter>
        """
        show_loopback = show_loopback.format(
                        interface_number=interface_number
                    )
        response = session.get_config(source='running', filter=show_loopback)

        output=ET.tostring(response.data, encoding='unicode')
        logging.basicConfig(filename='app.log',filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)
        logging.info('Loopback interface deleted successfully.')
        return output
    
    except Exception as error:
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(error)
        e=f'unable to show configured interface due to this error {str(error)}'
        return {'message': e }, 500
   
# Route to configure loopback via netconf with the passed payload
@app.route('/netconf_loopback_configuration', methods=['POST'])
def netconf_loopback_configuration():
    payload = request.json
    ipaddress = payload.get('loopback_ip')
    interface_number = payload.get('interface_number')
    desc=payload.get('description')
    subnet_mask=payload.get('subnet')

    response = netconf_config_loopback(interface_number,desc,ipaddress,subnet_mask)
    return jsonify({'response': response})

# Route to delete loopback via netconf with the passed payload
@app.route('/netconf_delete_loopback', methods=['POST'])
def netconf_delete_loopback():
    payload = request.json
    interface_number = payload.get('interface_number')

    response = delete_loopback_via_netconf(interface_number)
    return jsonify({'response': response})

# Route to show loopback via netconf with the passed payload
@app.route('/netconf_show_loopback', methods=['POST'])
def netconf_show_loopback():
    payload = request.json
    interface_number = payload.get('interface_number')

    response = show_loopback_via_netconf(interface_number)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)