from collections import OrderedDict

import pandas as pd


def view_collection_data_dim(db, collection_names, field = 'data'):
    """
    return dimention of data table for each collection.
    """
    collection_dims = OrderedDict()
    for coll in sorted(collection_names):
        doc = db[coll].find_one()
        try:
            df = pd.DataFrame(doc[field])
            collection_dims[coll] = df.shape
        except ValueError:
            continue
    return collection_dims
