# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module implements HTTP request handlers for the user views."""

from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_app
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user

from timesketch.lib.forms import UsernamePasswordForm
from timesketch.models.user import User


# Register flask blueprint
user_views = Blueprint(u'user_views', __name__)


@user_views.route(u'/login/', methods=[u'GET', u'POST'])
def login():
    """Handler for the login page view.

    There are two ways of authentication.
    1) If Single Sign On (SSO) is enabled in configuration and the environment
       variable is present, e.g. REMOTE_USER then the system will get or create
       the user object and setup a session for the user.
    2) Local authentication is used if SSO login is not enabled. This will
       authenticate the user against the local user database.

    Returns:
        Redirect if authentication is successful or template with context
        otherwise.
    """
    form = UsernamePasswordForm()

    # SSO login based on environment variable, e.g. REMOTE_USER.
    if current_app.config.get(u'SSO_ENABLED', False):
        remote_user_env = current_app.config.get(
            u'SSO_USER_ENV_VARIABLE', u'REMOTE_USER')
        remote_user = request.environ.get(remote_user_env, None)
        if remote_user:
            user = User.get_or_create(username=remote_user, name=remote_user)
            login_user(user)

    # Login form POST
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.check_password(plaintext=form.password.data):
                login_user(user)

    if current_user.is_authenticated():
        return redirect(request.args.get(u'next') or u'/')

    return render_template(u'user/login.html', form=form)


@user_views.route(u'/logout/', methods=[u'GET'])
def logout():
    """Handler for the logout page view.

    Returns:
        Redirect response.
    """
    logout_user()
    return redirect(url_for(u'user_views.login'))
