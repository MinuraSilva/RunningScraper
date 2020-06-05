# for handling errback / errors

import re

headers = {
        "Host": "www.adidas.ca",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

def extract_item_code(url):
    code = re.search(r'\w\w\d\d\d\d', url).group()
    return code


def append_selectors(*args):
    """
    Each argument must be a string.
    Simply appends all of the given arguments with a space in between and returns.
    """

    return_string = ""

    for a in args:
        assert type(a) is str, "append_selectors given non-string argument"
        return_string = return_string + " " + a.strip()

    return_string = return_string.strip()  # remove whitespace after last selector
    return return_string