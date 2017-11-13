#!/usr/bin/python

import requests, traceback, logging

NANOPOOL_HASHRATE_TEMPLATE = 'https://api.nanopool.org/v1/eth/hashrate/$ADDRESS$'

def checkHashRate(ethereumAddress, worker, hashRateLowerLimit):
    logging.debug('checkNanopoolHashRate()')
    if(worker != None):
        logging.warning('Supervising single worker is not supported. Ignoring...')
    err = 0
    try:
        r = requests.get(NANOPOOL_HASHRATE_TEMPLATE.replace('$ADDRESS$', ethereumAddress))
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
