# -*- coding: utf-8 -*-


import gevent


def map(fn, iterable):
    """Calls given function on each item from given iterable. Does it all
    in parallel. Returns results in the same order.

    :param fn: Callable.
    :param iterable: Iterable.
    """
    items = list(iterable)

    results = [None] * len(items)  # pre-populate the list with None
    jobs = []

    def fn_result_decorator(item):
        index = items.index(item)
        results[index] = fn(item)

    for item in items:
        job = gevent.spawn_link_exception(fn_result_decorator, item)
        jobs.append(job)

    gevent.joinall(jobs)
    return results
