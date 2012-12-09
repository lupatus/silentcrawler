# Silent Crawler

This simple Python module allows to crawl through objects tree without a need to care about exceptions. Can be useful if you have some structure that not always have needed values and you're only interested in retrieving them.

## Basic usage

```python
import silentcrawler

someobj = {'item' : { 'item2' : [1,2,3]}}

wrapped = silentcrawler.wrap(someobj)
print wrapped['item']['item2'][5].value_  # -> None
print wrapped.reset_()['item']['item2'][1].value_ # -> 2
wrapped2 = wrapped.reset_()['item']['item2'].wrap_()
print wrapped2[0].value_ #-> 1
print wrapped2.reset_()[3].value_ # -> None

# default value
wrapped = silentcrawler.wrap(someobj, default = 999)
print wrapped['item']['item2'][5].value_  # -> 999

# callbacks

# success callback
def on_success(value) :
    print 'success:', value
wrapped = silentcrawler.wrap(someobj, success=on_success)
wrapped['item'].get('item3').value_
# -> success: None

# failure callback
def on_failure(value, error) :
    print 'value:', value
    print 'with error:', repr(error)
wrapped = silentcrawler.wrap(someobj, failure=on_failure)
wrapped['something']['whatever'].lower()
# -> value: None
# -> with error: KeyError('something',)


def general_callback(value, is_error, error) :
    print 'value:', value
    if is_error :
        print 'but error occurred:', repr(error)
wrapped = silentcrawler.wrap(someobj, callback=general_callback)
wrapped['something']['whatever'].lower().value_
# -> value: None
# -> but error occurred: KeyError('something',)
wrapped.reset_()['item']['item2'].value_
# -> value: [1, 2, 3]
```

## Short Docu

**silentcrawler.wrap(obj, \*\*kwargs)**

Function returns _silentcrawler.Container_ object with given object.

Keyword arguments:

    *  _callable_ **success** - called on successful retrieval of value `def success(value)`
    *  _callable_ **failure** - called on failure in value search `def failure(value, exception_object)` 
    *  _callable_ **callback** - general callback function `def callback(value, is_error, exception_object)`
    *  _mixed_ **default** - default value
    *  _int_ **debug** - debug level (see below)
    *  _str_ **logger_id** - logger id (for `logging.getLogger(logger_id)`), alternative for logger object, by default it is `silentcrawler`
    *  _Logger_ **logger** - logger object

Debug:

Possible values are: _DEBUG\_NONE, DEBUG\_PATH, DEBUG\_LOG_

    *  _DEBUG\_NONE_ - debug turned off
    *  _DEBUG\_PATH_ - crawler will collect path elements, but without sending anything to log. Collected path can be retrieved with `wrapped.wrapper_.get_path()`.
    *  _DEBUG\_LOG_ - crawler will display errors in log
