# -*- coding: utf-8 -*-
"""
Created on Tue Jul 02 11:16:22 2013

@author: aitor
"""
import csv
from sets import Set

class network_creator():
    # Creates relations from a cooperation dict. The values can be a set or a list
    # INPUT {'wireless-sensor-networks': Set(['foo, 'bar', 'meh']), 
    #        'multi-agent-systems': Set(['foo'])
    def get_relations(cooperation):
        relations = []  
        for participants in cooperation.values():
            participants = list(participants)
            for participant in participants:
                    ind = participants.index(participant)
                    for i in range(ind+1, len(participants)):
                        if participant != participants[i]: 
                            relations.append([participant, participants[i]])       
        return relations        
        
    # Exports the relations as an undirected csv file for gephi.
    # TODO: Change it to proteus
    def export_gephi_csv_undirected(relations, filename):
        with open('./data/' + filename, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            for relation in relations:
                writer.writerow(relation)
                
    # Groups elements(projects, users, papers...) by their relations (tags, projects, papers...)
    # INPUT: {'foo': ['ambient-intelligence', 'aal'], 
    #         'bar': ['clustering', 'social-networks', 'aal'],
    #         'meh': ['clustering']}
    # OUTPUT: {'aal':['foo', 'bar'],
    #           'clustering': ['bar', 'meh']}
    def group_by_relations(elements):
        tags = {}
        for element in elements:
            for tag in elements[elements]:
                if not tag in tags.keys():
                    tags[tag] = Set()
                tags[tag].add(element)
        return tags
