import os

from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
)

# from .mock_repo import SiteRepository

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

# repo = SiteRepository(app.config['DATABASE_URL'])
# sites = repo.get_content()


@app.route('/')
def hello_world():
    return render_template('main.html')