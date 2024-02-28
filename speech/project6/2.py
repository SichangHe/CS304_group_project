def merge_dicts(list_of_dicts):
    all_keys = {key for d in list_of_dicts for key in d}
    merged_dict = {k: [d[k] for d in list_of_dicts if k in d] for k in all_keys}
    return merged_dict

list_of_dicts = [
    {"key1": "value1", "key2": "value2"},
    {"key1": "value3", "key2": "value4"},
    {"key1": "value5", "key2": "value6"},
]

merged_dict = merge_dicts(list_of_dicts)
print(merged_dict)
