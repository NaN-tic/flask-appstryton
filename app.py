#This file is part appstryton app for Flask.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
import os
import json
import ConfigParser
import pkg_resources
from pkginfo import *
import datetime

from flask import Flask, render_template, request, abort
from flask.ext.babel import Babel, gettext as _
from flask.ext.cache import Cache
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed

from modescription import get_description, read_rst


def get_config():
    '''Get values from cfg file'''
    conf_file = '%s/config.ini' % os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser.ConfigParser()
    config.read(conf_file)

    results = {}
    for section in config.sections():
        results[section] = {}
        for option in config.options(section):
            results[section][option] = config.get(section, option)
    return results

def create_app(config=None):
    '''Create Flask APP'''
    cfg = get_config()
    app_name = cfg['flask']['app_name']
    app = Flask(app_name)
    app.config.from_pyfile(config)

    return app

def get_template(app, tpl):
    '''Get template'''
    return "%s/%s" % (app.config.get('TEMPLATE'), tpl)

def parse_setup(filename):
    globalsdict = {}  # put predefined things here
    localsdict = {}  # will be populated by executed script
    execfile(filename, globalsdict, localsdict)
    return localsdict

def get_lang():
    return app.config.get('LANGUAGE')

conf_file = '%s/config.cfg' % os.path.dirname(os.path.realpath(__file__))
app = create_app(conf_file)
app.config['BABEL_DEFAULT_LOCALE'] = get_lang()
babel = Babel(app)
cache = Cache(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template(get_template(app, '404.html')), 404

def make_external(url):
    return urljoin(request.url_root, url)

def get_module(modules, module):
    '''Return dict of base data module'''
    return (item for item in modules if item["module_name"] == module).next()

def get_info_module(src):
    '''Return dict of info module'''
    try:
        info = UnpackedSDist(src)
    except:
        info = None
    return info

def get_modules():
    '''Return list of info dict module'''
    modules = []
    tocs = []
    name_toc = None
    add_toc = True

    for ep in pkg_resources.iter_entry_points('trytond.modules'):
        module_name = ep.module_name.split('.')[-1]
        name = ' '.join([n.capitalize() for n in module_name.split('_')])
        group = name.split(' ')[0]

        src = '%s/setup.py' % ep.dist.location
        info = get_info_module(src)

        if name_toc != group:
            name_toc = group
            tocs.append(group)
            add_toc = True
        else:
            name_toc = group
            add_toc = False

        mod = {
            'group': group,
            'name': name,
            'module_name': module_name,
            'version': ep.dist.version,
            'location': ep.dist.location,
            'info': info,
        }
        if add_toc:
            mod['toc'] = name_toc
        modules.append(mod)
    return modules, tocs

@app.route('/')
@cache.cached(timeout=120)
def index():
    modules, tocs = get_modules()
    return render_template(get_template(app, 'index.html'), modules=modules, tocs=tocs)

@app.route('/<slug>/')
@cache.cached(timeout=120)
def info(slug):
    modules_by_category = []
    lang = get_lang()
    modules, tocs = get_modules()
    module = get_module(modules, slug)

    if module:
        group = module['group']
        for mod in modules:
            if mod['group'] == group:
                modules_by_category.append({
                    'name': mod['name'],
                    'module_name': mod['module_name'],
                    })
        src = '%s/setup.py' % module['location']
        info = get_info_module(src)
        if info:
            module['info'] = info
        description = get_description(lang, module['location'], module['name'])
        if description:
            module['description'] = description
        return render_template(get_template(app, 'info.html'), module=module, tocs=modules_by_category)
    else:
        abort(404)

@app.route('/modules.atom')
@cache.cached(timeout=120)
def modules_feed():
    feed = AtomFeed('Tryton Modules',
                    feed_url=request.url, url=request.url_root)
    modules, tocs = get_modules()
    for module in modules:
        description = ''
        print module
        if module['info']:
            description = module['info'].summary
        url = ''
        feed.add(module['name'], unicode(description),
                 content_type='html',
                 author=app.config.get('AUTHOR'),
                 url=make_external(module['module_name']),
                 updated=datetime.datetime.now(),
                 published=datetime.datetime.now())
    return feed.get_response()

if __name__ == "__main__":
    app.run()
