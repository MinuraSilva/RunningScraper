import re
import logging

logger = logging.getLogger("adidas_ca")

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


def get_mens_size(size_code):
    assert (450 <= size_code <= 820)

    if size_code <= 750:
        return (size_code-450)/20
    elif size_code == 760:
        return 16.0
    else:
        return (size_code-780)/10 + 17


def shoe_size_conversion(size_str, sku):

    try:
        size_code = int(sku.split("_")[1])
        mens_size = get_mens_size(size_code)
        womens_size = mens_size + 1

        mens_size = f"M{mens_size}"
        womens_size = f"W{womens_size}"

        return [mens_size, womens_size]

    except:
        return [size_str]
