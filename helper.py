from datetime import datetime

def find_word(text, words):
    for word in words:
        if word in text:
            return word
    return None

def slice_str(s:str,start:str, end:str):
    a = s.find(start)
    if a == -1:
        return ' '
    return s[s.find(start)+len(start):s.find(end)]

def time_epoch():
    from time import mktime
    dt = datetime.now()
    sec_since_epoch = mktime(dt.timetuple()) + dt.microsecond/1000000.0

    millis_since_epoch = sec_since_epoch * 1000
    return int(millis_since_epoch)
