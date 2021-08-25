import logging
def llogInfo(f : function):
    logging.info(f())
def llogDebug(f : function):
    logging.debug(f())
def llogWarn(f : function):
    logging.warn(f())
def llogCrit(f : function):
    logging.critical(f())