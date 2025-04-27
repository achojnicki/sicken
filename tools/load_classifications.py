#!/usr/bin/env python3

from platform import system

import yaml
import json
import pymongo
import pprint

mongo_cli=pymongo.MongoClient()
mongo_db=mongo_cli['sicken']

mongo_classification_definitions=mongo_db['classification_definitions']
mongo_classification_gropus=mongo_db['classification_groups']



with open('/opt/sicken/files/sicken/classifications.yaml' if system()=='Linux' or system()=='Darwin' else 'C:\\sicken\\files\\sicken\\classifications.yaml' ,'r') as file:
    data=yaml.safe_load(file.read())

new_data={}


def add_classification_group(classification_group_uuid, classification_group_name, **kwargs):
    document={
        "classification_group_uuid": classification_group_uuid,
        "classification_group_name": classification_group_name
        }

    mongo_classification_gropus.insert_one(document)


def add_classification_definition(classification_uuid, classification_name, classification_description, classification_group_uuid, **kwargs):
    document={
        "classification_uuid": classification_uuid,
        "classification_name": classification_name,
        "classification_description": classification_description,
        "classification_group_uuid": classification_group_uuid
    }
    mongo_classification_definitions.insert_one(document)



for classification_group in data:
    add_classification_group(**data[classification_group])

    for classification in data[classification_group]['classifications']:
        add_classification_definition(**data[classification_group]['classifications'][classification], classification_group_uuid=classification_group)


#mongo_classification_definitions.create_index(
#    [
#        ('classification_group_name', pymongo.TEXT)],
#    name='classifications_names',
#    default_language='english'
#)