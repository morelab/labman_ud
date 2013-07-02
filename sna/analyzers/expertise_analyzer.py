# -*- coding: utf-8 -*-
"""
Created on Tue Jul 02 11:15:32 2013

@author: aitor
"""
from sets import Set


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
    
        
    # Groups persons according to their expertise to identify relations    
    # INPUT: {'foo': ['ambient-intelligence', 'aal'], 
    #         'bar': ['clustering', 'social-networks', 'aal'],
    #         'meh': ['clustering']}
    # OUTPUT: {'aal':['foo', 'bar'],
    #           'clustering': ['bar', 'meh']}
    def group_by_expertise(self, persons_expertise):
        expertises = {}
        for person in persons_expertise:
            for tag in persons_expertise[person]:
                if not tag in expertises.keys():
                    expertises[tag] = Set()
                expertises[tag].add(person)
        return expertises