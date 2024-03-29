from flask import Response, flash, redirect, render_template

from yacut import app, db
from yacut.forms import MyForm
from yacut.models import URLMap
from yacut.settings import BASE_URL, PORT
from yacut.utils import get_unique_id


@app.route('/', methods=('GET', 'POST'))
def index_view() -> str:
    form = MyForm()
    if form.validate_on_submit():
        if not form.custom_id.data:
            form.custom_id.data = get_unique_id(URLMap, URLMap.short)
        URLMap().create(db, form.data, validation=False)
        flash('Ваша новая ссылка готова:')
        if int(PORT):
            flash(f"{BASE_URL}:{PORT}/{form.custom_id.data}", 'url')
        else:
            flash(f"{BASE_URL}/{form.custom_id.data}", 'url')
    return render_template('index.html', form=form)


@app.route('/<string:short_id>')
def redirection(short_id: str) -> Response:
    return redirect(URLMap.get_original_link(short_id, api=False))