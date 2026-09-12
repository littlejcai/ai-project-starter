"""Pure business-rule example. Does not implement database concurrency or an API."""


def registration_decision(*, capacity, registered, already_registered, authenticated):
    if type(capacity) is not int or type(registered) is not int:
        raise ValueError('Counts must be integers')
    if capacity < 0 or registered < 0 or registered > capacity:
        raise ValueError('Invalid counts')
    if type(already_registered) is not bool or type(authenticated) is not bool:
        raise ValueError('Flags must be boolean')
    if not authenticated:
        return 'UNAUTHENTICATED'
    if already_registered:
        return 'ALREADY_REGISTERED'
    if registered >= capacity:
        return 'FULL'
    return 'ACCEPT'
