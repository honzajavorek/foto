# -*- coding: utf-8 -*-


import gevent


def map_count(fn, iterable):
    """Calls given function on each item from given iterable. Does it all
    in parallel. Returns number of processed items.

    :param fn: Callable.
    :param iterable: Iterable.
    """
    jobs = []

    for item in iterable:
        job = gevent.spawn_link_exception(fn, item)
        jobs.append(job)

    gevent.joinall(jobs)
    return len(jobs)


def map(fn, iterable):
    """Calls given function on each item from given iterable. Does it all
    in parallel. Returns results in the same order.

    :param fn: Callable.
    :param iterable: Iterable.
    """
    jobs = []
    for item in iterable:
        job = gevent.spawn_link_exception(fn, item)
        jobs.append(job)

    gevent.joinall(jobs)
    return [job.value for job in jobs]


def map_random(fn, iterable):
    """Calls given function on each item from given iterable. Does it all
    in parallel. Returns results randomly.

    :param fn: Callable.
    :param iterable: Iterable.
    """
    jobs = []
    for item in iterable:
        job = gevent.spawn_link_exception(fn, item)
        jobs.append(job)

    yielded = []
    jobs_count = len(jobs)
    while len(yielded) < jobs_count:
        for job in jobs:
            if job.ready() and job not in yielded:
                yield job.value
                yielded.append(job)
        gevent.sleep(0)
