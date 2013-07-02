# -*- coding: utf-8 -*-
"""
Created on Tue Jul 02 11:16:22 2013

@author: aitor
"""
import csv

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