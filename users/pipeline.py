# users/pipeline.py
def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'auth0':
        # Parse name from Auth0 response
        name = response.get('name', '')
        given_name = name.split(' ')[0] if name else ''
        family_name = ' '.join(name.split(' ')[1:]) if len(name.split(' ')) > 1 else ''

        # Only set names if not already set
        if not user.first_name:
            user.first_name = given_name
        if not user.last_name:
            user.last_name = family_name

        user.save()


def safe_user_details(backend, details, response, user=None, *args, **kwargs):
    """
    This is a safe version of `social_core.pipeline.user.user_details`:
    - It only updates user fields if they're not already set.
    """
    if user is None:
        return

    # 'details' comes from social_core – it contains info like first_name, last_name, email
    changed = False

    if not user.first_name and details.get('first_name'):
        user.first_name = details['first_name']
        changed = True

    if not user.last_name and details.get('last_name'):
        user.last_name = details['last_name']
        changed = True

    if not user.email and details.get('email'):
        user.email = details['email']
        changed = True

    if changed:
        user.save()


def custom_create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'user': user}
    email = details.get('email')
    first_name = details.get('first_name')
    last_name = details.get('last_name')

    if first_name==email:
        first_name = email[:6]  # take first 6 characters

    user = strategy.create_user(
        email=email,
        username=details.get('username') or email,
        first_name=first_name or '',
        last_name=last_name or ''
    )
    return {'user': user}

