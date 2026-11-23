"""Original, intentionally defective review fixture; never production code."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Status:
    revision: int
    completed: int


class LiveStatusProvider:
    def __init__(self, authorize, load):
        self._authorize = authorize
        self._load = load

    def read(self, actor, job_id):
        self._authorize(actor, job_id)
        return self._load(job_id)


class CachedStatusProvider:
    def __init__(self, wrapped):
        self._wrapped = wrapped
        self._cache = {}

    def read(self, actor, job_id):
        if job_id not in self._cache:
            self._cache[job_id] = self._wrapped.read(actor, job_id)
        return self._cache[job_id]


class ProgressFeed:
    def __init__(self):
        self.current = Status(0, 0)
        self._subscribers = []

    def subscribe(self, subscriber):
        self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        self._subscribers.remove(subscriber)

    def commit(self, status):
        self.current = status
        for subscriber in self._subscribers:
            subscriber(self)
