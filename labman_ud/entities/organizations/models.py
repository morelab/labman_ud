# -*- encoding: utf-8 -*-

import os

from django.db import models
from django.template.defaultfilters import slugify
from entities.core.models import BaseModel


ORGANIZATION_TYPES = (
    ('Company', 'Company'),
    ('Educational organization', 'Educational organization'),
    ('Foundation', 'Foundation'),
    ('Public administration', 'Public administration'),
    ('Research centre', 'Research centre'),
    ('University', 'University'),
)

# Create your models here.


def organization_logo_path(self, filename):
    return '%s/%s%s' % ('organizations', self.slug, os.path.splitext(filename)[-1])


###########################################################################
# Model: Organization
###########################################################################

class Organization(BaseModel):
    organization_type = models.CharField(
        max_length=75,
        choices=ORGANIZATION_TYPES,
        default='Company',
    )

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
# Model: OrganizationSeeAlso
###########################################################################

class OrganizationSeeAlso(BaseModel):
    organization = models.ForeignKey('Organization')
    see_also = models.URLField(
        max_length=512,
    )

    def __unicode__(self):
        return u'%s related resource: %s' % (self.organization.full_name, self.see_also)


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
