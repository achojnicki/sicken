#!/usr/bin/env python3

from platform import system

import yaml
import json
import pymongo
import pprint

mongo_cli=pymongo.MongoClient()
mongo_db=mongo_cli['sicken']

mongo_knowledge=mongo_db['knowledge']
mongo_knowledge_gropus=mongo_db['knowledge_groups']



with open('/opt/sicken/files/sicken/knowledge.yaml' if system()=='Linux' or system()=='Darwin' else 'C:\\sicken\\files\\sicken\\knowledge.yaml' ,'r') as file:
    data=yaml.safe_load(file.read())

new_data={}


def add_knowledge_group(knowledge_group_uuid, knowledge_group_name, knowledge_group_description, **kwargs):
    document={
        "knowledge_group_uuid": knowledge_group_uuid,
        "knowledge_group_name": knowledge_group_name,
        "knowledge_group_description": knowledge_group_description
        }

    mongo_knowledge_gropus.insert_one(document)


def add_knowledge(knowledge_uuid, knowledge_name, knowledge_description, knowledge_group_uuid, knowledge_value, **kwargs):
    document={
        "knowledge_uuid": knowledge_uuid,
        "knowledge_name": knowledge_name,
        "knowledge_description": knowledge_description,
        "knowledge_group_uuid": knowledge_group_uuid,
        "knowledge_value": knowledge_value
    }
    mongo_knowledge.insert_one(document)



for knowledge_group in data:
    add_knowledge_group(**data[knowledge_group])

    for knowledge in data[knowledge_group]['knowledge']:
        add_knowledge(**data[knowledge_group]['knowledge'][knowledge], knowledge_group_uuid=knowledge_group)


#mongo_classification_definitions.create_index(
#    [
#        ('classification_group_name', pymongo.TEXT)],
#    name='classifications_names',
#    default_language='english'
#)