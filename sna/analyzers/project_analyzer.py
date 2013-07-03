# -*- coding: utf-8 -*-
"""
Created on Tue Jul 02 12:20:59 2013

@author: aitor
"""
from sets import Set
import network_creator as nc
import pg # TODO: delete once the queries are djangoized

class project_analyzer():

    # Creates the social network of members based on common proyects
    # Only project manager and researcher roles are taken into account.    
    def create_common_project_network(self):                        
            persons_project = self.query_persons_project()
            projects = self.__process_person_projects(persons_project)
            relations = nc.get_relations(projects)         
            #nc.export_gephi_csv_undirected(relations, 'cooperationUndirected.csv')
            return relations
    
    # Creates the socal network of projects based on common tags       
    def create_related_projects_network(self):
        projectsTags = self.query_projects_tags()
        projects = self.process_projects(projectsTags)
        tags = nc.group_by_relations(projects)
        relations = nc.get_relations(tags) 
        #nc.export_gephi_csv_undirected(relations, 'projectsUndirected.csv')
        return relations
            
    # INPUT:  [('Aitor', 'hey'), ('Unai', 'hey'), 
    #          ('Aitor', 'hoo'), ('Pablo', 'hoo')]
    # OUTPUT: {'hey': ['Aitor', 'Unai'], 'hoo': ['Aitor', 'Pablo']}
    def __process_person_projects(persons_project):
        #results = [('diego-lopez-de-ipina', 1, '4gizar'), ('juan-lopez-de-armentia', 2, '4gizar'), ('inigo-elejalde', 2, '4gizar'), ('diego-lopez-de-ipina', 3, '4gizar')]
        cooperation = {}  
        for result in persons_project:
            name = result[0]
            project = result[1]            
            if project in cooperation.keys():
                if not result[0] in cooperation[project]:
                    cooperation[project].append(result[0])
                
            else:
                cooperation[project] = []
                cooperation[project].append(name)
        return cooperation
    
    def __process_projects_tags(projectsTags):
        projects = {}
        for project in projectsTags:
            name = project[0]
            if not name in projects.keys():
                projects[name] = Set()
            projects[name].add(project[1])
        
        return projects
 
    # ************************************************************************************    
    # TODO: All this functions must be djangoized. I'm not touching the queries until
    # then, they do not work rigth now, only for "documentation" purposes
    # ************************************************************************************            
            
    def query_persons_project():
        query_persons_project = ("select persons_person.slug, projects_project.slug "
        "from projects_assignedperson, persons_person, projects_project "
        "where projects_assignedperson.person_id= persons_person.id "
        "and projects_assignedperson.project_id = projects_project.id "
        "and projects_assignedperson.role_id <> 3 " # Only researchers and project managers are taken into account
        "order by projects_project.id ")
                
        con = pg.connect(dbname='labman', host='localhost', user='')
        res = con.query(query_persons_project)
        con.close()
        return res.getresult()
        
    def query_projects_tags():
        query_project_tags = ("select projects_project.slug, utils_tag.slug "
                    "from projects_project, utils_tag, projects_projecttag "
                    "where projects_projecttag.project_id = projects_project.id "
                    "and projects_projecttag.tag_id = utils_tag.id "
                    "order by projects_project.id ")
                    
        con = pg.connect(dbname='labman', host='localhost', user='postgres')
        res = con.query(query_project_tags)
        con.close()
        return res.getresult()
