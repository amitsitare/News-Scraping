# Flask Application with Google and GitHub Authentication

## Overview
This Flask application is a web-based platform that integrates:

1. **Google OAuth** for user authentication.
2. **GitHub OAuth** for user authentication.
3. Text extraction, sentiment analysis, and keyword analysis from news article URLs.
4. PostgreSQL for data storage.

## Features
- **News Article Analysis**: Extracts, processes, and analyzes content from URLs.
- **Google Login**: Uses OAuth to authenticate users and grants access based on email whitelisting.
- **GitHub Login**: Uses OAuth to authenticate users and grants admin-level access for specific usernames.
- **Data Visualization**: Displays processed data with sentence counts, word counts, stopword counts, sentiment analysis, and keywords.
- **Secure Access**: Protected routes with password validation and session management.
- **Database Integration**: Stores processed news data in a PostgreSQL database.

## Tech Stack
- **Backend**: Flask
- **Authentication**: Authlib, Google OAuth, GitHub OAuth
- **Web Scraping**: BeautifulSoup, Requests
- **Natural Language Processing**: NLTK
- **Database**: PostgreSQL

## Prerequisites
- Python 3.9+
- PostgreSQL database
- OAuth client credentials for Google and GitHub

## Installation

1. **Clone the Repository**
```bash
$ git clone <repository-url>
$ cd <repository-folder>
```

2. **Create and Activate a Virtual Environment**
```bash
$ python -m venv venv
$ source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
$ pip install -r requirements.txt
```

4. **Set Up OAuth Credentials**
   - **Google OAuth**:
     - Create a project in Google Cloud Console.
     - Enable the OAuth 2.0 API.
     - Download the `client_secrets.json` file and place it in the project directory.
   - **GitHub OAuth**:
     - Create an OAuth app in GitHub Developer Settings.
     - Note the `Client ID` and `Client Secret`.

5. **Database Configuration**
   - Install and configure PostgreSQL.
   - Update the connection string in the code:
     ```python
     conn=psycopg2.connect(
         host='your_host', 
         database='your_database', 
         user='your_user', 
         password='your_password')
     ```

6. **Run the Application**
```bash
$ python app.py
```
Access the application at: `http://127.0.0.1:5000`

## Endpoints

### `/` (Home)
- **Method**: GET, POST
- **Description**: Accepts a news article URL, extracts and processes the content, and stores the result in the database.

### `/view_data`
- **Method**: POST
- **Description**: Password-protected route to view all processed data.

### `/login/github`
- **Method**: GET
- **Description**: Initiates GitHub OAuth login.

### `/login/github/authorize`
- **Method**: GET
- **Description**: Handles GitHub OAuth authorization and grants access based on username.

### `/logout/github`
- **Method**: GET
- **Description**: Logs out the GitHub session.

### `/index`
- **Method**: GET
- **Description**: Redirects users to Google OAuth for authentication.

### `/google/login/callback`
- **Method**: GET
- **Description**: Handles the callback from Google OAuth.

### `/protected`
- **Method**: GET
- **Description**: Displays processed data for authenticated Google users with allowed email addresses.

## Security
- **Session Management**: Uses Flask sessions to maintain user login state.
- **Secret Keys**: Ensure `app.secret_key` and OAuth secrets are secure.
- **Whitelisted Emails and Usernames**: Grants access only to authorized users.

## Dependencies
- Flask
- Authlib
- NLTK
- psycopg2
- BeautifulSoup
- Requests
- Google Auth OAuthlib

## Environment Variables
- Set the following environment variables for secure OAuth:
  ```bash
  export GOOGLE_CLIENT_SECRET_FILE="path/to/client_secrets.json"
  export GITHUB_CLIENT_ID="your_github_client_id"
  export GITHUB_CLIENT_SECRET="your_github_client_secret"
  ```

## Database Schema
The `clean_text` table stores processed news data:

| Column            | Type    | Description                             |
|-------------------|---------|-----------------------------------------|
| id                | SERIAL  | Primary key                            |
| Name              | TEXT    | Name of the user                       |
| url               | TEXT    | URL of the news article                |
| clean_news_text   | TEXT    | Extracted and cleaned text             |
| num_sentence      | INTEGER | Number of sentences                    |
| num_word          | INTEGER | Number of words                        |
| num_stop_word     | INTEGER | Number of stopwords                    |
| News_Sentiment    | TEXT    | Sentiment analysis result              |
| num_post_tag      | TEXT    | Part-of-speech tag counts (as JSON)    |
| Common_Keywords   | TEXT    | Most common keywords                   |

## Future Improvements
- Add user-friendly error handling.
- Optimize scraping for various news article formats.
- Enhance the UI with interactive charts.
- Integrate additional OAuth providers.

## License
This project is licensed under the MIT License.
