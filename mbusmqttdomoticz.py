# device type sharky 775 GigaJoule HeatMeter
# the choice of virtual sensor is yours i only provided some basic info to get you started
# install libmbus first https://github.com/rscada/libmbus
# for more info go to https://the78mole.de/taking-your-m-bus-online-with-mqtt/ for more information on mbus connection
# sidenote this is not a domoticz plugin but a script to run the times you need it to e.g. 5 minutes
# for every 5 minutes use: crontab -e
# */5 * * * * python3 /path/to/file/mbusmqttdomoticz.py

import json
import subprocess
import paho.mqtt.client as mqtt
cmd = "mbus-serial-request-data -b 2400 /dev/ttyUSB0 0 | xq ."

output = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
data = json.loads(output)
mbus_data = data.get("MBusData", {})
slave_information = mbus_data.get("SlaveInformation", {})
data_records = mbus_data.get("DataRecord", [])

client = mqtt.Client()
client.connect("192.168.x.x", 1883) # use your mqtt server ( i dont use logins on my home network)

for i, record in enumerate(data_records):
    id = record.get("@id", str(i)) # @id is field with data (not all fields are needed only below id's)
    value = record.get("Value", "") # Value = field with the data
    if value:
        value = float(value)
        if id == "0": # GJ total (Create general counter incremental virtual sensor and change the idx number)
            value /= 1000 #convert from MJ to GJ
            message = '{{"idx":1190,"nvalue":0,"svalue":"{value} Gj"}}'.format(idx=id, value=value)
                
        elif id == "3": # total volume m3 (create Waterflow or custom virtual sensor and change te idx number)
            value /= 1000
            message = '{{"idx":1188,"nvalue":0,"svalue":"{value} m3"}}'.format(idx=id, value=value)
                
        elif id == "4": # power in Watt (create general, Kwh or custom sensor and change the idx number)
            value /= 1000
            message = '{{"idx":1161,"nvalue":0,"svalue":"{value} W"}}'.format(idx=id, value=value)
                
        elif id == "5": # Volume Flow (create Waterflow or custom virtual sensor and change te idx number)
            value /= 100
            message = '{{"idx":1164,"nvalue":0,"svalue":"{value} m3/h"}}'.format(idx=id, value=value)
                
        elif id == "6": # Flow temp (create LaCrosse TX3 virtual temp sensor and change te idx number)
            value /= 10
            message = '{{"idx":1166,"nvalue":0,"svalue":"{value} C"}}'.format(idx=id, value=value)
                
        elif id == "7": # Return temp (create LaCrosse TX3 virtual temp sensor and change te idx number)
            value /= 10
            message = '{{"idx":1167,"nvalue":0,"svalue":"{value} C"}}'.format(idx=id, value=value)
                
        elif id == "8": # temp difference (create LaCrosse TX3 virtual temp sensor and change te idx number)
            value /= 10
            message = '{{"idx":1168,"nvalue":0,"svalue":"{value} C"}}'.format(idx=id, value=value)
        
        else:
            continue
        # Publish the message to the "domoticz/in" topic
        client.publish("domoticz/in", message)
        print("Data sent to domoticz/in for idx {}: {}".format(id, message)) # console output when run manualy to test

# Disconnect from the MQTT server
client.disconnect()
