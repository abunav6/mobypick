import json
import boto3
import urllib
from botocore.exceptions import ClientError


def send_email(subject, body, recipient):
    ses = boto3.client('ses', region_name='us-east-1')
    email_message = {
        'Subject': {'Data': subject},
        'Body': {'Html': {'Data': body}}
    }
    try:
        response = ses.send_email(
            Source="ad6641@nyu.edu",
            Destination={'ToAddresses': [recipient]},
            Message=email_message
        )
        print(response)
  
    except ClientError as e:
        print(f"err : {e}")
    

def lambda_handler(event, context):
    # fetch all users from Dynamo
    # then for each user:
    #   call Personalize recommendation on that userID
    #   get book title and URL from Dynamo
    #   put it in a msg and email to that user
    
    personalizeRt = boto3.client('personalize-runtime')

    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('UserInfo')
    campaignArn = 'arn:aws:personalize:us-east-1:005671395589:campaign/book-recommendations-genre-and-lang'
    try:
        response = table.scan()
        users = response.get('Items', [])
        if users:
            for user in users:
                uid = user['userID']
                response = personalizeRt.get_recommendations(
                    campaignArn = 'arn:aws:personalize:us-east-1:005671395589:campaign/book-recommendations-genre-and-lang',
                    userId = uid,
                    numResults = 3
                )
                if response['itemList'] and len(response['itemList'])>0:
                    recommendations = response['itemList']
                    items = {}

                    for rec in recommendations:
                        itemId = rec['itemId']
                        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                        table = dynamodb.Table('CompleteBookData')
                        
                        
                        book = table.scan(
                            FilterExpression="ITEM_ID= :itemid",
                            ExpressionAttributeValues={
                                ":itemid": itemId,
                            }
                        )
                        if book['Items'] and len(book['Items'])==1:
                            bookData = book['Items'][0]
                            items[itemId] = {
                                'title': bookData['original_title'],
                                'author': bookData['name'],
                                'goodreads_url': bookData['url'],
                        }
                                
                        else:
                            continue
                        
                    html_message = "<ul>"
                    for idx, (book_id, book_info) in enumerate(items.items(), start=1):
                        title = book_info['title']
                        author = book_info['author']
                        url = book_info['goodreads_url']
                        html_message += f"<li>{idx}. <a href='{url}' target='_blank'>{title}</a> : {author}</li>"
                    html_message += "</ul>"
                    subject = "Here's your weekly recommendation!"
                    recipient_email = user['email']
                    send_email(subject, html_message, recipient_email)


    except Exception as e:
        print(e)


    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Finished email flow')
    }
