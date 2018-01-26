#!/usr/bin/python

import subprocess, logging, traceback

#nvidia-smi stats -d pwrDraw
#0, pwrDraw , 1515942330734500, 114

def getGpuPowerArray():
    error = 0
    logging.debug('getGpuPowerArray()')
    try:
        stdout = subprocess.check_output(['nvidia-smi', 'stats', '-d pwrDraw'])
        logging.debug(stdout)
        powerDict = {}
        lines = stdout.splitlines()
        for line in lines:
            splitLine = line.split(',')
            logging.debug(splitLine)
            gpu = int(splitLine[0])
            power = int(splitLine[3])
            if(powerDict.has_key(gpu)):
                powerDict[gpu] = (int(powerDict[gpu][0]) + power, int(powerDict[gpu][1]) + 1)
            else:
                powerDict[gpu] = (power, 1)
        logging.debug(powerDict)
        powerArray = []
        for gpu, powers in powerDict.items():
            # TODO: This is not sorted, so we mess up the gpu index here...
            powerArray.append(int(powers[0]/powers[1]))
        return 0, powerArray
    except subprocess.CalledProcessError as darn:
        logging.error('Failed to get stats')
        logging.error(str(darn.returncode))
        logging.error(darn.output)
        return 1,[]
    except:
        logging.error('Unknown error')
        logging.error("Unexpected error:" + str(traceback.format_exc()))
        return 2,[]
    
    
    
