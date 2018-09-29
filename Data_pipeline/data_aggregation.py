import pymongo
import pandas as pd
import pprint


def verify_collections(db, collections):
    """
        collections: List[str]

        db: pymongo.database.Database

        verify if collection names do exist in the database. Return True if it is.
    """
    return set(collections).issubset(set(db.list_collection_names()))


def create_tables(db, collections, max_tables=100):
    """
    This function iterate through documents in collections and merge tables
    if number of rows for each table is same.

    if any one of the collection is invalid or some tables cannot be combined,
    return empty list.

        collections: List[str]
            collections to aggregate data

        max_tables: int
            maximum merged tables to return

        return: List[pandas.core.frame.DataFrame]
    """
    if not verify_collections(db, collections):
        return []

    res = []
    cursors = [db[collection].find(limit=max_tables) for collection in collections]
    for docs in zip(*cursors):
        merged = pd.DataFrame(docs[0]['data'])
        for doc in docs[1:]:
            new_df = pd.DataFrame(doc['data'])
            merged = merge_two_dfs(merged, new_df)
        res.append(merged)
    return res

def merge_two_dfs(df_a, df_b):
    """
        doc_a: pandas.core.frame.DataFrame
            first DataFrame

        doc_b: pandas.core.frame.DataFrame
            second DataFrame

        return: pandas.core.frame.DataFrame
    """
    if df_a.shape[0] != df_b.shape[0]:
        return None

    merged_df = pd.concat([df_a, df_b], axis=1)
    return merged_df

"""
    collections=[
     'lte_maxpowerinputs',
     'lte_maxpowertx_agc_data',
     'lte_maxpowertx_power',
     ]

     dfs = create_tables(db, collections)

"""
