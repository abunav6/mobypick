import datetime
import re
import logging
import boto3
import time
import os
import pymysql
from boto3.dynamodb.conditions import Key, Attr

os.environ['TZ'] = 'America/New_York'
time.tzset()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

current_date = datetime.datetime.combine(datetime.date.today(), datetime.time(0,0))
language_code = {'english': 'en', 'french': 'fr', 'spanish': 'es'}


def elicit_slot(intent, slot, message):
    logger.debug("Sending new elicitation")
    logger.debug(intent)
            
    response = {
        "sessionState": {
            "sessionAttributes": {},
            "dialogAction": {
                "slotToElicit": slot,
                "type": "ElicitSlot"
            },
            "intent": intent
        },
        "messages": [
    	buildmsg(message)	
        ]
    }

    logger.debug(response)
    return response


def buildmsg(msg):
    return {'contentType': 'PlainText', 'content': msg}

def get_value(slots, field):
    if not slots[field]:
        return None
    try:
        return slots[field]['value']['resolvedValues'][0]
    except:
        return 'INVALID'
        

def get_latest_recommendation(user_id, genre, language):
    personalizeRt = boto3.client('personalize-runtime')
    if language:
        language = language_code[language.lower()]
    # all filters also filter on read and disliked
    if genre is not None or language is not None:
        print("GOT ADDITIONAL KEYS")
        if(genre is not None and language is not None):
            print("Filtering on both language and genre")
            filterArn = "arn:aws:personalize:us-east-1:005671395589:filter/filter-lang-genre-in-read-disliked-out"
            filterDict = {"languageCode" : "\"" + language + "\"", "includeGenres" : "\"" + genre  + "\""}
        elif(language is not None):
            print("Filtering on just language")
            filterArn = "arn:aws:personalize:us-east-1:005671395589:filter/filter-language-read-disliked"
            filterDict = {"languageCode" : "\"" + language + "\""}
        elif(genre is not None):
            print("Filtering on just genre")
            filterArn = "arn:aws:personalize:us-east-1:005671395589:filter/filter-genre-in-read-disliked-out"
            filterDict = {"includeGenres" : "\"" + genre  + "\""}
        else:
            filterArn = "arn:aws:personalize:us-east-1:005671395589:filter/filter-already-read-and-disliked"

        print(filterDict)
        response = personalizeRt.get_recommendations(
            campaignArn = 'arn:aws:personalize:us-east-1:005671395589:campaign/book-recommendations-genre-and-lang',
            userId = user_id,
            filterArn = filterArn,
            filterValues = filterDict,
            numResults = 3
        )
    else:
        response = personalizeRt.get_recommendations(
            campaignArn = 'arn:aws:personalize:us-east-1:005671395589:campaign/book-recommendations-genre-and-lang',
            filterArn = "arn:aws:personalize:us-east-1:005671395589:filter/filter-already-read-and-disliked",
            userId = user_id,
            numResults = 3
        )
    
    recs = []
    print("Personalize resp: ", response)
    
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

    return items

    
    

def lambda_handler(event, context):
    print('event = ', event)
    intent = event['sessionState']['intent']
    user_id = event['sessionState']['sessionAttributes']['userId']
    
    if intent['name'] == 'BookRecommendIntent':
        logger.info("inside BookRecommendIntent")

        slots = intent['slots']
        
        print('userId = ', user_id)
        
        genre_confirmation = get_value(slots, 'genre_confirmation')
        
        if not genre_confirmation:
            return elicit_slot(intent, 'genre_confirmation', "Do you have a genre preference? [Yes/No]")
        
        genre = get_value(slots, 'genre')
        
        if genre_confirmation.lower() == 'yes' and not genre:
            return elicit_slot(intent, 'genre', "What genre are you in the mood for?")
        if genre == "INVALID":
            return elicit_slot(intent, 'genre', "That doesn't seem right! \nCould you please enter a valid genre?")
        elif genre is not None and genre.lower() not in ['fiction', 'mystery_thriller_crime', 'romance', 'non_fiction', 'history_biography', 'fantasy_paranormal', 'children', 'young_adult', 'comics_graphic', 'poetry']:
            return elicit_slot(intent, 'genre', "We don't have any books for you in this genre :( \nCould you please enter a different one?")
    
        logger.debug("Validating language")
        
        language_confirmation = get_value(slots, 'language_confirmation')
        if not language_confirmation:
            return elicit_slot(intent, 'language_confirmation', "Do you have a language preference? [Yes/No]")
        language = get_value(slots, 'language')
        if language_confirmation.lower() == 'yes' and not language:
            return elicit_slot(intent, 'language', "What language do you prefer?")
        if language == "INVALID":
            return elicit_slot(intent, 'language', "That doesn't seem right! \nCould you please enter a valid language?")
        elif language is not None and language.lower() not in ['english', 'spanish', 'french']:
            return elicit_slot(intent, 'language', "We don't have that language yet! Please choose from this list: English, Spanish, French")
        result = []
        if user_id:
            result = get_latest_recommendation(user_id, genre, language)
        print(result)
        print(len(result))
        
        if result:
            book_messages = "I think you will enjoy reading:<br><br>" + "<br>".join([f"<a href='{book['goodreads_url']}'>Title: {book['title']}</a><br>Author: {book['author']}<br><br>" for book in result])
            print(book_messages)
        
            return {
                "sessionState": {
                    "sessionAttributes": {},
                    "dialogAction": {
                        "fulfillmentState": "Fulfilled",
                        "type": "Close"
                    },
                    "intent": intent
                },
                "messages": [buildmsg(book_messages)]
            }
        else:
            return {
                "sessionState": {
                    "sessionAttributes": {},
                    "dialogAction": {
                        "fulfillmentState": "Failed",
                        "type": "Close"
                    },
                    "intent": intent
                },
                "messages": [buildmsg("Try Again")]
           }