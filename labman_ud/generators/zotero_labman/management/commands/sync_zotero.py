#encoding: utf-8 

from django.core.management.base import NoArgsCommand
from django.template.defaultfilters import slugify

from django.conf import settings
from generators.zotero_labman.models import ZoteroLog
from entities.events.models import Event, EventType
from entities.publications.models import Publication, PublicationType, PublicationAuthor, PublicationTag
from entities.organizations.models import Organization, OrganizationType
from entities.utils.models import Language, Tag
from entities.persons.models import Person
from entities.projects.models import Project, RelatedPublication

from pyzotero import zotero
from dateutil import parser
from datetime import datetime

import requests
import os
import re
import operator

# Dict with supported Zotero's itemTypes, translated to LabMan's PublicationTypes
SUPPORTED_ITEM_TYPES = {
    'bookSection': 'Book section', 
    'book': 'Book',
    'journalArticle': 'Journal article',
    'magazineArticle': 'Journal article',
    'newspaperArticle': 'Journal article',
    'thesis': 'PhD thesis',
    'report': 'Technical Report',
    'patent': 'Misc',
    'presentation': 'Misc',
    'document': 'Misc',
    'conferencePaper': 'Conference paper',
}

class Command(NoArgsCommand):
    can_import_settings = True

    help = 'Synchronizes Labman\'s publications DB with data from your Zotero library.'

    def handle_noargs(self, **options):
        self.__api_key = getattr(settings, 'ZOTERO_API_KEY', None)
        self.__library_id = getattr(settings, 'ZOTERO_LIBRARY_ID', None)
        self.__library_type = getattr(settings, 'ZOTERO_LIBRARY_TYPE', None)
        self.__media_root = getattr(settings, 'MEDIA_ROOT', None)
        self.__api_limit = 10

        # Get slugs of the projects for tag comparision
        project_slugs = Project.objects.all().order_by('slug').values('slug')
        self.__project_slugs = [slug['slug'] for slug in project_slugs] 
        
        # TODO: Check variables

        # Get last version synced from the DB log
        try:
            last_version_db = ZoteroLog.objects.all().order_by('-created')[0].version
        except:
            last_version_db = 0

        self.__parse_last_items(last_version_db)
        if last_version_db != 0:
            self.__sync_deleted_items(last_version_db)

    def __get_last_library_version_zotero(self):
        r = requests.get('https://api.zotero.org/'+  self.__library_type + 's/'+ self.__library_id + '/items?format=versions&key=' + self.__api_key)
        return max(r.json().items(), key=operator.itemgetter(1))[1]


    def __parse_last_items(self, version=0, prefix='[NEW_ITEMS_SYNC]'):
        zot = zotero.Zotero(self.__library_id, self.__library_type, self.__api_key)

        # Get last version number in zotero to insert in DB log as last version synced
        last_version = self.__get_last_library_version_zotero()

        if version == last_version:
            print prefix, 'Labman is already updated to last version in Zotero (%i)! :-)' % (last_version)
        else:
            if version > last_version:
                # This should not happend anytime, but in this case, we solve the error by syncing the penultimate version in Zotero
                print prefix, 'Labman version number (%i) is higher than Zotero\'s one (%i)... :-/ Solving the error...' % (version, last_version)
                version = last_version - 1

            print prefix, 'Getting items since version', version
            print prefix, 'Last version in Zotero is', last_version
            print '\n'

            gen = zot.makeiter(zot.items(limit=self.__api_limit, order='dateModified', sort='desc', newer=version))

            lastitems = []

            moreitems = True
            while moreitems:
                try:
                    items = gen.next()
                except StopIteration:
                    moreitems = False

                if items and items != lastitems:
                    for item in items:
                        if item['itemType'] in SUPPORTED_ITEM_TYPES:
                            try:
                                pub = ZoteroLog.objects.filter(zotero_key=item['key']).order_by('-created')[0].publication
                                # Delete publication if exists
                                print prefix, 'Item already exists! Deleting...'

                                # Delete file if has attachment:
                                if str(pub.pdf):
                                    os.remove(self.__media_root + '/' + str(pub.pdf))
                                # Delete object in DB
                                pub.delete()
                            except:
                                pass
                            
                            # Create new publication
                            print prefix, 'Creating new publication...', item['title']
                            pub = None
                            pub, authors, tags, observations = self.__save_publication(item)
                            if observations:
                                print prefix, 'Saved but...', observations

                            # Create new log entry
                            zotlog = ZoteroLog(zotero_key=item['key'], updated=parser.parse(item['updated']), version=last_version, observations=observations)

                            # A second connection to Zotero API is needed for the retrieval of children, otherwise the iterator stops
                            zot_children = zotero.Zotero(self.__library_id, self.__library_type, self.__api_key)
                            children = zot_children.children(item['key'])
                            
                            for child in children:
                                if child['itemType'] == 'attachment' and child['contentType'] == 'application/pdf':
                                    print prefix, 'Getting attachment: ' + child['filename'] + '...'

                                    r = requests.get('https://api.zotero.org/'+  self.__library_type + 's/'+ self.__library_id + '/items/'+ child['key'] + '/file?key=' + self.__api_key)

                                    pdf_path = self.__get_publication_path(pub)

                                    # If the directory doesn't exist, create it
                                    pdf_dir = self.__media_root + '/' + os.path.dirname(pdf_path)
                                    if not os.path.exists(pdf_dir):
                                        os.makedirs(pdf_dir)

                                    with open(self.__media_root + '/' + pdf_path, 'wb') as pdffile:
                                        pdffile.write(r.content)

                                    pub.pdf = pdf_path
                                    zotlog.attachment = True

                            print prefix, 'Saving into DB...'
                            # Save publication
                            pub.save()

                            # Saving authors and tags (many-to-many fields)
                            order = 1
                            for author in authors:
                                pubauth = PublicationAuthor(
                                    author=author,
                                    publication=pub,
                                    position=order
                                )
                                pubauth.save()
                                order += 1
                            for tag in tags:
                                pubtag = PublicationTag(
                                    publication=pub,
                                    tag=tag
                                )
                                pubtag.save()

                                # Find publication - project relations through tags
                                if tag.name in self.__project_slugs:
                                    print prefix, 'Saving found publication-project relationship:', tag.name
                                    pubproj = RelatedPublication(publication=pub, project=Project.objects.get(slug=tag))
                                    pubproj.save()

                            # Save log
                            zotlog.publication = pub
                            zotlog.save()
                            print prefix, 'OK!'

                            print '-'*30
                    lastitems = items

    def __sync_deleted_items(self, version, prefix='[DELETE_SYNC]'):
        zot = zotero.Zotero(self.__library_id, self.__library_type, self.__api_key)

        # Get last version number in zotero to insert in DB log as last version synced
        last_version = self.__get_last_library_version_zotero()

        if version == last_version:
            print prefix, 'Labman is already updated to last version in Zotero (%i)! :-)' % (last_version)
        else:
            if version > last_version:
                # This should not happend anytime, but in this case, we solve the error by syncing the penultimate version in Zotero
                print prefix, 'Labman version number (%i) is higher than Zotero\'s one (%i)... :-/ Solving the error...' % (version, last_version)
                version = last_version - 1

            print prefix, 'Getting removed items since version', version
            print prefix, 'Last version in Zotero is', last_version
            print '\n'

            gen = zot.makeiter(zot.trash(limit=self.__api_limit, order='dateModified', sort='desc', newer=version))

            lastitems = []

            moreitems = True
            while moreitems:
                try:
                    items = gen.next()
                except StopIteration:
                    moreitems = False

                if items and items != lastitems:
                    for item in items:
                        if item['itemType'] in SUPPORTED_ITEM_TYPES:
                            try:
                                pub = ZoteroLog.objects.filter(zotero_key=item['key']).order_by('-created')[0].publication
                                print prefix, 'Deleting ', item['title'], '...'

                                # Delete file if has attachment:
                                if str(pub.pdf):
                                    os.remove(self.__media_root + '/' + str(pub.pdf))
                                # Delete object in DB
                                pub.delete()

                                zotlog = ZoteroLog(zotero_key=item['key'], updated=parser.parse(item['updated']), version=last_version, delete=True, publication=None)
                                zotlog.save()
                                print '-'*30
                            except:
                                pass
                    lastitems = items

    def __get_publication_path(self, pub):
        # if the publication is presented at any event (conference, workshop, etc.), it will be stored like:
        #   publications/2012/ucami/title-of-the-paper.pdf
        if pub.presented_at:
            sub_folder = pub.presented_at.slug

        # otherwise, it will be stored like:
        #   publications/2012/book-chapter/title-of-the-paper.pdf
        else:
            sub_folder = pub.publication_type.slug

        return '%s/%s/%s/%s' % ('publications', pub.year, sub_folder, slugify(str(pub.title.encode('utf-8'))) + '.pdf')

    def __save_publication(self, item):
        pub = Publication()

        observations = ''

        # Publicaton type
        pub.publication_type, created = PublicationType.objects.get_or_create(name=SUPPORTED_ITEM_TYPES[item['itemType']])

        # Publication language
        pub.language, created = Language.objects.get_or_create(name=item['language']) if 'language' in item and item['language'] else (None, False)
        
        # Publication date / year
        try:
            pub.published = parser.parse(item['date'])
            pub.year = pub.published.year
        except:
            year = re.findall(r'\d{4}', item['date'])
            if year:
                pub.published = datetime(int(year[0]),1,1)
                pub.year = year[0]
            else:
                pub.published = None
                pub.year = '2030'
                observations = 'Error getting year from ', item['date']

        # University
        if 'university' in item and item['university']:
            organization_type, created = OrganizationType.objects.get_or_create(name='University')
            pub.university, created = Organization.objects.get_or_create(full_name=item['university'], 
                defaults={'organization_type': organization_type})

        # Common attributes for all publications
        pub.title = item['title']
        pub.abstract = item['abstractNote']
        pub.short_title = item['shortTitle'] if 'shortTitle' in item and item['shortTitle'] else None
        pub.doi = item['DOI'] if 'DOI' in item and item['DOI'] else None       
        pub.pages = item['pages'] if 'pages' in item and item['pages'] else None
        pub.issue = item['issue'] if 'issue' in item and item['issue'] else None
        pub.book_title = item['bookTitle'] if 'bookTitle' in item and item['bookTitle'] else None

        # Attributes that can be both from publications and "parent" publications
        pub_subpub_attributes = {
            'journal_abbreviation': item['journalAbbrevation'] if 'journalAbbrevation' in item and item['journalAbbrevation'] else None,
            'series': item['series'] if 'series' in item and item['series'] else None,
            'series_number': item['seriesNumber'] if 'seriesNumber' in item and item['seriesNumber'] else None,
            'volume': item['volume'] if 'volume' in item and item['volume'] else None,
            'publisher': item['publisher'] if 'publisher' in item and item['publisher'] else None,
            'edition': item['edition'] if 'edition' in item and item['edition'] else None,
            'series_text': item['seriesText'] if 'seriesText' in item and item['seriesText'] else None,
            'isbn': item['ISBN'] if 'ISBN' in item and item['ISBN'] else None,
            'issn': item['ISSN'] if 'ISSN' in item and item['ISSN'] else None,
            'year': pub.year,
        }

        # If conference paper, create Conference event and Proceeding parent publication
        if item['itemType'] == 'conferencePaper':
            if item['conferenceName']:
                conf_name = item['conferenceName']
            else:
                conf_name = item['proceedingsTitle']
                conf_name = conf_name.replace('proc. of the ', '')
                conf_name = conf_name.replace('Proc. of the ', '')
                conf_name = conf_name.replace('proceedings of the ', '')
                conf_name = conf_name.replace('Proceedings of the ', '')

            proceedings_title = item['proceedingsTitle'] if item['proceedingsTitle'] else item['bookTitle']
            proceedings_title = 'Proceedings of ' + conf_name if not proceedings_title else proceedings_title

            pub_type_proceedings, created = PublicationType.objects.get_or_create(name='Proceedings')

            pub_subpub_attributes['abstract'] = proceedings_title
            proceedings, created = Publication.objects.get_or_create(
                publication_type = pub_type_proceedings,
                title = proceedings_title,
                defaults=pub_subpub_attributes
            )

            event_type_academic, created = EventType.objects.get_or_create(name='Academic event')
            pub.presented_at, created = Event.objects.get_or_create(
                full_name=conf_name, 
                defaults={
                    'event_type': event_type_academic,
                    'year': pub.published.year, 
                    'location': item['place'], 
                    'proceedings': proceedings
                }
            )

            # Relation between the publication and its parent
            pub.part_of = proceedings

        # If journal, magazine or newspaper article or book section, create parent publication
        elif item['itemType'] in ['bookSection', 'journalArticle', 'magazineArticle', 'newspaperArticle']:
            if item['itemType'] == 'bookSection':
                parentpub_type, created = PublicationType.objects.get_or_create(name='Book')
                parentpub_title = item['bookTitle'] if 'bookTitle' in item and item['bookTitle'] else 'Book ?'
            elif item['itemType'] == 'journalArticle':
                parentpub_type, created = PublicationType.objects.get_or_create(name='Journal')
                parentpub_title = item['journal_abbreviation'] if 'journalAbbrevation' in item and item['journalAbbrevation'] else 'Journal ?'
            elif item['itemType'] == 'magazineArticle':
                parentpub_type, created = PublicationType.objects.get_or_create(name='Magazine')
                parentpub_title = item['publication'] if 'publication' in item and item['publication'] else 'Magazine ?'
            elif item['itemType'] == 'newspaperArticle':
                parentpub_type, created = PublicationType.objects.get_or_create(name='Newspaper')
                parentpub_title = item['publication'] if 'publication' in item and item['publication'] else 'Newspaper ?'

            pub_subpub_attributes['abstract'] = ' '
            parentpub, created = Publication.objects.get_or_create(
                publication_type = parentpub_type,
                title = parentpub_title,
                defaults=pub_subpub_attributes
            )

            # Relation between the publication and its parent
            pub.part_of = parentpub

        # If it has no parent publication, all those attributes go to publication itself
        else:
            pub.__dict__.update(pub_subpub_attributes)    

        # Authors
        # We save them later (when we save pub in DB) (many-to-many fields)
        authors = []
        for creator in item['creators']:
            if creator['creatorType'] == 'author':
                # TODO: Author searching with Aitor Almeida's awesome IF
                author_slug = slugify(str(creator['firstName'].encode('utf-8')) + ' ' + str(creator['lastName'].encode('utf-8')))
                try:
                    a = Person.objects.get(slug__icontains=author_slug)
                except:
                    a = Person(
                        first_name=creator['firstName'],
                        first_surname=creator['lastName']
                        )
                    a.save()
                authors.append(a)
        
        # Tags
        tags = []

        for tag in item['tags']:
            t, created = Tag.objects.get_or_create(
                slug=slugify(str(tag['tag'].encode('utf-8'))),
                defaults={'name': tag['tag']}
            )
            tags.append(t)

        return pub, authors, tags, observations