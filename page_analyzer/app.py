import os
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)
from validators import url as validate

from .urls_repo import SiteRepository

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

repo = SiteRepository(app.config['DATABASE_URL'])


def normalize_url(url):
    parsed_url = urlparse(url)
    normalized_url = parsed_url._replace(scheme=parsed_url.scheme.lower(),
                                         netloc=parsed_url.netloc.lower(),
                                         path=parsed_url.path.rstrip('/'))
    return urlunparse(normalized_url)


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('main.html', messages=messages, url='')


@app.route('/urls', methods=['POST'])
def urls_post():
    user_data = request.form.to_dict()
    user_data['url'] = normalize_url(user_data['url'])
    urls = repo.get_content()
    urls_names = []
    for url in urls:
        urls_names.append(url['name'])
    is_valid = validate(user_data['url'])
    if is_valid is not True:
        flash('Некорректный URL', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'main.html',
            messages=messages,
            url=user_data['url'],
        )
    if user_data['url'] in urls_names:
        flash('Страница уже существует', 'alert-info')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'main.html',
            messages=messages,
            url=user_data['url'],
        )
    if len(user_data['url']) > 255:
        flash('URL превышает 255 символов', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'main.html',
            messages=messages,
            url=user_data['url'],
        )
    
    id = repo.save(user_data)
    flash('Страница успешно добавлена', 'alert-success')
    return redirect(url_for('urls_show', id=id), code=302)


@app.route('/urls')
def urls_get():
    return render_template(
        'urls.html',
        urls=repo.get_content()
    )


@app.route('/urls/<id>')
def urls_show(id):
    url = repo.find(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'url.html',
        url=url,
        messages=messages,
    )