import boto3
import os
from boto3.dynamodb.conditions import Attr
from datetime import datetime

DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'counters')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)
last_update_format = '%d/%m/%Y %H:%M:%S'


def now():
    return datetime.now().strftime(last_update_format)


def db_read(counter):
    res = table.get_item(
        Key={
            'name': counter
        })
    if 'Item' in res:
        return res['Item']
    else:
        return None


def db_create(counter, value, updater):
    item = {
        'name': counter,
        'value': value,
        'last_updater': updater,
        'last_update': now()
    }
    table.put_item(
        Item=item,
        ConditionExpression=Attr('name').not_exists())
    return item


def db_delete(counter):
    res = table.delete_item(
        Key={
            'name': counter
        },
        ConditionExpression=Attr('name').exists())


def db_update(counter, value, updater):
    item = table.update_item(
        Key={
            'name': counter
        },
        UpdateExpression='SET #val = :val, last_updater = :last_updater, last_update = :last_update',
        ExpressionAttributeNames={
            '#val': 'value'
        },
        ExpressionAttributeValues={
            ':val': value,
            ':last_updater': updater,
            ':last_update': now()
        },
        ConditionExpression=Attr('name').exists(),
        ReturnValues='ALL_NEW')
    return item['Attributes']


def db_add(counter, delta, updater):
    item = table.update_item(
        Key={
            'name': counter
        },
        UpdateExpression='SET #val = #val + :delta, last_updater = :last_updater, last_update = :last_update',
        ExpressionAttributeNames={
            '#val': 'value'
        },
        ExpressionAttributeValues={
            ':delta': delta,
            ':last_updater': updater,
            ':last_update': now()
        },
        ConditionExpression=Attr('name').exists(),
        ReturnValues='ALL_NEW')
    return item['Attributes']
