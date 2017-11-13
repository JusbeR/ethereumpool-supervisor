#!/usr/bin/python

import requests, traceback, logging

ETHERMINE_HASHRATE_TEMPLATE = 'https://api.ethermine.org/miner/$ADDRESS$/currentStats'
ETHERMINE_WORKER_DATAILS_TEMPLATE = 'https://api.ethermine.org/miner/$ADDRESS$/workers'

def getHashRate(ethereumAddress, worker):
    ret = 0
    hashRate = 0
    if worker != None:
        req = requests.get(ETHERMINE_WORKER_DATAILS_TEMPLATE.replace('$ADDRESS$', ethereumAddress))
        if req.status_code >= 400:
            logging.warning('Getting HashRate failed, ethermine maybe broken or wrong address?\
            . status_code:' + str(req.status_code))
            ret = 3
        logging.debug('Response: ' + req.text)
        workerFound = False
        for item in req.json()['data']:
            if item['worker'] == worker:
                hashRate = int(item['currentHashrate'])
                hashRate = hashRate/(1000*1000)
                workerFound = True
                break
        status = req.json()['status']
        if(not workerFound):
            logging.error('Could not find such worker. Are you sure that \
            all the params are right and worker is running?')
            ret = 3
    else:
        req = requests.get(ETHERMINE_HASHRATE_TEMPLATE.replace('$ADDRESS$', ethereumAddress))
        if req.status_code >= 400:
            logging.warning('Getting HashRate failed, ethermine maybe broken or wrong address?\
            . status_code:' + str(req.status_code))
            ret = 3
        logging.debug('Response: ' + req.text)
        status = req.json()['status']
        hashRate = req.json()['data']['currentHashrate']
        hashRate = hashRate/(1000*1000)

    if status != 'OK':
        logging.warning('TODO: Status is not OK. No freaking idea what that means? I guess we report error.')
        ret = 2
    return ret, hashRate

def checkHashRate(ethereumAddress, worker, hashRateLowerLimit):
    logging.debug('checkEthermineHashRate()')
    err = 0
    try:
        ret, hashRate = getHashRate(ethereumAddress, worker)
        if ret == 0:
            if(hashRate >= hashRateLowerLimit):
                logging.debug('Hash rate ok(' + str(hashRate) + ')')
                return 0
            else:
                logging.warning('Hash rate is smaller(' + str(hashRate)  + ') than wanted(' + str(hashRateLowerLimit) + '). This might cause recovery boot soonish.')
                return 1
        else:
            return ret
    except Exception as e:
        logging.warning('Getting HashRate failed, ethermine, internet connection or this code maybe broken?')
        logging.warning("Unexpected error:" + str(traceback.format_exc()))
        return 2
    return err
