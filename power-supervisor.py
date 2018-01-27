#!/usr/bin/python

import sys
import argparse
import time
import threading
import os
import logging
import power_reader
from argparse import RawTextHelpFormatter

scriptLocation = os.path.dirname(os.path.realpath(__file__))

def rebootThread(waitTime, stop_event):
    logging.debug('Starting reboot thread, booting in ' + str(waitTime) + ' seconds if no change in conditions...')
    stop_event.wait(waitTime)
    if(stop_event.isSet()):
        logging.warning('Critical thread Reboot cancelled')
        return
    logging.warning('Booting...')
    os.system('reboot --reboot')


parser = argparse.ArgumentParser(description='\
This script is used to check if GPU cards are spending "enough" power.\n\
If not, reboot is tried as recovery action.\n',
formatter_class=RawTextHelpFormatter)

parser.add_argument("--interval", help='How often(minutes) to check the power consumption. default 1', default=1, type=int)
parser.add_argument("--wait_reboot", help='How long to wait before rebooting after problems detected default 10', default=10, type=int)
parser.add_argument("--total_power", help='Minimum acceptable total power consumption(W) default 1000', default=1000, type=int)
parser.add_argument("--one_gpu_power", help='Minimum acceptable total power consumption(W) in one GPU(0=disbled), default 0', default=0, type=int)
parser.add_argument("-v", "--verbose", action="store_true", help="Print debug logs")
parser.add_argument("-l", "--log_to_file", action="store_true", help="Print to file, instead of stdout")

args = parser.parse_args()
debug = args.verbose
interval = args.interval
waitReboot = args.wait_reboot
totalPower = args.total_power
oneGpuPower = args.one_gpu_power
logToFile = args.log_to_file

loggingLevel=None
if(debug):
    loggingLevel = logging.DEBUG
else:
    loggingLevel = logging.INFO

if(logToFile):
    logging.basicConfig(
        filename=scriptLocation + '/' + os.path.splitext(os.path.basename(__file__))[0] + '.log',
        level=loggingLevel,
        format='%(asctime)s %(message)s')
else:
    logging.basicConfig(level=loggingLevel)

logging.info('Checking power consumption in every ' + str(interval) + ' minutes')
logging.info('Booting computer if total power is below ' + str(totalPower) + 'W')
if(oneGpuPower):
    logging.info('Booting computer if one GPU has power below ' + str(oneGpuPower) + 'W')

reboot_thread_stop = None
reboot_thread = None

def cancelRebootThread():
    global reboot_thread
    global reboot_thread_stop
    if(reboot_thread and reboot_thread.isAlive()):
        reboot_thread_stop.set()

def startRebootThread():
    global reboot_thread
    global reboot_thread_stop
    if(reboot_thread and reboot_thread.isAlive()):
        logging.debug('Reboot thread seems to be running already')
    else:
        rebootTimeSeconds = waitReboot*60
        reboot_thread_stop = threading.Event()
        reboot_thread = threading.Thread(target=rebootThread, args=(rebootTimeSeconds, reboot_thread_stop))
        reboot_thread.start()

try:
    while(1):
        error, gpuPowerArray = power_reader.getGpuPowerArray()
        totalPowerUsed = 0
        oneGpuProblem = False
        totalProblem = False
        if(error != 0):
            logging.error('Could not read GPU powers, stack might be stuck')
            startRebootThread()
        else:
            for gpuPower in gpuPowerArray:
                if(oneGpuPower > 0 and gpuPower < oneGpuPower):
                    logging.warning('One GPU is using too little power (' + str(gpuPower) + 'W)')
                    oneGpuProblem = True
                totalPowerUsed += gpuPower
            logging.debug('Total power: ' + str(totalPowerUsed))
            if(totalPowerUsed < totalPower):
                logging.warning('total power usage is too little (' + str(totalPowerUsed) + 'W)')
                totalProblem = True
            if(totalProblem or oneGpuProblem):
                startRebootThread()
            else:
                cancelRebootThread()
        time.sleep(interval*60)

except KeyboardInterrupt as e:
    cancelRebootThread()
    raise e