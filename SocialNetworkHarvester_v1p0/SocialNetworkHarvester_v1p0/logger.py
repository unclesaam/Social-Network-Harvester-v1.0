import logging
import os
import pprint
import re

class Logger():

    indentation = 4
    indent_level = 0
    pp = pprint.PrettyPrinter()

    def __init__(self, loggerName, filePath, format, wrap=False):
        open(filePath, 'w').close()
        self.logger = logging.getLogger(loggerName)
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(filePath, mode="a+")
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(format)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.wrap = wrap

    def log(self, message, indent=True):
        self.logger.info('%s%s'%(' '*(self.indent_level), message))

    def pretty(self, message):
        self.logger.info(self.pp.pformat(message))

    def exception(self, message='EXCEPTION'):
        self.logger.exception(message)

    def debug(self, showArgs=False, showFile=True):
        '''Decorator used to intelligently debug functions
        '''
        def outer(func):
            def inner(*args, **kwargs):
                prefix = "FUNCTION"
                if showFile:
                    prefix = re.sub(r'(.*/)|(.*\\)', '', func.__code__.co_filename)+':'
                self.logger.info('%s%s %s%s:'%(' '*self.indent_level, prefix, func.__name__,
                                                     func.__code__.co_varnames[:func.__code__.co_argcount]))
                self.indent_level += self.indentation
                if showArgs:
                    for variable, i in zip(func.__code__.co_varnames[:func.__code__.co_argcount],
                                           range(0,func.__code__.co_argcount)):
                        if isinstance(args[i], dict):
                            self.logger.info("%s%s = %s"%(" "*self.indent_level,variable,
                                                          self.pp.pformat(args[i])))
                        else:
                            self.logger.info("%s%s = %s"%(" "*self.indent_level,variable,args[i]))
                if self.wrap:
                    if self.indent_level > self.indentation*40:
                        self.indent_level = 8
                    elif self.indent_level < 0:
                        self.indent_level = self.indentation*40 - 4
                try:
                    ret = func(*args, **kwargs)
                    self.indent_level -= self.indentation
                except:
                    self.indent_level -= self.indentation
                    raise
                return ret
            return inner
        return outer
