from datetime import datetime 
from functools import wraps 
import logging
import time 

logger = logging.getLogger(__name__)
logger.info(f"Logger Initiated: {logger}")

def timeme(func):
    @wraps(func)
    def timediff(*args,**kwargs):
        a = time.time()
        result = func(*args,**kwargs)
        b = time.time()
        logger.debug(f"@timeme: {func.__name__} took {b - a} seconds")
        return result 
    return timediff

def convert_resolution_to_ms(parsed_resolution):
    SECOND = 1000
    MINUTE = 60 * SECOND
    HOUR = 60 * MINUTE
    DAY = 24 * HOUR

    value = parsed_resolution['value']
    interval_unit = parsed_resolution['unit']

    if interval_unit == "min":
        formula = MINUTE
    elif interval_unit == "hour":
        formula = HOUR
    elif interval_unit == "day":
        formula = DAY
    else:
        return logger.error(f"Unknown interval unit: {interval_unit}")
    
    ms = value * formula
    return ms

def get_lookback_unix_time(parsed, lookback):
    '''
    Dependent on standard_interval_formatter function "parsed" as input 
    '''
    SECOND = 1000
    MINUTE = 60 * SECOND
    HOUR = 60 * MINUTE
    DAY = 24 * HOUR

    value = parsed['value']
    interval_unit = parsed['unit']

    if interval_unit == "min":
        formula = MINUTE
    elif interval_unit == "hour":
        formula = HOUR
    elif interval_unit == "day":
        formula = DAY
    else:
        return logger.error(f"Unknown interval unit: {interval_unit}")

    unix_time = int(datetime.timestamp(datetime.now()) * 1000)
    starttime = unix_time - lookback * value * formula 
    logger.debug(f"starttime: {starttime}")
    return starttime