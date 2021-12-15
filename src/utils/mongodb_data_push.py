import json
from pymongo import MongoClient


def flatten_json(y):
    out = {}

    def flatten(x, name=''):

        # If the Nested key-value
        # pair is of dict type
        if type(x) is dict:

            for a in x:
                flatten(x[a], name + a + '_')

        # If the Nested key-value
        # pair is of list type
        elif type(x) is list:

            i = 0

            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


if __name__ == "__main__":
    client = MongoClient('0.0.0.0', port=27017)
    db = client.IBM_FINAL_PROJECT
    collection = db.ibm_data
    f = open('data.json', )
    data = json.load(f)
    flattened_data = []
    for row in data:
        flattened_data.append(flatten_json(row))
    collection.ibm_data.insert_many(flattened_data)
