# -*- coding: utf-8 -*-
"""
Created on Tue Jul 02 11:15:32 2013

@author: aitor
"""
from sets import Set
from datetime import date
import network_creator as nc
import pg # TODO: delete once the queries are djangoized


class expertise_analyzer():
    
    # Infers the person expertise using the project+paper tags
    # Input: {'clustering': 2, 'social-networks': 2, 'mobile-applications': 1, 'data-mining': 2, 
    #          'natural-language-processing': 2, 'persuasive-technologies': 1, 'android': 1, 
    #          'social-network-analysis': 2, 'emergency-management': 2, 'intelligent-objects': 1}    
    def __infer_person_expertise(self, tags_values):
        # TODO: Completely arbitrary number, we should fine tune it according to the 
        # results with the final model.
        magic_expertise_percentage = 0.3    
        
        # Tags sorted from high to low weight value
        sorted_tags = sorted(tags_values, key=tags_values.get, reverse=True)
        
        # Knowledge accummulaed by a person
        total_knowledge_weight = 0
        for v in tags_values.values():
            total_knowledge_weight += v
            
        expertise_weight = total_knowledge_weight * magic_expertise_percentage
        
        accum_knowledge = 0    
        expertise_tags = []
        for tag in sorted_tags:
            if accum_knowledge > expertise_weight:
                break
            expertise_tags.append(tag)
            accum_knowledge += tags_values[tag]
            
        return expertise_tags
    
    # Infers the expertise for all the members of the research group
    # INPUT: {'foo': {'ambient-intelligence': 1, 'aal': 1, 'osgi': 1, 'domotic': 1, 'elders': 1}, 
    #         'bar': {'clustering': 2, 'social-networks': 2, 'mobile-applications': 1, 
    #                  'data-mining': 2, 'natural-language-processing': 2, 'persuasive-technologies': 1, 
    #                  'android': 1, 'social-network-analysis': 2, 'emergency-management': 2, 
    #                  'intelligent-objects': 1}
    #        }             
    def process_expertise(self, persons_tags):
        persons_expertise = {}
        for person in persons_tags:
            expertise = self.__infer_person_expertise(persons_tags[person])
            persons_expertise[person] = expertise
        return persons_expertise   
    
    # Based on the person expertises recovers their chronological evolution   
    def get_expertise_year(self, person, expertises): 
        startYear = 2004 # TODO change it to the first year of the person in the lab 
        endYear = date.today().year   
        
        expertise_year = {}
        for expertise in expertises:
            years = []
            for year in range(startYear, endYear+1):
                expertise_year_value = self.query_expertise_person_year(expertise, person, year)
                years.append(expertise_year_value)
            expertise_year[expertise] = years
            
        return expertise_year
        
    # Create the social network based on the expertise relations
    #  
    def create_expertise_network(self):
        slugs = self.query_person_slugs()
        persons_tags = self.add_tags(slugs)
        persons_expertise = self.process_expertise(persons_tags)
        expertises = nc.group_by_relations(persons_expertise)
        relations = nc.get_relations(expertises) 
        #nc.export_gephi_csv_undirected(relations, 'expertiseUndirected.csv')
        return relations
        
    # ************************************************************************************    
    # TODO: All this functions must be djangoized. I'm not touching the queries until
    # then, they do not work rigth now, only for "documentation" purposes
    # ************************************************************************************ 
        
    def query_persons_tags():
        query_persons_tags = ("select persons_person.slug, utils_tag.slug "
                    "from projects_assignedperson, persons_person, projects_project, utils_tag, projects_projecttag "
                    "where projects_assignedperson.person_id= persons_person.id "
                    "and projects_assignedperson.project_id = projects_project.id "
                    "and projects_assignedperson.role_id <> 3 "
                    "and projects_projecttag.project_id = projects_project.id "
                    "and projects_projecttag.tag_id = utils_tag.id "
                    "order by projects_project.id")
                
        con = pg.connect(dbname='labman', host='localhost', user='meh')
        res = con.query(query_persons_tags)
        con.close()
        return res.getresult()
    
    def query_person_tags(personSlug):
        query_person_tags = ("select utils_tag.slug "
                    "from projects_assignedperson, persons_person, projects_project, utils_tag, projects_projecttag "
                    "where projects_assignedperson.person_id= persons_person.id "
                    "and projects_assignedperson.project_id = projects_project.id "
                    "and projects_assignedperson.role_id <> 3 "
                    "and projects_projecttag.project_id = projects_project.id "
                    "and projects_projecttag.tag_id = utils_tag.id "
                    "and persons_person.slug = $1 " )
                
        con = pg.connect(dbname='labman', host='localhost', user='meh')
        res = con.query(query_person_tags, (personSlug, ))
        con.close()
        return res.getresult()
        
    def query_expertise_person_year(expertise, person, year):
        query_expertise_person_year = ("select count(projects_project.id) "
                        "from projects_project, projects_assignedperson, persons_person, projects_projecttag, utils_tag "
                        "where projects_project.start_year <= {0} "
                        "and projects_project.end_year >= {0} "
                        "and persons_person.slug = '{1}' "
                        "and utils_tag.slug = '{2}' "
                        "and utils_tag.id = projects_projecttag.tag_id "
                        "and projects_project.id = projects_projecttag.project_id "
                        "and projects_project.id = projects_assignedperson.project_id "
                        "and persons_person.id = projects_assignedperson.person_id ").format(year,person,expertise)
                    
        con = pg.connect(dbname='labman', host='localhost', user='meh')
        res = con.query(query_expertise_person_year)
        con.close()
        return res.getresult()
        
    # getting the results from query_person_tags
    def get_user_tags(results):
        tags = {}
        for r in results:
            name = r[0]
            if not name in tags.keys():
                tags[name] = Set()
            tags[name].add(r[1])
        return tags
        
    def query_person_slugs():
        query_slugs = ("select distinct persons_person.slug "
                    "from persons_person")
                
        con = pg.connect(dbname='labman', host='localhost', user='meh')
        res = con.query(query_slugs)
        con.close()
        return res.getresult()
    
    def add_tags(self, slugs):
        persons_tags = {}
        for s in slugs:
            name = s[0]
            tags = self.query_person_tags(name)
            tag_values = {}
            for t in tags:
                tag = t[0]
                if not tag in tag_values.keys():
                    tag_values[tag] = 1
                else:
                    tag_values[tag] += 1
            persons_tags[name] = tag_values
        
        return persons_tags