import json, logging, datetime
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

import boto3, uuid
bot_id = 'M6HMDAMQBR'  # Replace with your Bot ID
bot_alias_id = 'TSTALIASID'  # Replace with your Bot Alias ID
locale_id = 'en_US'  # Replace with the desired locale
session_id = str(uuid.uuid4())


# Initialize the Amazon Lex runtime client


def lambda_handler(event, context):
    uid = event['queryStringParameters']['uid']
    messages = json.loads(event['body'])["messages"]
    bot_response_message = 'Oops! Something went wrong!'
    if messages:
        logger.debug(f"Got {messages}")
        lex_runtime = boto3.client('lexv2-runtime', region_name='us-east-1')  # Replace with your desired region       
        message = messages[0]['unstructured']['text']
        response = lex_runtime.recognize_text(
            botId=bot_id,
            botAliasId=bot_alias_id,
            localeId=locale_id,
            sessionId=session_id,
            sessionState={
                'sessionAttributes': {
                    'userId': uid
                },  # You can pass session attributes if needed
            },
            text=message
        )
        print("lex response: ", response)
        bot_response_message = response['messages'][0]['content']

    body = {"messages" : [bot_response_message]}
    
    
    response = {
      "statusCode": 200,
      
      "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin":'*'
      },
      "body": json.dumps(body)
    }
    print("response: ", response)
    return response