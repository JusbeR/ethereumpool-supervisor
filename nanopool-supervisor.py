
#!/usr/bin/python

import requests, sys, argparse, traceback, time, threading, os
from argparse import RawTextHelpFormatter

NANOPOOL_HASHRATE_TEMPLATE = 'https://api.nanopool.org/v1/eth/hashrate/$ADDRESS$'

def debug(text):
  if(DEBUG):
    print(text)

def checkHashRate():
    debug('checkHashRate()')
    err = 0
    try:
        r = requests.get(NANOPOOL_HASHRATE_TEMPLATE.replace('$ADDRESS$', nanoPoolHashRateAddress))
        if(r.status_code >= 400):
            print('Getting HashRate failed, nanopool maybe broken or wrong address?. status_code:' + str(r.status_code))
            return 3
        debug('Response: ' + r.text)
        status = r.json()['status']
        hashRate = r.json()['data']
        if(status == True):
            if(hashRate >= hashRateLowerLimit):
                debug('Hash rate ok(' + str(hashRate) + ')')
                return 0
            else:
                print('Hash rate is smaller(' + str(hashRate)  + ') than wanted(' + str(hashRateLowerLimit) + '). This might cause recovery boot soonish.')
                return 1
        else:
            print('TODO: Status is not true. No freaking idea what that means? I guess we report error.')
            return 1
    except Exception as e:
        print('Getting HashRate failed, nanopool, internet connection or this code maybe broken?')
        print("Unexpected error:" + str(traceback.format_exc()))
        return 2
    return err

def rebootThread(waitTime, stop_event):
    debug('Starting reboot thread, booting in ' + str(waitTime) + ' seconds if no change in conditions...')
    stop_event.wait(waitTime)
    if(stop_event.isSet()):
        print('Critical thread Reboot cancelled')
        return
    print('Booting...')
    #os.system('reboot --reboot')


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
parser.add_argument("-v", "--verbose", action="store_true",
                    help="Print debug logs to stdout")
parser.add_argument("address", help='ethereum address')

args = parser.parse_args()
DEBUG = args.verbose
nanoPoolHashRateAddress = args.address
interval = args.interval
seriousBootInterval = args.serious_boot_interval
unsureBootInterval = args.unsure_boot_interval
hashRateLowerLimit = args.hash_rate_limit

print('Supervising account: ' + nanoPoolHashRateAddress)
print('Checking hash rate in every ' + str(interval) + ' minutes')
print('Booting computer if hash rate is below ' + str(hashRateLowerLimit))
print('Booting computer after ' + str(seriousBootInterval) + ' minutes if serious problems are detected and after ' + str(unsureBootInterval) + ' minutes if unsure problems are detected.')

serious_thread_stop = None
serious_thread = None
unsure_thread_stop = None
unsure_thread = None

while(1):
    ret = checkHashRate()
    if(ret == 0):
        debug('All OK')
        if(serious_thread and serious_thread.isAlive()):
            serious_thread_stop.set()
        if(unsure_thread and unsure_thread.isAlive()):
            unsure_thread_stop.set()
    elif(ret == 1):
        print('Serious problems detected in Hashrate')
        if(serious_thread and serious_thread.isAlive()):
            debug('Serious thread seems to be running already')
        else:
            serious_thread_stop = threading.Event()
            serious_thread = threading.Thread(target=rebootThread, args=(seriousBootInterval*60, serious_thread_stop))
            serious_thread.start()
    elif(ret == 2):
        print('Maybe fatal problems detected in Hashrate')
        if(unsure_thread and unsure_thread.isAlive()):
            debug('Unsure thread seems to be running already')
        else:
            unsure_thread_stop = threading.Event()
            unsure_thread = threading.Thread(target=rebootThread, args=(unsureBootInterval*60, unsure_thread_stop))
            unsure_thread.start()
    elif(ret == 3):
        print('Likely not fatal problems detected in Hashrate, not doing anything')
    else:
        print('Unknown code')
    time.sleep(interval*60)
