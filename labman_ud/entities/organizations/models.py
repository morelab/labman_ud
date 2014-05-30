# -*- encoding: utf-8 -*-

import os

from django.db import models
from django.template.defaultfilters import slugify
from entities.core.models import BaseModel


# Create your models here.


def organization_logo_path(self, filename):
    return '%s/%s%s' % ('organizations', self.slug, os.path.splitext(filename)[-1])


###########################################################################
# Model: OrganizationType
###########################################################################

class OrganizationType(BaseModel):
    name = models.CharField(
        max_length=100,
    )

    slug = models.SlugField(
        max_length=100,
        blank=True,
        unique=True,
    )

    description = models.TextField(
        max_length=1500,
        blank=True,
    )

    class Meta:
        ordering = ['slug']

    def __unicode__(self):
        return u'%s' % (self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.name.encode('utf-8')))
        super(OrganizationType, self).save(*args, **kwargs)


###########################################################################
# Model: Organization
###########################################################################

class Organization(BaseModel):
    organization_type = models.ForeignKey('OrganizationType')

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
        blank=True,
    )

    slug = models.SlugField(
        max_length=250,
        blank=True,
        unique=True,
    )

    country = models.ForeignKey('utils.Country')

    homepage = models.URLField(
        blank=True,
        null=True,
    )

    logo = models.ImageField(
        upload_to=organization_logo_path,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['slug']

    def __unicode__(self):
        if self.short_name == self.full_name:
            return u'%s' % (self.full_name)
        else:
            return u'%s (%s)' % (self.short_name, self.full_name)

    def save(self, *args, **kwargs):
        if not self.short_name:
            self.short_name = self.full_name

        else:
            self.short_name = self.short_name

        self.slug = slugify(self.short_name.encode('utf-8'))
        super(Organization, self).save(*args, **kwargs)


###########################################################################
# Model: Unit
###########################################################################

class Unit(BaseModel):
    organization = models.ForeignKey('Organization')

    head = models.ForeignKey('persons.Person', null=True, blank=True)

    order = models.PositiveSmallIntegerField(
        unique=True,
    )

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return u'%s' % (self.organization.full_name)

    def save(self, *args, **kwargs):
        super(Unit, self).save(*args, **kwargs)
