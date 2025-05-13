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
from .checks_repo import CheckRepository

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

url_repo = SiteRepository(app.config['DATABASE_URL'])
check_repo = CheckRepository(app.config['DATABASE_URL'])


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
    urls = url_repo.get_content()
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
    
    id = url_repo.save(user_data)
    flash('Страница успешно добавлена', 'alert-success')
    return redirect(url_for('urls_show', id=id), code=302)


@app.route('/urls')
def urls_get():
    urls=url_repo.get_content()
    urls_with_last_check = []
    for url in urls:
        url_with_last_check = url
        url_with_last_check["last_check"] = check_repo.get_last_check_date_by_id(url["id"])
        urls_with_last_check.append(url_with_last_check)
    return render_template(
        'urls.html',
        urls=urls_with_last_check
    )


@app.route('/urls/<id>')
def urls_show(id):
    url = url_repo.find(id)
    messages = get_flashed_messages(with_categories=True)
    checks = check_repo.get_content_by_url_id(id)
    return render_template(
        'url.html',
        url=url,
        messages=messages,
        checks = checks
    )

@app.route('/urls/<id>/checks', methods=['POST'])
def create_check(id):
    check_repo.save(id)
    flash('Страница успешно проверена', 'alert-success')
    return redirect(url_for('urls_show', id=id))
# render_template(
#         'url.html',
#         url=url,
#         messages=messages,
#         checks = checks
#     )
