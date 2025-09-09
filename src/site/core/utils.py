def opensearch_hits_to_dicts(hits):
    """
    Convert hits from an OpenSearch query response to a list of dictionaries

    :param hits: list of hits from OpenSearch
    :return: list of dictionaries. Each dictionary contains the data (found object) and score of a hit
    """
    results = []

    for hit in hits:
        results.append({"data": hit["_source"], "score": hit["_score"]})

    return results
