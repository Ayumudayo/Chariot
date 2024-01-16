import boto3
import json
import os

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

class AwsDynamo:
    """A Class that handles AWS DynamoDB"""

    def __init__(self, credentials_file='./keys.json', region_name='ap-northeast-2'):
        with open(credentials_file, 'r') as f:
            cfg = json.load(f)
        
        access_key_id = os.getenv('Accees_Key_ID')
        secret_access_key = os.getenv('Secret_Access_Key')
        
        self.dyn_resource = boto3.resource(
            'dynamodb', 
            region_name=region_name, 
            aws_access_key_id=access_key_id, 
            aws_secret_access_key=secret_access_key
        )
    
    def _get_table(self, table_name):
        return self.dyn_resource.Table(table_name)

    def push(self, data, table_name):
        table = self._get_table(table_name)
        try:
            table.put_item(Item=data)
            return True
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False

    def update(self, isEnd, ID, name, lNum):
        table = self._get_table('linelists')
        try:
            table.update_item(
                Key={'LinePK': 'Joul', 'linenumber': lNum},
                UpdateExpression="set isEntryEnd=:b, winnerID=:wid, winnerName=:wname",
                ExpressionAttributeValues={
                    ':b': isEnd, ':wid': ID, ':wname': name
                },
                ReturnValues="UPDATED_NEW"
            )
            return True
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False

    def delete(self, line, userID):
        table = self._get_table('entrylist')
        try:
            table.delete_item(
                Key={
                    'linenumber': line,
                    'entryuserID': userID
                }
            )
            return True
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False

    def _query_table(self, table_name, **kwargs):
        table = self._get_table(table_name)
        return table.query(**kwargs)

    def getLineNumber(self):
        response = self._query_table(
            'linelists',
            ProjectionExpression="linenumber",
            KeyConditionExpression=Key('LinePK').eq('Joul'),
            ScanIndexForward=False,
            Limit=1
        )
        return response['Items'][0]['linenumber']

    def getLogNumber(self):
        response = self._query_table(
            'log',
            ProjectionExpression="logNumber",
            KeyConditionExpression=Key('LOG').eq('LOG'),
            ScanIndexForward=False,
            Limit=1
        )
        return response['Items'][0]['logNumber']

    def getEntryUsers(self, lNum):
        response = self._query_table(
            'entrylist',
            ProjectionExpression="entryuserID, entryuserName",
            KeyConditionExpression=Key('linenumber').eq(lNum),
            ScanIndexForward=False
        )
        return response['Items']

    def checkExist(self, lNum, userID):
        response = self._query_table(
            'entrylist',
            ProjectionExpression="entryuserID",
            KeyConditionExpression=Key('linenumber').eq(lNum) & Key('entryuserID').eq(userID),
            ScanIndexForward=False,
            Limit=1
        )
        return bool(response['Items']) and userID == response['Items'][0]['entryuserID']


if __name__ == '__main__':
    with open("./keys.json", 'r') as f:
        cfg = json.load(f)

    aws_client = AwsDynamo(
        access_key_id=cfg['AwsKeys']['Accees_Key_ID'],
        secret_access_key=cfg['AwsKeys']['Secret_Access_Key']
    )
