import re
from urllib.parse import quote_plus, urljoin


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


def build_item_page_url(uri):
    """
    replaces the {countryLang} tag with country code and builds a fully formed URL
    Converts uri -> '{countryLang}/t/react-miler-running-shoe-DnVKQm/CW1777-005'
    to this -> 'https://www.nike.com/ca/t/react-miler-running-shoe-DnVKQm/CW1777-005
    """

    country_code = "ca"
    base_url = "https://www.nike.com/"
    replace_string = "{countryLang}"

    url = urljoin(base_url, uri)
    url = url.replace(replace_string, country_code)

    return url

def nike_base64_to_url_encoding(in_string):
    """
    Converts the base 64 encoded string found in the json to a url encoding.
    """

    decoded_base_64 = in_string.encode().decode('unicode_escape')
    # 'unicode_escape' added for safety in case future versions include escape slashes.

    url_encoded = quote_plus(decoded_base_64)

    return url_encoded


def find_data(response):
    """returns the part of the selector that contains the json as string. Gets everything in between { }"""

    search_script = re.compile("\s*window\.INITIAL_REDUX_STATE")  # start pattern for script containing data

    for a in response.css("script"):
        script = str(a.css("::text").get(default=""))
        if search_script.match(script):
            json_string = re.search("{.*}", script).group()

            return json_string

    raise ValueError("Could not find the script with data in html")

# #####################################################################
# Improvements over extract_val:
# - handles lists of lists
# - accepts regex in "keys" addition to string
# - can apply multiple keys in sequence

def extract_val_re(obj, keys):
    """
    Input:
        obj: A python dict (also allows a list of lists - not sure if that is valid JSON)
        keys: Either string or compiled regex object or a list of strings and/or compiled regex objects

    If a single key is given, finds all instance of the key at any level of the JSON object and returns a list of these values.
    If a list of keys is given, applies the keys iteratively; i.e. first apply the first key to get result_1, then apply the second key on result_1 and so on.

    Output: A list of the values of those keys.
    """

    # helper to extract a single key
    def extract_single(obj, key):
        ret = []
        if isinstance(obj, dict):
            keys = obj.keys()
            for k in keys:
                # if key name matches, add to ret
                if re.search(key, k):
                    ret.append(obj[k])
                # if dict, recurse
                if isinstance(obj[k], dict):
                    ret.extend(extract_val_re(obj[k], key))
                elif isinstance(obj[k], list):
                    for li in obj[k]:
                        ret.extend(extract_val_re(li, key))
        elif isinstance(obj, list):
            for item in obj:
                ret.extend(extract_val_re(item, key))

        return ret

    # convert keys to regex if they are not already
    def convert_regex(single_or_list):

        # helper to convert a single key to regex
        def convert_single(str_or_regex):
            if isinstance(str_or_regex, str):
                return re.compile(f"^{str_or_regex}$")
            elif isinstance(str_or_regex, type(re.compile("compiled_object"))):
                # do nothing if already regex
                return str_or_regex
            else:
                assert False, "key is not either a string or a compiled regex object"

        # convert all keys to regex
        if isinstance(single_or_list, list):
            new_list = []
            for itm in single_or_list:
                new_list.append(convert_single(itm))
            return new_list
        else:
            return convert_single(single_or_list)

    # extract either a single key or a series of keys
    if not (isinstance(keys, list)):
        regex_key = convert_regex(keys)
        return extract_single(obj, regex_key)
    elif isinstance(keys, list):
        filtered = obj

        for key in keys:
            regex_key = convert_regex(key)
            filtered = extract_single(filtered, regex_key)
        return filtered
# #####################################################################