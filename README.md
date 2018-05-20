# im_util
This package contains miscellaneous utility functions for use by other im_* packages. 

[![Build Status](https://travis-ci.org/emlynoregan/im_util.svg?branch=master)](https://travis-ci.org/emlynoregan/im_util)

## Install

Use the python package for this library. You can find the package online [here](https://pypi.org/project/im-util/).

Change to your Python App Engine project's root folder and do the following:

> pip install im_util --target lib

Or add it to your requirements.txt. You'll also need to set up vendoring, see [app engine vendoring instructions here](https://cloud.google.com/appengine/docs/python/tools/using-libraries-python-27).

## make_flash

This is a utility function used in other im_X modules, which can take a first class function object (includes function name, body and closure information) and its argument values, and return a stable hash. This is used where you want to determine if the same function + args + etc has been called multiple times, and do something with that information (eg: debounce a call, use a cached result, etc). The function uses cloudpickle to pickle the inputs to a string, then md5 to hash that string. md5 guarantees a good spread across the hash space, and is fast to calculate. It is not cryptographically secure, but that shouldn't matter in the cases that this function is suitable for.

    def make_flash(f, *args, **kwargs)
    
    Arguments:
    - f: a first class function
    - args, kwargs: arguments that would be passed to the function
    Returns:
    - a string, a hash of the inputs.
  
