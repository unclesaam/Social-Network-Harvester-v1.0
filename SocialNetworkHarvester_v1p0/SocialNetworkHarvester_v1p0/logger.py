import logging
import os
import pprint
import re
import threading

class Logger():

    indent_level = 0
    pp = pprint.PrettyPrinter()

    def __init__(self, loggerName="defaultLogger", filePath="default.log", format='%(message)s',
                 wrap=False, append=True, indentation=4, showThread=False):
        if not append:
            open(filePath, 'w').close()
        self.defaultFilePath = filePath
        self.format = format
        self.wrap = wrap
        self.indentation = indentation
        self.loggerName = loggerName
        self.fileHandler = None
        self.createLogger()
        self.showThread = showThread

    def setFileHandler(self, filepath):
        if self.fileHandler:
            self.logger.removeHandler(self.fileHandler)
        self.fileHandler = logging.FileHandler(filepath, mode="a+")
        self.fileHandler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(self.format)
        self.fileHandler.setFormatter(formatter)
        self.logger.addHandler(self.fileHandler)

    def createLogger(self):
        self.logger = logging.getLogger(self.loggerName)
        self.logger.setLevel(logging.DEBUG)
        self.setFileHandler(self.defaultFilePath)

    def log(self, message, indent=True):
        try:
            self.logger.info('%s%s%s'%(self.showThread*'{:<12}'.format(threading.current_thread().name),
                                       ' '*(self.indent_level), message))
        except UnicodeEncodeError:
            self.exception('An error occured in logging.')

    def pretty(self, message):
        try:
            self.logger.info(self.pp.pformat(message))
        except:
            self.exception('An error has occured in PrettyLogging.')

    def exception(self, message='EXCEPTION'):
        self.logger.exception("%s%s"%(self.showThread*'{:<12}'.format(threading.current_thread().name),message))

    def debug(self, showArgs=False, showFile=False, showClass=True):
        '''Decorator used to intelligently debug functions, classes, etc.
        '''
        def outer(func):
            def inner(*args, **kwargs):
                filename = func.__code__.co_filename
                func_name = func.__name__
                argCount = func.__code__.co_argcount
                inClassInstance = 0
                varNames = func.__code__.co_varnames

                s = []
                if self.showThread:
                    s += ['{:<12}'.format(threading.current_thread().name)]
                s += [' '*self.indent_level]
                if showFile:
                    s += [re.sub(r'(.*/)|(.*\\)', '', filename), ": "]

                if 'self' in varNames:
                    varNames = tuple(var for var in varNames if var != 'self')
                    inClassInstance = 1
                    instance = args[0]
                    if showClass:
                        s += ["%s."%re.search(r"(?<=\.)\w+(?=\'>)", str(type(instance))).group(0)]

                s += [func_name, '(']
                for varName in varNames[0:argCount-inClassInstance]:
                    s += [varName, ', ']
                if s[-1] == ', ':
                    s[-1] = "):"
                else:
                    s.append("):")
                self.logger.info("".join(s))

                self.indent_level += self.indentation

                if showArgs:
                    for variable, i in zip(varNames[:argCount-inClassInstance], range(inClassInstance,argCount)):
                        if isinstance(args[i], dict):
                            self.logger.info("%s<arg %s = %s>"%(" "*self.indent_level,variable,
                                                          self.pp.pformat(args[i])))
                        else:
                            self.logger.info("%s<arg %s = %s>"%(" "*self.indent_level,variable,args[i]))

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