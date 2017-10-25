
#!/usr/bin/python

import requests, sys, argparse, traceback, time, threading, os, logging
from argparse import RawTextHelpFormatter

NANOPOOL_HASHRATE_TEMPLATE = 'https://api.nanopool.org/v1/eth/hashrate/$ADDRESS$'

scriptLocation = os.path.dirname(os.path.realpath(__file__))

def checkHashRate():
    logging.debug('checkHashRate()')
    err = 0
    try:
        r = requests.get(NANOPOOL_HASHRATE_TEMPLATE.replace('$ADDRESS$', nanoPoolHashRateAddress))
        if(r.status_code >= 400):
            logging.warning('Getting HashRate failed, nanopool maybe broken or wrong address?. status_code:' + str(r.status_code))
            return 3
        logging.debug('Response: ' + r.text)
        status = r.json()['status']
        hashRate = r.json()['data']
        if(status == True):
            if(hashRate >= hashRateLowerLimit):
                logging.debug('Hash rate ok(' + str(hashRate) + ')')
                return 0
            else:
                logging.warning('Hash rate is smaller(' + str(hashRate)  + ') than wanted(' + str(hashRateLowerLimit) + '). This might cause recovery boot soonish.')
                return 1
        else:
            logging.warning('TODO: Status is not true. No freaking idea what that means? I guess we report error.')
            return 1
    except Exception as e:
        logging.warning('Getting HashRate failed, nanopool, internet connection or this code maybe broken?')
        logging.warning("Unexpected error:" + str(traceback.format_exc()))
        return 2
    return err

def rebootThread(waitTime, stop_event):
    logging.debug('Starting reboot thread, booting in ' + str(waitTime) + ' seconds if no change in conditions...')
    stop_event.wait(waitTime)
    if(stop_event.isSet()):
        logging.warning('Critical thread Reboot cancelled')
        return
    logging.warning('Booting...')
    os.system('reboot --reboot')


parser = argparse.ArgumentParser(description='This script is used to check if \
Hash rate in nanopool is still ok. If not, reboot is tried as recovery action.\
\n\
Usage:\n\
blaa',
formatter_class=RawTextHelpFormatter)

parser.add_argument("--interval", help='How often(minutes) to check the hash rate(it seems that it updates in every 10 minutes)', default=5, type=int)
parser.add_argument("--serious_boot_interval", help='How fast to reboot after serious problems are detected', default=20, type=int)
parser.add_argument("--unsure_boot_interval", help='How fast to reboot after unsure problems are detected', default=60, type=int)
parser.add_argument("--hash_rate_limit", help='Hash rate supervision limit(Mh/s', default=1, type=int)
parser.add_argument("-v", "--verbose", action="store_true", help="Print debug logs")
parser.add_argument("-l", "--log_to_file", action="store_true", help="Print to file, instead of stdout")
parser.add_argument("address", help='ethereum address')

args = parser.parse_args()
debug = args.verbose
nanoPoolHashRateAddress = args.address
interval = args.interval
seriousBootInterval = args.serious_boot_interval
unsureBootInterval = args.unsure_boot_interval
hashRateLowerLimit = args.hash_rate_limit
logToFile = args.log_to_file

loggingLevel=None
if(debug):
    loggingLevel = logging.DEBUG
else:
    loggingLevel = logging.INFO

if(logToFile):
    logging.basicConfig(filename=scriptLocation + '/' + os.path.splitext(__file__)[0] + '.log', level=loggingLevel)
else:
    logging.basicConfig(level=loggingLevel)

logging.info('Supervising account: ' + nanoPoolHashRateAddress)
logging.info('Checking hash rate in every ' + str(interval) + ' minutes')
logging.info('Booting computer if hash rate is below ' + str(hashRateLowerLimit))
logging.info('Booting computer after ' + str(seriousBootInterval) + ' minutes if serious problems are detected and after ' + str(unsureBootInterval) + ' minutes if unsure problems are detected.')

serious_thread_stop = None
serious_thread = None
unsure_thread_stop = None
unsure_thread = None

while(1):
    ret = checkHashRate()
    if(ret == 0):
        logging.debug('All OK')
        if(serious_thread and serious_thread.isAlive()):
            serious_thread_stop.set()
        if(unsure_thread and unsure_thread.isAlive()):
            unsure_thread_stop.set()
    elif(ret == 1):
        logging.warning('Serious problems detected in Hashrate')
        if(serious_thread and serious_thread.isAlive()):
            logging.debug('Serious thread seems to be running already')
        else:
            serious_thread_stop = threading.Event()
            serious_thread = threading.Thread(target=rebootThread, args=(seriousBootInterval*60, serious_thread_stop))
            serious_thread.start()
    elif(ret == 2):
        logging.warning('Maybe fatal problems detected in Hashrate')
        if(unsure_thread and unsure_thread.isAlive()):
            logging.debug('Unsure thread seems to be running already')
        else:
            unsure_thread_stop = threading.Event()
            unsure_thread = threading.Thread(target=rebootThread, args=(unsureBootInterval*60, unsure_thread_stop))
            unsure_thread.start()
    elif(ret == 3):
        logging.warning('Likely not fatal problems detected in Hashrate, not doing anything')
    else:
        logging.info('Unknown code')
    time.sleep(interval*60)
