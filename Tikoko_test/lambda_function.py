import json
import logging
import time
import uuid
import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = 'tinkoko'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)


def lambda_handler(event, context):
    resource = event['resource']
    http_method = event['httpMethod']
    path_parameters = event['pathParameters'] if 'pathParameters' in event else {
    }
    query_parameters = event.get('queryStringParameters')
    if query_parameters is None:
        query_parameters = {}
    request_body = json.loads(event['body']) if event.get('body') else {}

    if resource == '/create-user' and http_method == 'POST':
        return create_user(request_body)
    elif resource == '/create-product' and http_method == 'POST':
        return create_product(request_body)
    elif resource == '/get-user/{id}' and http_method == 'GET':
        user_id = path_parameters['id']
        return get_user(user_id)
    elif resource == '/get-username/{userName}' and http_method == 'GET':
        username = path_parameters['userName']
        return get_userName(username)
    elif resource == '/update-user/{id}' and http_method == 'PUT':
        user_id = path_parameters['id']
        return update_user(user_id, request_body)
    elif resource == '/list-product' and http_method == 'GET':
        return list_products(query_parameters)
    else:
        return {
            'statusCode': 404,
            'body': 'Resource not found.'
        }


def create_user(request_body):
    try:
        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'activateUser': request_body.get('activateUser', False),
            'currency': request_body.get('currency', ''),
            'lastName': request_body.get('lastName', ''),
            'email': request_body.get('email', ''),
            'firstName': request_body.get('firstName', ''),
            'phone': request_body.get('phone', ''),
            'role': request_body.get('role', ''),
            'userName': request_body.get('userName', '')
        }

        response = table.put_item(Item=user_data)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            response_payload = {
                'id': user_id,
                'activateUser': user_data['activateUser'],
                'createdAt': str(int(time.time() * 1000)),
                'currency': user_data['currency'],
                'lastName': user_data['lastName'],
                'email': user_data['email'],
                'firstName': user_data['firstName'],
                'phone': user_data['phone'],
                'role': user_data['role'],
                'userId': user_data['userName']
            }

            return {
                'statusCode': 200,
                'body': json.dumps(response_payload)
            }
        else:
            return {
                'statusCode': 500,
                'body': 'Error creating user: Put item operation failed.'
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error creating user: {str(e)}'
        }


def create_product(request_body):
    # Generate a unique ID for the product
    product_id = str(uuid.uuid4())

    # Extract the necessary information from the request body
    category = request_body.get('category')
    city = request_body.get('city')
    count = request_body.get('count')
    country = request_body.get('country')
    description = request_body.get('description')
    images = request_body.get('images')
    price = request_body.get('price')
    product_name = request_body.get('productName')
    quantity = request_body.get('quantity')
    sub_category = request_body.get('subCategory')
    seller_id = request_body.get('sellerId')
    weight = request_body.get('weight')

    # Create the product item to be saved in DynamoDB
    product_item = {
        'id': product_id,
        'category': category,
        'city': city,
        'count': count,
        'country': country,
        'description': description,
        'images': images,
        'price': price,
        'productName': product_name,
        'quantity': quantity,
        'subCategory': sub_category,
        'sellerId': seller_id,
        'weight': weight
    }

    try:
        # Save the product item to DynamoDB
        table.put_item(Item=product_item)

        # Create the response payload
        response_payload = {
            'id': product_id,
            'category': category,
            'city': city,
            'count': count,
            'country': country,
            'createdAt': str(table.creation_date_time),
            'description': description,
            'images': images,
            'price': price,
            'productName': product_name,
            'quantity': quantity,
            'subCategory': sub_category,
            'sellerId': seller_id,
            'weight': weight
        }

        # Return the response payload
        return {
            'statusCode': 200,
            'body': json.dumps(response_payload)
        }

    except Exception as e:
        # Handle any errors that occur during the creation of the product
        return {
            'statusCode': 500,
            'body': f'Error creating product: {str(e)}'
        }


def get_user(user_id):
    try:
        response = table.get_item(
            Key={
                'id': user_id

            }
        )

        # Check if the user record exists
        if 'Item' in response:
            user = response['Item']
            user_data = {
                'id': user['id'],
                'activateUser': user['activateUser'],
                'currency': user['currency'],
                'lastName': user['lastName'],
                'email': user['email'],
                'firstName': user['firstName'],
                'phone': user['phone'],
                'role': user['role'],
                'userId': user['userName']
            }

            return {
                'statusCode': 200,
                'body': json.dumps(user_data)
            }
        else:
            return {
                'statusCode': 404,
                'body': 'User not found.'
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }


def get_userName(username):
    try:
        response = table.scan(
            FilterExpression='userName = :username',
            ExpressionAttributeValues={':username': username}
        )

        # Check if the user record exists
        if 'Item' in response:
            user = response['Item']
            user_data = {
                'id': user['id'],
                'activateUser': user['activateUser'],
                'currency': user['currency'],
                'lastName': user['lastName'],
                'email': user['email'],
                'firstName': user['firstName'],
                'phone': user['phone'],
                'role': user['role'],
                'userId': user['userName']
            }

            return {
                'statusCode': 200,
                'body': json.dumps(user_data)
            }
        else:
            return {
                'statusCode': 404,
                'body': 'User not found.'
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }


def update_user(user_id, request_body):
    try:
        response = table.get_item(
            Key={'id': user_id}
        )
        user = response['Item']

        if 'photo' in request_body:
            user['photo'] = request_body['photo']
        if 'verificationMeans' in request_body:
            user['verificationMeans'] = request_body['verificationMeans']
        if 'idNumber' in request_body:
            user['idNumber'] = request_body['idNumber']

        table.put_item(Item=user)

        response_payload = {
            'id': user_id,
            'activateUser': user.get('activateUser', False),
            'createdAt': str(user.get('createdAt', 0)),
            'currency': user.get('currency', ''),
            'lastName': user.get('lastName', ''),
            'email': user.get('email', ''),
            'firstName': user.get('firstName', ''),
            'phone': user.get('phone', ''),
            'role': user.get('role', []),
            'userId': user.get('userName', ''),
            'photo': user.get('photo', []),
            'verificationMeans': user.get('verificationMeans', ''),
            'idNumber': user.get('idNumber', '')
        }

        return {
            'statusCode': 200,
            'body': json.dumps(response_payload)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def list_products(query_parameters):
    limit = int(query_parameters.get('limit', 10))
    seller_id = query_parameters.get('sellerId')

    try:
        response = table.scan(
            Limit=limit,
            FilterExpression='sellerId = :sellerId',
            ExpressionAttributeValues={':sellerId': seller_id}
        )

        items = response.get('Items', [])

        response_payload = {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'isBase64Encoded': False,
            'body': json.dumps({
                'length': len(items),
                'items': items,
                'LastEvaluatedKey': response.get('LastEvaluatedKey')
            })
        }

        return response_payload

    except Exception as e:
        return {
            'isBase64Encoded': False,
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
