import json
import boto3
import time
import urllib.parse
import logging
import pymysql
import os

def get_qsps(event):
    return event['queryStringParameters']

def lambda_handler(event, context):
    print("Entering getRecommendations API..")
    print(event, context)
    personalizeRt = boto3.client('personalize-runtime')
    
    # if we get anything in the events['queryStringParamters'] in addition to userId
    # then we need to create a custom `context` object to pass to get_recs
    qsps = get_qsps(event)
    qspKeys = qsps.keys()
    print(qspKeys)
    
    # all filters also filter on read and disliked
    if(len(qspKeys) > 1):
        print("GOT ADDITIONAL KEYS")
        if("languageCode" in qspKeys and "includeGenres" in qspKeys):
            print("Filtering on both language and genre")
            filterArn = "arn:aws:personalize:us-east-1:005671395589:filter/filter-lang-genre-in-read-disliked-out"
        elif("languageCode" in qspKeys):
            print("Filtering on just language")
            filterArn = "arn:aws:personalize:us-east-1:005671395589:filter/filter-language-read-disliked"
        elif("includeGenres" in qspKeys):
            print("Filtering on just genre")
            filterArn = "arn:aws:personalize:us-east-1:005671395589:filter/filter-genre-in-read-disliked-out"
        else:
            filterArn = "arn:aws:personalize:us-east-1:005671395589:filter/filter-already-read-and-disliked"
        # construct a context dict based on qsps
        
        # {"languageCode" : "\"" + qsps['languageCode'] + "\""}
        filterDict = {key: "\"" + urllib.parse.unquote(value) + "\"" for (key,value) in qsps.items() if key != "userID"}
        print(filterDict)
        print("Using filter arn: " + filterArn)
        response = personalizeRt.get_recommendations(
            campaignArn = 'arn:aws:personalize:us-east-1:005671395589:campaign/book-recommendations-genre-and-lang',
            userId = qsps['userID'],
            filterArn = filterArn,
            filterValues = filterDict,
            numResults = 10
        )
    else:
        response = personalizeRt.get_recommendations(
            campaignArn = 'arn:aws:personalize:us-east-1:005671395589:campaign/book-recommendations-genre-and-lang',
            filterArn = "arn:aws:personalize:us-east-1:005671395589:filter/filter-already-read-and-disliked",
            userId = qsps['userID'],
            numResults = 10
        )
    
    recs = []
    print(response)
    # # ### BAIL-OUT FOR TESTING ###
    # bailout_response = {
    #   "statusCode": 200,
    #   "headers": {
    #     "Content-Type": "application/json"
    #   },
    #   "body": json.dumps(response)
    # }
    # return bailout_response
    
    for item in response['itemList']:
        recs.append(item['itemId'])
    
    user_name = "admin"
    password = "Bookreco123"
    rds_host = "mobypickbookreco.ctoo3wejf5nw.us-east-1.rds.amazonaws.com"
    db_name = "mobypickbookrec"
    
    try:
        conn = pymysql.connect(host=rds_host, user=user_name, passwd=password, db=db_name, connect_timeout=5)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit(1)
    
    items = []
    # substrings = ["%s"] * len(recs)
    placeholder = ", ".join(["%s"] * len(recs))
    item_count = 0
    sql_string = "SELECT * FROM Book WHERE ITEM_ID IN ({});".format(placeholder)
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(sql_string, recs)
        print("The following books were retrieved:")
        data = list(cur)
        for row in data:
            item_count += 1
            print("ROW " + str(item_count))
            print(row)
            items.append({
                'id': row.get("ITEM_ID"),
                'title': row.get("title"),
                'author': row.get("name"),
                'goodreads_url': row.get("url"),
                'poster_url' : row.get("image_url")
            })
    # dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    # table = dynamodb.Table('CompleteBookData')
    
    # items = []
    # for item in recs:
    #     book = table.scan(
    #         FilterExpression="ITEM_ID= :itemid",
    #         ExpressionAttributeValues={
    #             ":itemid": item,
    #         }
    #     )
    #     if book['Items'] and len(book['Items'])==1:
    #         bookData = book['Items'][0]
    #         items.append({
    #             'id':item,
    #             'title': bookData['original_title'],
    #             'author': bookData['name'],
    #             'goodreads_url': bookData['url'],
    #             'poster_url' : bookData['image_url']
    #         })
            
    #     else:
    #         continue
    
    # print(recs)
    
    response = {
      "statusCode": 200,
      "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin":'*'
      },
      "body": json.dumps(items)
    }
    
    print("DONE - getRecommendations API")
    return response