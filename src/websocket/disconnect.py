import json
import boto3
import os
from lib.scan_table import scan

def handler(event, context):
  # Get the connection Id from request when a user disconnects
  connectionId=event['requestContext'].get('connectionId')
  client = boto3.client('dynamodb')

  # Get data user from DynamoDB
  item = client.get_item(
          TableName=os.getenv('TABLE_NAME'),
          Key={'connectionId': {'S': connectionId}}
          )

  userName = item.get('Item').get('userName').get('S')
  
  # Deletes the user disconnected from DynamoDB
  client.delete_item(TableName=os.getenv('TABLE_NAME'), Key={"connectionId": {"S": event['requestContext'].get('connectionId')}})

  # Get all users connected
  connections_list = scan(os.getenv('TABLE_NAME'))

  endpoint_api = os.getenv('WEBSOCKET_ADDRESS')   
  apigateway_client = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint_api)

  # Send a message to all users notifying the user disconnected
  for connection in connections_list:
    apigateway_client.post_to_connection(ConnectionId=connection['connectionId'], Data=json.dumps({'action': 'userExit', 'userName': userName, 'connectionId': connectionId}))

  return {
    'statusCode': 200,
    'body': json.dumps('Disconnected from the server!')
  }