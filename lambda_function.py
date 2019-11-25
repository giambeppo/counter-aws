import json
import decimal
from botocore.exceptions import ClientError
from dynamodb_access import db_read, db_create, db_update, db_delete, db_add

print('Loading function')


def replace_decimals(obj):
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj:
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj


def respond(err, status_code, res=None):
    print(res)
    replace_decimals(res)
    return {
        'statusCode': status_code,
        'body': err if err else json.dumps(res, indent=2),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Authorization,Content-Type,X-Amz-Date,X-Amz-Security-Token,X-Api-Key'
        }
    }


def set(with_function, counter, value, updater):
    try:
        item = with_function(counter, value, updater)
        return respond(None, 200, item)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return respond(f'Counter "{counter}" does not exist', 404)
        else:
            raise e


def get(params):
    counter = params['counter']
    if 'after' in params:
        after = params['after']
        updater = params['by'] if 'by' in params else 'unknown'
        if after == 'increment':
            return set(db_add, counter, 1, updater)
        elif after == 'decrement':
            return set(db_add, counter, -1, updater)
        elif after == 'set':
            if 'newValue' in params:
                value = params['newValue']
                try:
                    value = int(value)
                except ValueError:
                    return respond(f'Invalid parameter "newValue", must be an integer: "{value}"', 400)
                return set(db_update, counter, value, updater)
            else:
                return respond(f'Missing parameter "newValue" for operation "after=set"', 400)
        else:
            return respond(f'Unknow value for parameter "after": "{after}"', 400)
    else:
        item = db_read(counter)
        if item:
            return respond(None, 200, item)
        else:
            return respond(f'Counter "{counter}" does not exist', 404)


def put(params):
    counter = params['counter']
    try:
        value = params['value'] if 'value' in params else int(0)
        try:
            value = int(value)
        except ValueError:
            return respond(f'Invalid parameter "value", must be an integer: "{value}"', 400)
        updater = params['by'] if 'by' in params else 'unknown'
        item = db_create(counter, value, updater)
        return respond(None, 201, item)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return respond(f'Counter "{counter}" exists already', 409)
        else:
            raise e


def delete(params):
    counter = params['counter']
    try:
        db_delete(counter)
        return respond(None, 204, {})
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return respond(f'Counter "{counter}" does not exist', 404)
        else:
            raise e


def post(params):
    counter = params['counter']
    updater = params['by'] if 'by' in params else 'unknown'
    value = params['value'] if 'value' in params else int(0)
    try:
        value = int(value)
    except ValueError:
        return respond(f'Invalid parameter "value", must be an integer: "{value}"', 400)
    return set(db_update, counter, value, updater)


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    operations = {
        'DELETE': delete,
        'GET': get,
        'POST': post,
        'PUT': put
    }
    operation = event['httpMethod']
    if operation in operations:
        params = event['queryStringParameters']
        return operations[operation](params)
    else:
        return respond(f'Unsupported method "{operation}"', status_code=400)
