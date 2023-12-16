# MobyPick

Team Members:

- Anubhav Dinkar (ad6641)
- Arpan Chatterjee
- Shirley Berry
- Shruti Garg (sg7395)


## About MobyPick

We have designed and built Moby Pick, a cloud-based web
application that provides users with personalized book rec-
ommendations. The main goal of our application is to en-
courage users to broaden their horizons in their book-reading
habits and discover new books they may have otherwise over-
looked.

### Architecture

MobyPick is hosted on a load-balanced Elastic Beanstalk environment, which uses auto-scaling EC2 instances. It uses the following AWS services:
- Cognito for user authentication
- DynamoDB for user info
- RDS for complete book data
- Personalize for book recommendations
- Lex for the chatbot
- API gateway for setting up recommendation and chatbot APIs
- Lambda as an event handler for Lex and API GW
- S3 as data store for the frontend
- EventBridge to trigger weekly recommendations
- SES to send weekly recommendations to the users


## Usage

1. Visit this website

```
  https://mobypick.us-east-1.elasticbeanstalk.com/
```

2. Sign up / Log in to the website using your email ID. This will be verified, so ensure you have access to the email you're using
3. Depending on if you are a new or existing user, you will be redirected to different pages:
   - If you are new, you will be playing a book picker game, where you can select any number of books that get added to your want-to-read list. After that, you are redirected to your profile page
   - If you are a returning user, you will land on your profile page.
4. You will then have the opportunity to modify your language and genre preferences
5. You may also get personalized recommendations from our recommendation model
6. You can also speak with Ahab, our chatbot that uses NLP to understand your live preferences and recommend accordingly.


   
 


