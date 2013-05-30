# -*- coding: utf-8 -*-

from django.db import models


class DateAwareModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
