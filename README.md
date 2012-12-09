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

# general callback
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

Function returns _silentcrawler.Wrapper_ object with given object.

Keyword arguments:

  *  _callable_ **success** - called on successful retrieval of value `def success(value)`
  *  _callable_ **failure** - called on failure in value search `def failure(value, exception_object)` 
  *  _callable_ **callback** - general callback function `def callback(value, is_error, exception_object)`
  *  _mixed_ **default** - default value
  *  _int_ **debug** - debug level (see below)
  *  _str_ **logger_id** - logger id (for `logging.getLogger(logger_id)`), alternative for logger object, by default it is `silentcrawler`
  *  _Logger_ **logger** - logger object

Debug:

  *  _silentcrawler.DEBUG\_NONE_ - debug turned off
  *  _silentcrawler.DEBUG\_PATH_ - crawler will collect path elements, but without sending anything to log. Collected path can be retrieved with `wrapped.wrapper_.get_path()`.
  *  _silentcrawler.DEBUG\_LOG_ - crawler will display errors in log

If debug is set to _DEBUG\_LOG_ then you can set either `logger_id` or pass _Logger_ object into as `logger`.

### silentcrawler.Wrapper

Wrapper accepts any try to call, get attribute or get item and sends it to _Crawler_ object, so you're able to use this object as source object.

**Properties**

  *  **value_** - holds current value, triggers _success,failure_ and _callback_ callbacks
  *  **crawler_** - _silentcrawler.Crawler_ object

**Methods**

  *  **reset_()** - resets crawler (moves current value pointer to first object)
  *  **wrap_(\*\*kwargs)** - returns new _silentcrawler.Crawler_ object with current value as base object, for kwyword arguments see _silentcrawler.wrap_

If any of these properties or methods clashes with property or object that you would like to use, you can use _Crawler_ object directly :

```python
wrapped = silentcrawler.wrap(obj)
print wrapped.crawler_.attr('reset_').run().value()
```


### silentcrawler.Crawler

**Methods**

  *  **item(key)** - sets current value to `current[key]`
  *  **attr(name)** - sets current value to `getattr(current, name)`
  *  **run(\*args, \*\*kwargs)** - sets current value to result of `current(*args, **kwargs)`
  *  **reset()** - moves current value pointer to first object, resets all errors and path
  *  **value()** - returns current value, triggers _success,failure_ and _callback_ callbacks
  *  **get_current()** - returns current value
  *  **has_errors()** - returns boolean, wherever there was already a problem with retrieving a value
  *  **get_error()** - returns Exception object (if occured) or `None`
  *  **get_path()** - returns current path as string if debug is enabled or empty string in other case
