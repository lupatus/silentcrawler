
DEBUG_NONE  = 0
DEBUG_PATH  = 1
DEBUG_LOG   = 2

def wrap(obj, *args, **kwargs) :
    
    class Crawler(object) :
        
        def __init__(self, obj, success=None, failure=None, callback=None,  default=None, debug = DEBUG_NONE, logger_id = 'safecrawler', logger = None) :
            self._obj = obj
            self._default = default
            self._success = success
            self._callback = callback
            self._failure = failure
            self._debug   = debug > DEBUG_NONE
            self._setup_logger(debug, logger, logger_id)
            self.reset()
        
        def _check(self) :
            if self._failed : 
                return False
            if self._fail :
                self._failed = True
                msg = 'Object in path "%s" is None, cannot go forward.' % self.get_path()
                self._error  = Exception(msg)
                self._logger['error'](msg)
                return False
            return True
            
        def _check_value(self) :
            if self._current is None :
                self._fail = True
        
        def _setup_logger(self, level, logger, logger_id) :
            self._logger = {}
            if (level & DEBUG_LOG) > 0 and (logger or logger_id) :
                if logger is None :
                    import logging
                    logger = logging.getLogger(logger_id)
                for n in ['debug', 'info', 'warning', 'error', 'exception'] :
                    self._logger[n] = getattr(logger, n)
            else :
                for n in ['debug', 'info', 'warning', 'error', 'exception'] :
                    self._logger[n] = lambda msg, *args, **kwargs : None
        
        def _exception(self, e) :
            self._error = e
            self._failed = True
            self._current = self._default
            if self._debug :
                self._logger['exception']('Caught exception in path %s', self.get_path())
        
        def get_current(self) :
            return self._current
        
        def has_errors(self) :
            return self._failed
        
        def get_path(self) :
            if self._path :
                return ''.join(self._path)
            else :
                return ''
        
        def get_error(self) :
            return self._error
        
        def value(self) :
            if self._failed :
                if callable(self._failure) :
                    self._failure(self._current, self._error)
                if callable(self._callback) :
                    self._callback(self._current, True, self._error)
            else :
                if callable(self._success) :
                    self._success(self._current)
                if callable(self._callback) :
                    self._callback(self._current, False, None)
            return self._current
        
        def reset(self) :
            self._current = self._obj
            if self._debug :
                self._path    = ['obj']
            else :
                self._path    = None
            self._failed  = False
            self._fail    = self._obj is None
            self._error   = None
            return self
        
        def attr(self, attr) :
            if not self._check() :
                return
            if self._debug :
                self._path.extend(['.', attr])
            try :
                self._current = getattr(self._current, attr)
                self._check_value()
            except Exception, e :
                self._exception(e)
            return self
            
        def run(self, *args, **kwargs) :
            if not self._check() :
                return
            if self._debug :
                argv = []
                for a in args :
                    argv.append(repr(a))
                for k in kwargs.keys() :
                    argv.append('%s=%s' % (k, repr(kwargs[k])))
                self._path.extend(['(', ', '.join(argv), ')'])
            try :
                self._current = self._current(*args, **kwargs)
                self._check_value()
            except Exception, e :
                self._exception(e)
            return self
            
        def item(self, item) :
            if not self._check() :
                return
            if self._debug :
                self._path.extend(['[',repr(item),']'])
            try :
                self._current = self._current[item]
                self._check_value()
            except Exception, e :
                self._exception(e)
            return self
    
    class Wrapper(object) :
        
        def __init__(self, obj, *args, **kwargs) :
            object.__setattr__(self, '__crawler', Crawler(obj, *args, **kwargs))
        
        def reset_(self) :
            object.__getattribute__(self, '__crawler').reset()
            return self
        
        def wrap_(self, *args, **kwargs) :
            return Wrapper(object.__getattribute__(self, '__crawler').get_current(), *args, **kwargs)
        
        def __getattr__(self, attr) :
            if attr == 'value_' :
                return object.__getattribute__(self, '__crawler').value()
            if attr == 'crawler_' :
                return object.__getattribute__(self, '__crawler')
            object.__getattribute__(self, '__crawler').attr(attr)
            return self
        
        def __call__(self, *args, **kwargs) :
            object.__getattribute__(self, '__crawler').run(*args, **kwargs)
            return self
        
        def __getitem__(self, item) :
            object.__getattribute__(self, '__crawler').item(item)
            return self
        
    return Wrapper(obj, *args, **kwargs)


if __name__ == '__main__' :
    
    
    ### SOME DUMMY TESTS...
    
    import sys

    class Printer(object) :
        def info(self, msg, *args, **kwargs) :
            print 'INFO:', msg % args
        def debug(self, msg, *args, **kwargs) :
            print 'DEBUG:', msg % args
        def warning(self, msg, *args, **kwargs) :
            print 'WARNING:', msg % args
        def error(self, msg, *args, **kwargs) :
            print 'ERROR:', msg % args
        def exception(self, msg, *args, **kwargs) :
            print 'EXCEPTION:', sys.exc_info()
            print 'EXCEPTION:', msg % args


    class a(object) :
        def blabla(self, *args, **kwargs) :
            return {
                'item' : ['a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10', 'a11', 'a12', 'a13', 'a14']
            }

    class b(object) :
        def __init__(self) :
            self.whatever = a()

    w = wrap(b(), default='AXX', debug=DEBUG_LOG, logger=Printer())
    print w.whatever.blabla(1,2,3,debug=True)['item'][22].upper().value_
    print w.reset_().whatever.blabla(1,2,3,debug=True)['item'][12].upper().value_
    w2 = w.reset_().whatever.blabla(1,2,3,debug=True)['item'].wrap_(debug = DEBUG_PATH, default = 'aXX')
    print w2[10].upper().value_
    print w2.wrapper_.get_path(), ' | ', w2.wrapper_.has_errors(), ' | ', w2.wrapper_.get_error()
    print w2[210].upper().value_
    print w2.crawler_.get_path(), ' | ', w2.wrapper_.has_errors(), ' | ', w2.wrapper_.get_error()
    print w2.reset_().whatever.upper().value_
    print w2.crawler_.get_path(), ' | ', w2.wrapper_.has_errors(), ' | ', w2.wrapper_.get_error()
    
    def on_success(value) :
        print 'success:', value
    def on_failure(value, error) :
        print 'value:', value
        print 'with error:', repr(error)
    def general_callback(value, is_error, error) :
        print 'value:', value
        if is_error :
            print 'but error occurred:', repr(error)
    w3 = wrap({'item' : [1,2,3]}, callback = general_callback, success = on_success, failure = on_failure)
    w3['item'][0].value_
    w3.whatever.value_
    