# -*-coding: utf-8 -*-
# adminPages.py

from flask import Blueprint

admin = Blueprint('admin', __name__)

@admin.route('/login/')
def admin_login():
    pass

@admin.route('/page/')
def admin_pages():
    pass

@admin.route('/page/new/')
def new_page():
    pass

@admin.route('/page/edit/')
def edit_page():
    pass

