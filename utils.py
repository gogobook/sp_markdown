# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache import caches, cache


User = get_user_model()


def create_user(**kwargs):
    if 'username' not in kwargs:
        kwargs['username'] = "user_foo%d" % User.objects.all().count()

    if 'email' not in kwargs:
        kwargs['email'] = "%s@bar.com" % kwargs['username']

    if 'password' not in kwargs:
        kwargs['password'] = "bar"

    return User.objects.create_user(**kwargs)

def login(test_case_instance, user=None, password=None):
    user = user or test_case_instance.user
    password = password or "bar"
    login_successful = test_case_instance.client.login(username=user.username, password=password)
    test_case_instance.assertTrue(login_successful)


def cache_clear():
    cache.clear()  # Default one

    for c in caches.all():
        c.clear()
