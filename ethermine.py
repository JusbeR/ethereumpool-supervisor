#!/usr/bin/python

import requests
import traceback
import logging

ETHERMINE_HASHRATE_TEMPLATE = 'https://api.ethermine.org/miner/$ADDRESS$/currentStats'
ETHERMINE_WORKER_DATAILS_TEMPLATE = 'https://api.ethermine.org/miner/$ADDRESS$/workers'

def get_hash_rate(ethereum_address, worker):
    ret = 0
    hash_rate = 0
    if worker != None:
        req = requests.get(ETHERMINE_WORKER_DATAILS_TEMPLATE.replace('$ADDRESS$', ethereum_address))
        if req.status_code >= 400:
            logging.warning('Getting HashRate failed, ethermine maybe broken or wrong address?\
            . status_code:' + str(req.status_code))
            ret = 3
        logging.debug('Response: ' + req.text)
        worker_found = False
        for item in req.json()['data']:
            if item['worker'] == worker:
                hash_rate = int(item['currentHashrate'])
                hash_rate = hash_rate/(1000*1000)
                worker_found = True
                break
        status = req.json()['status']
        if not worker_found:
            logging.error('Could not find such worker. Are you sure that \
            all the params are right and worker is running?')
            ret = 3
    else:
        req = requests.get(ETHERMINE_HASHRATE_TEMPLATE.replace('$ADDRESS$', ethereum_address))
        if req.status_code >= 400:
            logging.warning('Getting HashRate failed, ethermine maybe broken or wrong address?\
            . status_code:' + str(req.status_code))
            ret = 3
        logging.debug('Response: ' + req.text)
        status = req.json()['status']
        hash_rate = req.json()['data']['currentHashrate']
        hash_rate = hash_rate/(1000*1000)

    if status != 'OK':
        logging.warning('TODO: Status is not OK. No freaking idea what that \
        means? I guess we report error.')
        ret = 2
    return ret, hash_rate

def check_hash_rate(ethereum_address, worker, hash_rate_lower_limit):
    logging.debug('checkEthermineHashRate()')
    err = 0
    try:
        ret, hash_rate = get_hash_rate(ethereum_address, worker)
        if ret == 0:
            if hash_rate >= hash_rate_lower_limit:
                logging.debug('Hash rate ok(' + str(hash_rate) + ')')
                return 0
            else:
                logging.warning('Hash rate is smaller(' + str(hash_rate)  + ') than wanted('
                                + str(hash_rate_lower_limit) + '). This might cause recovery \
                                boot soonish.')
                return 1
        else:
            return ret
    except Exception as e:
        logging.warning('Getting HashRate failed, ethermine, internet connection \
        or this code maybe broken?')
        logging.warning("Unexpected error:" + str(traceback.format_exc()))
        return 2
    return err
