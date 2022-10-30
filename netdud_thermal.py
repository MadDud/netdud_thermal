#!/usr/bin/python3
import time
import board
import adafruit_dht
import json
import logging
from splunk_hec_handler import SplunkHecHandler
from datetime import datetime, timezone
# === config

sleep = 60.0

log_file = "/var/log/netdud_thermal.log"

hostname = "rpi01"

hec_server = ""
hec_key = ""
hec_port =

# ===

# Initial the dht device, with data pin connected to:
# dhtDevice = adafruit_dht.DHT22(board.D18)
# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

# configure splunk HEC
logger = logging.getLogger('SplunkHecHandlerExample')
logger.setLevel(logging.DEBUG)
splunk_handler = SplunkHecHandler(hec_server,hec_key, port=hec_port, proto='https', ssl_verify=False, source=hostname)
logger.addHandler(splunk_handler)

# configure logfile
logging.basicConfig(filename=log_file, format="%(message)s", level=logging.INFO)


while True:
    try:
        now = datetime.now(timezone.utc)
        current_time = now.strftime("%F %H:%M:%S%z")
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity

        data_set = {"sensor": hostname, "time":current_time, "temperature":temperature_c, "humidity":humidity }
        data_set_json = json.dumps(data_set)

        # send HEC to splunk
        #logger.info(data_set_json)

        # save to file
        logging.info(data_set_json)

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(3.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error
    except KeyboardInterrupt:
        dhtDevice.exit()
        print('exiting script')
    time.sleep(sleep)
