import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

import json

with open("./keys.json", 'r') as f:
    cfg = json.load(f)

Accees_Key_ID = cfg['AwsKeys']['Accees_Key_ID']
Secret_Access_Key = cfg['AwsKeys']['Secret_Access_Key']

f.close()

class awsDynamo:
    """A Class that handle AWS DynamoDB"""

    def __init__(self):        
        super().__init__()

        # Get the service resource.
        awsDynamo.dyn_resource = boto3.resource('dynamodb', region_name='ap-northeast-2', 
                                                aws_access_key_id=Accees_Key_ID, 
                                                aws_secret_access_key=Secret_Access_Key)
        awsDynamo.table = None


    # Push data to table
    @staticmethod
    def push(data, tName):

        awsDynamo.table = awsDynamo.dyn_resource.Table(tName)

        try:
            awsDynamo.table.put_item(
                Item = data
            )
            
            awsDynamo.table = None
            return True

        except ClientError as e:
            print(e.response['Error']['Message'])
            return False
    

    # Update Table 'linelist'
    @staticmethod
    def update(isEnd, ID, name, lNum):

        awsDynamo.table = awsDynamo.dyn_resource.Table('linelists')

        try:
            response = awsDynamo.table.update_item(
                Key={'LinePK': 'Joul', 'linenumber': lNum},
                UpdateExpression="set isEntryEnd=:b, winnerID=:wid, winnerName=:wname",
                ExpressionAttributeValues={
                    ':b': isEnd, ':wid': ID, ':wname': name},
                ReturnValues="UPDATED_NEW")
        except:
            raise

        awsDynamo.table = None
        return True
    

    # Use only on Table 'entrylist'
    @staticmethod
    def delete(line, userID):
        awsDynamo.table = awsDynamo.dyn_resource.Table('entrylist')

        try:
            awsDynamo.table.delete_item(
                Key=
                {
                    'linenumber': line,
                    'entryuserID': userID
                }
            )
        except:
            raise

        awsDynamo.table = None
        return True
    

    # Retrieve highest line number
    @staticmethod
    def getLineNumber():

        awsDynamo.table = awsDynamo.dyn_resource.Table('linelists')
        rs = awsDynamo.table.query(
            ProjectionExpression="linenumber",
            KeyConditionExpression=Key('LinePK').eq('Joul'),
            ScanIndexForward = False,
            Limit = 1
        )

        awsDynamo.table = None
        return rs['Items'][0]['linenumber']
    

    # Retrieve highest line number
    @staticmethod
    def getLogNumber():

        awsDynamo.table = awsDynamo.dyn_resource.Table('log')
        rs = awsDynamo.table.query(
            ProjectionExpression="logNumber",
            KeyConditionExpression=Key('LOG').eq('LOG'),
            ScanIndexForward = False,
            Limit = 1
        )

        awsDynamo.table = None
        return rs['Items'][0]['logNumber']
    

    # Retrieve user list who entered
    @staticmethod
    def getEntryUsers(lNum):

        awsDynamo.table = awsDynamo.dyn_resource.Table('entrylist')
        
        rs = awsDynamo.table.query(
            ProjectionExpression="entryuserID, entryuserName",
            KeyConditionExpression=Key('linenumber').eq(lNum),
            ScanIndexForward = False,
        )
        
        # List
        return rs['Items']


    # Check there is a user on the list who reqeust entry
    @staticmethod
    def checkExist(lNum, userID):

        awsDynamo.table = awsDynamo.dyn_resource.Table('entrylist')

        rs = awsDynamo.table.query(
            ProjectionExpression="entryuserID",
            KeyConditionExpression=Key('linenumber').eq(lNum) & Key('entryuserID').eq(userID),
            ScanIndexForward = False,
            Limit=1
        )

        try:
            if (len(rs['Items']) == 0):
                awsDynamo.table = None
                return False

            if (userID == rs['Items'][0]['entryuserID']):
                awsDynamo.table = None
                return True
        except:
            awsDynamo.table = None
            raise

        return False