from flask import Blueprint, jsonify, request, redirect, url_for
from critiquebrainz.data.model.user import User
from critiquebrainz.decorators import crossdomain
from critiquebrainz.ws.oauth import oauth
from critiquebrainz.ws.parser import Parser

user_bp = Blueprint('ws_user', __name__)


@user_bp.route('/me')
@crossdomain()
@oauth.require_auth()
def user_me_handler(user):
    """Get your profile information.

    :query inc: includes

    :resheader Content-Type: *application/json*
    """
    inc = Parser.list('uri', 'inc', User.allowed_includes, optional=True) or []
    return jsonify(user=user.to_dict(inc, confidential=True))


@user_bp.route('/me/reviews')
@oauth.require_auth()
@crossdomain()
def user_reviews_handler(user):
    """Get your reviews.

    :resheader Content-Type: *application/json*
    """
    return redirect(url_for('review.list', user_id=user.id, **request.args))


@user_bp.route('/me/applications')
@oauth.require_auth()
@crossdomain()
def user_applications_handler(user):
    """Get your applications.

    :resheader Content-Type: *application/json*
    """
    return jsonify(applications=[c.to_dict() for c in user.clients])


@user_bp.route('/me/tokens')
@oauth.require_auth()
@crossdomain()
def user_tokens_handler(user):
    """Get your OAuth tokens.

    :resheader Content-Type: *application/json*
    """
    return jsonify(tokens=[t.to_dict() for t in user.tokens])


@user_bp.route('/me', methods=['POST'])
@oauth.require_auth('user')
@crossdomain()
def user_modify_handler(user):
    """Modify your profile.

    **OAuth scope:** user

    :reqheader Content-Type: *application/json*

    :json string display_name: Display name **(optional)**
    :json string email: Email address **(optional)**
    :json boolean show_gravatar: Show gravatar **(optional)**

    :resheader Content-Type: *application/json*
    """
    def fetch_params():
        display_name = Parser.string('json', 'display_name', optional=True)
        email = Parser.email('json', 'email', optional=True)
        show_gravatar = Parser.bool('json', 'show_gravatar', optional=True)
        return display_name, email, show_gravatar

    display_name, email, show_gravatar = fetch_params()
    user.update(display_name, email, show_gravatar)
    return jsonify(message='Request processed successfully')


@user_bp.route('/me', methods=['DELETE'])
@oauth.require_auth('user')
@crossdomain()
def user_delete_handler(user):
    """Delete your profile.

    **OAuth scope:** user

    :resheader Content-Type: *application/json*
    """
    user.delete()
    return jsonify(message='Request processed successfully')


@user_bp.route('/<uuid:user_id>', methods=['GET'])
@crossdomain()
def user_entity_handler(user_id):
    """Get profile of a user with a specified UUID.

    :resheader Content-Type: *application/json*
    """
    user = User.query.get_or_404(str(user_id))
    inc = Parser.list('uri', 'inc', User.allowed_includes, optional=True) or []
    return jsonify(user=user.to_dict(inc))


@user_bp.route('/', methods=['GET'])
@crossdomain()
def review_list_handler():
    """Get list of users.

    :query limit: results limit, min is 0, max is 50, default is 50 **(optional)**
    :query offset: result offset, default is 0 **(optional)**

    :resheader Content-Type: *application/json*
    """
    def fetch_params():
        limit = Parser.int('uri', 'limit', min=1, max=50, optional=True) or 50
        offset = Parser.int('uri', 'offset', optional=True) or 0
        return limit, offset

    limit, offset = fetch_params()
    users, count = User.list(limit, offset)
    return jsonify(limit=limit, offset=offset, count=count,
                   users=[p.to_dict() for p in users])
