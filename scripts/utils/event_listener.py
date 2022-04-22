from collections import defaultdict
# See: https://dev.to/kuba_szw/build-your-own-event-system-in-python-5hk6

subscribers = defaultdict(list)


def subscribe(event_type, fn):
    subscribers[event_type].append(fn)


def post_event(event_type):
    if event_type in subscribers:
        for fn in subscribers[event_type]:
            fn()
