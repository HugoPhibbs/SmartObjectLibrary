def opensearch_hits_to_dicts(hits):
    results = []

    for hit in hits:
        results.append({"data": hit["_source"], "score": hit["_score"]})

    return results
