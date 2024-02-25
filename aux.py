def bcva_edtrs_to_logmar(bcva_score, max_logmar=1.0):
    """
    Convert BCVA (ETDRS letters score) to LogMAR value.

    Parameters:
        bcva_score (float): BCVA score in ETDRS letters (range: 0 to 100).
        max_logmar (float, optional): Maximum LogMAR value (default is 1.0).

    Returns:
        float: LogMAR value corresponding to the given BCVA score.
    """
    bcva_score = max(0, min(100, bcva_score))
    logmar_value = max_logmar * (1 - bcva_score / 100)
    return logmar_value