from django.core.cache import cache
from django.conf import settings
from django.template.defaultfilters import slugify


def get_googleadwords_lock_id(model, identifier):
    _identifier = slugify(identifier) 
    return '%s-%s-%s' % (settings.GOOGLEADWORDS_LOCK_ID, model.__name__, _identifier)


def acquire_googleadwords_lock(model, idenitier):
    # cache.add fails if if the key already exists
    return cache.add(get_googleadwords_lock_id(model, idenitier), "true", settings.GOOGLEADWORDS_LOCK_TIMEOUT)


def release_googleadwords_lock(model, idenitier):
    # memcache delete is very slow, but we have to use it to take
    # advantage of using add() for atomic locking
    return cache.delete(get_googleadwords_lock_id(model, idenitier))
