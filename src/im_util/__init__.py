import time
import datetime
import logging
import types
import cloudpickle
import hashlib

TASKUTILS_LOGGING = False
TASKUTILS_DUMP = False

def set_logging(value):
    global TASKUTILS_LOGGING
    TASKUTILS_LOGGING = value

def get_logging():
    global TASKUTILS_LOGGING
    return TASKUTILS_LOGGING or TASKUTILS_DUMP

def set_dump(value):
    global TASKUTILS_DUMP
    TASKUTILS_DUMP = value

def get_dump():
    global TASKUTILS_DUMP
    return TASKUTILS_DUMP

def datetime_to_unixtimestampusec(aDateTime):
    return long(time.mktime(aDateTime.timetuple()) * 1000000 + aDateTime.microsecond) if aDateTime else 0

def get_utcnow_unixtimestampusec():
    return datetime_to_unixtimestampusec(datetime.datetime.utcnow())

def logdebug(message):
    if get_logging():
        logging.debug(message)
        
def logwarning(message):
    if get_logging():
        logging.warning(message)

def logexception(message):
    if get_logging():
        logging.exception(message)

def dumper(thing):
    if get_dump():
        def printf(f, indent, foundf):
            logdebug("%s [%s] %s" % ("#" * (indent+1), len(cloudpickle.dumps(f)), f))
            logdebug("%s code size = %s" % ("#" * (indent+1), len(cloudpickle.dumps(f.func_code))))
#             print "%s closure size = %s" % ("#" * indent, len(cloudpickle.dumps(f.func_closure)))
            dodumpclosure(f, (indent+1), foundf + [f])
                    
        def printi(arg, indent):
            logdebug("%s [%s] %s" % ("#" * (indent+1), len(cloudpickle.dumps(arg)), arg))

        def printlen(obj, indent):
            logdebug("%s [%s] %s" % ("#" * (indent+1), len(obj), type(obj)))
    
        def printmsg(msg, indent):
            logdebug("%s %s" % ("*" * (indent+1), msg))
    
        def dodumpitem(item, indent, foundf):
            if isinstance(item, types.FunctionType):
                printf(item, indent, foundf)
            elif isinstance(item, dict):
                printlen(item, indent)
                for key, value in item.iteritems():
                    printmsg(key, indent)
                    dodumpitem(value, indent+1, foundf)
            elif isinstance(item, (list, set, tuple)):
                printlen(item, indent)
                for index, elem in enumerate(item):
                    printmsg(index, indent)
                    dodumpitem(elem, indent+1, foundf)
            else:
                printi(item, indent) # not a function
    
        def dodumpclosure(f, indent, foundf):
            if f.func_closure:
                cells = [lcell for lcell in f.func_closure]
                for cell in cells: #[lcell.cell_contents for lcell in f.func_closure]:
                    try:
                        item = cell.cell_contents
                        if isinstance(item, types.FunctionType):
                            if f == item:
                                printmsg("%s - Function in its own closure, stop traverse" % item, indent)
                            elif item in foundf:
                                printmsg("%s - Function in ancestor closure, stop traverse" % item, indent)
                            else:
                                dodumpitem(item, indent, foundf)
                        else:
                            dodumpitem(item, indent, foundf)
                    except ValueError, vex:
                        printmsg(repr(vex), indent)
            else:
                printmsg("null closure", indent)
 
        try:   
            dodumpitem(thing, 0, [])
        except Exception:
            logexception("dumper failed")
            
def make_flash(f, *args, **kwargs):
    flash = hashlib.md5(
            cloudpickle.dumps((f, args, kwargs))
        ).hexdigest()
    logdebug(flash)
    return flash

def make_objhash(obj):
    objhash = hashlib.md5(
            cloudpickle.dumps(obj)
        ).hexdigest()
    logdebug(objhash)
    return objhash

#backward compatibility
def GenerateStableId(instring):
    return hashlib.md5(instring).hexdigest()


###### split utils, cribbed from google's mapreduce libs
# cribbed from /usr/lib/google-cloud-sdk/platform/google_appengine/google/appengine/ext/mapreduce/property_range.py
# added parameterised alphabet

_ALPHABET = "".join(chr(i) for i in range(128))

_STRING_LENGTH = 4

def _split_string_property(start, end, n, include_start, include_end, alphabet = _ALPHABET):
    try:
        start = start.encode("ascii")
        end = end.encode("ascii")
    except UnicodeEncodeError, e:
        raise ValueError("Only ascii str is supported.", e)
    
    return _split_byte_string_property(start, end, n, include_start, include_end, alphabet)

def _split_byte_string_property(start, end, n, include_start, include_end, alphabet = _ALPHABET):

    i = 0
    for i, (s, e) in enumerate(zip(start, end)):
        if s != e:
            break
    common_prefix = start[:i]
    start_suffix = start[i+_STRING_LENGTH:]
    end_suffix = end[i+_STRING_LENGTH:]
    start = start[i:i+_STRING_LENGTH]
    end = end[i:i+_STRING_LENGTH]
    
    
    weights = _get_weights(_STRING_LENGTH, alphabet)
    start_ord = _str_to_ord(start, weights, alphabet)
    if not include_start:
        start_ord += 1
    end_ord = _str_to_ord(end, weights, alphabet)
    if include_end:
        end_ord += 1
    
    
    stride = (end_ord - start_ord) / float(n)
    if stride <= 0:
        raise ValueError("Range too small to split: start %s end %s", start, end)
    splitpoints = [_ord_to_str(start_ord, weights, alphabet)]
    previous = start_ord
    for i in range(1, n):
        point = start_ord + int(round(stride * i))
        if point == previous or point > end_ord:
            continue
        previous = point
        splitpoints.append(_ord_to_str(point, weights, alphabet))
    end_str = _ord_to_str(end_ord, weights, alphabet)
    if end_str not in splitpoints:
        splitpoints.append(end_str)
    
    
    splitpoints[0] += start_suffix
    splitpoints[-1] += end_suffix
    
    return [common_prefix + point for point in splitpoints]


def _get_weights(max_length, alphabet):
    """Get weights for each offset in str of certain max length.
    
    Args:
      max_length: max length of the strings.
    
    Returns:
      A list of ints as weights.
    
    Example:
      If max_length is 2 and alphabet is "ab", then we have order "", "a", "aa",
    "ab", "b", "ba", "bb". So the weight for the first char is 3.
    """
    weights = [1]
    for i in range(1, max_length):
        weights.append(weights[i-1] * len(alphabet) + 1)
    weights.reverse()
    return weights


def _str_to_ord(content, weights, alphabet):
    """Converts a string to its lexicographical order.
    
    Args:
      content: the string to convert. Of type str.
      weights: weights from _get_weights.
    
    Returns:
      an int or long that represents the order of this string. "" has order 0.
    """
    ordinal = 0
    for i, c in enumerate(content):
        ordinal += weights[i] * alphabet.index(c) + 1
    return ordinal


def _ord_to_str(ordinal, weights, alphabet):
    """Reverse function of _str_to_ord."""
    chars = []
    for weight in weights:
        if ordinal == 0:
            return "".join(chars)
        ordinal -= 1
        index, ordinal = divmod(ordinal, weight)
        chars.append(alphabet[index])
    return "".join(chars)

