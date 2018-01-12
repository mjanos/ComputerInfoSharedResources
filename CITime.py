import re

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )

"""Formats time into a readable format"""
def format_time(seconds):
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1: name = name.rstrip('s')
            result.append("{} {}".format(int(value),name))
    return ', '.join(result[:4])

"""Formats date into a readable format"""
def format_date(date_string):
    try:
        re_date = re.match("([0-9]{4})([0-9]{2})([0-9]{2})",date_string)
        final_string = "%s/%s/%s" % (re_date.group(2),re_date.group(3),re_date.group(1))
    except:
        final_string = date_string
    return final_string
