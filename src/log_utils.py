
import logging

def configure_log():
    logger = logging.getLogger('main_logger')
    logger.setLevel(logging.DEBUG)

    st = logging.StreamHandler()  
    st.setLevel(logging.DEBUG)
    
    ch = logging.FileHandler('scrapper.log', mode='w')  
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    st.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(st)
    logger.addHandler(ch)
    return logger

log= configure_log()