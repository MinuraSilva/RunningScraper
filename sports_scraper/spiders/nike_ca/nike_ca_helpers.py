from urllib.parse import quote_plus


def extract_val(obj, key):
    """
    Extracts value of given key from any level of a nested dict.
    Does not handle list of lists (i.e. without a key between the two levels of list).
    Returns a list of values.
    """

    ret = []
    if isinstance(obj, dict):
        keys = obj.keys()
        for k in keys:
            # if key name matches, add to ret
            if k == key:
                ret.append(obj[k])

            # if dict, recurse
            if isinstance(obj[k], dict):
                ret.extend(extract_val(obj[k], key))
            elif isinstance(obj[k], list):
                for li in obj[k]:
                    ret.extend(extract_val(li, key))

    return ret

def nike_base64_to_url_encoding(in_string):
    """
    Converts the base 64 encoded string found in the json to a url encoding.
    """

    decoded_base_64 = in_string.encode().decode('unicode_escape')
    # 'unicode_escape' added for safety in case future versions include escape slashes.

    url_encoded = quote_plus(decoded_base_64)

    return url_encoded
