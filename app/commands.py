import click
from flask.cli import with_appcontext
from app.models.core import User
from app import db

@click.command('make-superadmin')
@click.argument('email')
@with_appcontext
def make_superadmin(email):
    """Promote a user to superadmin."""
    user = User.query.filter_by(email=email).first()
    if not user:
        click.echo(f'Error: User with email {email} not found.')
        return
    
    user.is_superadmin = True
    db.session.commit()
    click.echo(f'User {email} has been promoted to superadmin.')
