import pandas as pd
import re

def iso639_to_name(code):
    iso_codes = pd.read_csv('utils/iso-639-3.tab', sep='\t')
    try:
        name = iso_codes[iso_codes['Id'] == code]['Ref_Name'].item()
    except:
        name = 'unknown language'
    return name

def convert_dates(s):
    '''convert a string to a normalized date format, i.e. a single int or a 2-uple (int, int)
    corresponding to a date range.
    '''
    pattern1 = re.compile('[0-9]*')
    pattern2 = re.compile('[0-9]*-[0-9]*')
    pattern1bce = re.compile('[0-9]*BCE')
    pattern2bce = re.compile('[0-9]*-[0-9]*BCE')

    if bool(pattern1.fullmatch(s)):
        return int(s)
    elif bool(pattern2.fullmatch(s)):
        xx = s.split('-')
        return (int(xx[0]), int(xx[1]))
    elif bool(pattern1bce.fullmatch(s)):
        s = s.replace('BCE','')
        return -int(s)
    elif bool(pattern2bce.fullmatch(s)):
        s = s.replace('BCE','')
        xx = s.split('-')
        return (-int(xx[0]), -int(xx[1]))
    else:
        return 'unknown'