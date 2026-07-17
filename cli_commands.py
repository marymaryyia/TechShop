import click
from flask import current_app
from extensions import db
from app.models import User


def register_commands(app):
    @app.cli.command('create-admin')
    @click.argument('email')
    @click.option('--password', default='Admin123!')
    @click.option('--first-name', default='Admin')
    @click.option('--last-name', default='User')
    def create_admin(email, password, first_name, last_name):
        user = User.query.filter_by(email=email).first()
        if user:
            user.role = 'super_admin'
            user.status = 'active'
            db.session.commit()
            click.echo(f'Updated {email} to super_admin.')
        else:
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                role='super_admin',
                status='active'
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            click.echo(f'Created super_admin: {email} / {password}')

    @app.cli.command('seed')
    def seed():
        from seed import run
        run()
        click.echo('Database seeded.')