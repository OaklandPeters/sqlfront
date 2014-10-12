
conversion_lookup = {
    #(_from, _to): converstion-function
    #ex. (str, int): _assert_str_to_int
}

def convertible(value, _from=None, _to=None, name=None):
    
    # Validation '_to' is required
    
    
    
    type_pair = (_from, _to) 
    if type_pair in conversion_lookup:
        return conversion_lookup[type_pair](value, name)
    # ~ approximately the same as:
    #if (_from, _to) == (str, int):
    #    return _assert_str_to_int(value, name)
    
    # FALLBACK TYPE-INFERENCE ON _from
    #---- if no direct version found:
    #.... look for: potential_pairs = type pairs with (*, _to) 
    #    potential_pairs = [(temp_from, temp_to)
    #        for (temp_from, temp_to) in conversion_lookup.keys()
    #        if temp_to == _to
    #    ]
    #     and see if 
    #    for temp_pair in potential_pairs:
    #        temp_from = temp_pair[0]
    #        if isinstance(_from, temp_from):
    #            inferred_from = temp_from
    
    #ALSO: If no _from is provided, do TYPE-INFERENCE on type(value)
    
    
def _assert_str_to_int(value, name):
    """ _assert_str_to_int(object: value, str: name) --> str """ 
    if isinstance(value, basestring):
        try:
            int(value)
        except ValueError:
            raise ValueError(str.format(
                "'{0}' string must be convertible to an integer: '{1}'",
                name, value
            ))
        return str(value)
    elif isinstance(offset, int):
        return str(offset)
    else:
        raise TypeError(str.format(
            "'{0}' should be type basestring or int, not '{0}'",
            name, _class_name(value)
        ))
conversion_lookup[(str, int)] = _assert_str_to_int





def _class_name(obj):
    return obj.__class__.__name__