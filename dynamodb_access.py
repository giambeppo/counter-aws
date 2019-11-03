import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('counters')


def db_read(counter):
  res = table.get_item(
    Key={
      'name': counter
    })
  if 'Item' in res:
    return res['Item']
  else:
    return None


def db_create(counter, value):
  item = {
    'name': counter,
    'value': value
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
  

def db_update(counter, value):
  item = table.update_item(
    Key={
      'name': counter
    },
    UpdateExpression='SET #val = :val',
    ExpressionAttributeNames={
      '#val': 'value'
    },
    ExpressionAttributeValues={
      ':val': value
    },
    ConditionExpression=Attr('name').exists(),
    ReturnValues='ALL_NEW')
  return item['Attributes']
  

def db_add(counter, delta):
  item = table.update_item(
    Key={
      'name': counter
    },
    UpdateExpression='SET #val = #val + :delta',
    ExpressionAttributeNames={
      '#val': 'value'
    },
    ExpressionAttributeValues={
      ':delta': delta
    },
    ConditionExpression=Attr('name').exists(),
    ReturnValues='ALL_NEW')
  return item['Attributes'] 

