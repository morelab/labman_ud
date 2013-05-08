# coding: utf-8

import os

from django.db import models
from django.template.defaultfilters import slugify

from utils.models import Country

# Create your models here.


def organization_logo_path(self, filename):
    return '%s/%s%s' % ('organizations', self.slug, os.path.splitext(filename)[-1])


#########################
# Model: OrganizationType
#########################

class OrganizationType(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=u'Name',
    )

    slug = models.SlugField(
        max_length=100,
        blank=True,
    )

    description = models.TextField(
        max_length=1500,
        blank=True,
    )

    def __unicode__(self):
        return u'%s' % (self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.name))
        super(OrganizationType, self).save(*args, **kwargs)


#########################
# Model: Organization
#########################

class Organization(models.Model):
    sub_organization_of = models.ForeignKey(
        'self',
        blank=True,
        null=True,
    )

    full_name = models.CharField(
        max_length=250,
    )

    short_name = models.CharField(
        max_length=250,
    )

    slug = models.SlugField(
        max_length=250,
        blank=True,
    )

    country = models.ForeignKey(Country)

    homepage = models.URLField(
        blank=True,
        null=True,
    )

    def __unicode__(self):
        return u'%s (%s)' % (self.short_name, self.full_name)

    def save(self, *args, **kwargs):
        if not self.short_name:
            self.short_name = self.full_name.encode('utf-8')
        self.slug = slugify(str(self.short_name))
        super(Organization, self).save(*args, **kwargs)
