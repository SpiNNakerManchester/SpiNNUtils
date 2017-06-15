_already_issued = set()


def warn_once(logger, msg):
    if msg in _already_issued:
        return
    _already_issued.add((msg))
    logger.warn(msg)


def reset():
    global _already_issued
    _already_issued = set()
