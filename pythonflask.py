from flask import Flask, render_template,redirect,request,url_for,session

from authlib.integrations.flask_client import OAuth

import nltk
nltk.download('all')
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
import string
import psycopg2
from bs4 import BeautifulSoup
import requests
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from collections import Counter

from nltk.probability import FreqDist
# for google
from google_auth_oauthlib.flow import Flow



app = Flask(__name__)
# to google login 
app.secret_key = 'hello'  # Secret key for session management

# Path to the client secrets file
client_secrets_file = 'client_secret_289671021146-e0uk4j9gucflnqh1dbnnqkh698l9for0.apps.googleusercontent.com.json'

# Scopes define the level of access you are requesting from the user
scopes = ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'openid']
          

# Redirect URI for the OAuth flow to google
redirect_uri = 'https://dhp1.onrender.com/google/login/callback'

# Create the OAuth flow object
flow = Flow.from_client_secrets_file(client_secrets_file, scopes=scopes, redirect_uri=redirect_uri)

# to github
oauth = OAuth(app)

app.config['SECRET_KEY'] = "THIS SHOULD BE SECRET"
app.config['GITHUB_CLIENT_ID'] = "eb0d9925818407c8eecf"
app.config['GITHUB_CLIENT_SECRET'] = "06a5a99e4f3b467f549d01f30d30f86f77a6a91a"

github = oauth.register(
    name='github',
    client_id=app.config["GITHUB_CLIENT_ID"],
    client_secret=app.config["GITHUB_CLIENT_SECRET"],
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)




conn=psycopg2.connect(
        host='dpg-cnleda8l5elc73dq8j0g-a',  database='country_5aym', user='amit', password='J6O5kkf7wCcsGeN7XAgKWbL4rsMves0W')
VIEW_DATA_PASSWORD = "amit"


github_admin_usernames = ["amitsitare", "atmabodha"]

# To connetct the html
@app.route('/', methods=['POST','GET'])
def submit():

    if request.method == "POST":
      name = request.form["Name"]
      url = request.form['url']
      html = requests.get(url).text
      soup = BeautifulSoup(html, 'html.parser')
      # Sample list of classes to try
      class_list = ["_s30J clearfix","post-content entry-content","AQ4YE r31Sh","jsx-ace90f4eca22afc7 Story_description__fq_4S description paywall","articlebodycontent col-xl-9 col-lg-12 col-md-12 col-sm-12 col-12","ads__container inline-story-add inline_ad1"]

      # Initialize cleaned_text as None
      cleaned_text = None

      # Iterate over the list of classes
      for class_name in class_list:
      # Attempt to find elements using the current class
        paragraphs = soup.find_all(class_=class_name)
        
        if paragraphs:
        # If elements are found, break the loop
          cleaned_text = '\n'.join([re.sub(r'<*?>|[,?:”“";#@"]|\.{2,}', '', p.get_text()) for p in paragraphs])
          # Find the last occurrence of a full stop
          last_full_stop_index = cleaned_text.rfind('.')
          # Extract the text before the last full stop
          cleaned_text = cleaned_text[:last_full_stop_index + 1]
          break
      
      if cleaned_text is not None:
        sentence = len(sent_tokenize(cleaned_text))
        word_list = word_tokenize(cleaned_text)
        punct=['.','?','!',',_,/,@,']
        word_count=0
        for w in word_list:
          if w not in punct:
                word_count+=1
        words = word_tokenize(cleaned_text)

        # Analyze sentiment using VADER sentiment analyzer
        sentiment_analyzer = SentimentIntensityAnalyzer()
        sentiment_scores = [sentiment_analyzer.polarity_scores(word)["compound"] for word in words]

        # Calculate the overall sentiment score
        overall_score = sum(sentiment_scores)

        # Determine the sentiment interpretation
        if overall_score > 0:
            overall_sentiment = "Positive"
        elif overall_score < 0:
            overall_sentiment = "Negative"
        else:
            overall_sentiment = "Neutral"

        # Get the list of English stopwords
        stop_words = set(stopwords.words('english'))
        # to count the keyword
        filtered_tokens = [word for word in words if word.lower() not in stop_words]

        # Calculate frequency distribution
        fdist = FreqDist(filtered_tokens)

        # Get the most common words
        keywords = fdist.most_common(10)  # Change 10 to the number of keywords you wan

        # Count stopwords
        stopword_count = 0
        for word in words:
          if word.lower() in stop_words:
            stopword_count += 1
        
        # count the Upos Tag
        pos_tags = pos_tag(words, tagset='universal')
        upos_tag_count = {}  # Initialize as an empty dictionary
        for tag in pos_tags:
          upos_tag_count[tag[1]] = upos_tag_count.get(tag[1], 0) + 1

        cur=conn.cursor()
        # create table
        cur.execute("CREATE TABLE IF NOT EXISTS clean_text(id SERIAL PRIMARY KEY,Name Text,url TEXT,clean_news_text TEXT,num_sentence INTEGER,num_word INTEGER, num_stop_word INTEGER,News_Sentiment TEXT, num_post_tag TEXT,Common_Keywords TEXT)")
         # insert data into the table
        cur.execute("insert into clean_text(Name,url,clean_news_text, num_sentence, num_word,num_stop_word,News_Sentiment, num_post_tag,Common_Keywords) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    
                    (name,url,cleaned_text,sentence,word_count,stopword_count,overall_sentiment,str(upos_tag_count),keywords))
        conn.commit()
        
        return render_template('input.html', text=cleaned_text,name=name, sentences=sentence,words=word_count,stop_words=stopword_count,overall_sentiment=overall_sentiment,upos_tags=str(upos_tag_count),keywords=keywords)
      else:
         return "this News-link do not allow to processing"
      
      
    return render_template('input.html')

@app.route('/view_data', methods=['POST'])
def view_data():
    password_attempt = request.form['password']
    if password_attempt == VIEW_DATA_PASSWORD:

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM clean_text")
        data = cursor.fetchall()

        return render_template('detail.html', data=data)
    else:
        return "Incorrect password. Access denied."

# Github login route
@app.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)

# Github authorize route
@app.route('/login/github/authorize')
def github_authorize():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    session['github_token'] = token
    resp = github.get('user').json()
    print(f"\n{resp}\n")
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clean_text")
    data = cursor.fetchall()
    
    logged_in_username = resp.get('login')
    if logged_in_username in github_admin_usernames:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clean_text")
         
        data = cursor.fetchall()
        return render_template("detail.html",data=data)
    else:
        return redirect(url_for('submit'))

# Logout route for GitHub
@app.route('/logout/github')
def github_logout():
    session.clear()
    return redirect(url_for('submit'))


# To Google login
@app.route('/index')
def index():
    if 'google_token' in session:
        # User is already authenticated, redirect to a protected route
        return redirect(url_for('protected'))
    else:
        # User is not authenticated, render the ggl.html template
        authorization_url, _ = flow.authorization_url(prompt='consent')
        return redirect(authorization_url)
# Callback route for handling OAuth response
@app.route('/google/login/callback')
def callback():
    # Handle the callback from the Google OAuth flow
    flow.fetch_token(code=request.args.get('code'))
    session['google_token'] = flow.credentials.token

    # Redirect to the protected route or another page
    return redirect(url_for('protected'))

# Protected route accessible only to authenticated users
# Define the allowed email addresses
allowed_emails = ['amitdiwakar946@gmail.com','kushal@sitare.org','su-23004@sitare.org']

@app.route('/protected')
def protected():
    if 'google_token' in session:
        # User is authenticated
        # Get the user's email from the Google API
        userinfo = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers={'Authorization': f'Bearer {session["google_token"]}'})
        email = userinfo.json().get('email')

        # Check if the user's email is in the allowed list
        if email in allowed_emails:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clean_text")
            data = cursor.fetchall()
            return render_template("detail.html", data=data)
        else:
            # User is not authorize
            return redirect(url_for('submit'))
    else:
        # User is not authenticated
        return redirect(url_for('submit'))



if __name__ == '__main__':
    app.run(debug=True)





