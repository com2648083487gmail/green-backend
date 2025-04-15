from app import create_app, db
import click
from flask.cli import with_appcontext

app = create_app()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """初始化数据库."""
    db.create_all()
    click.echo('数据库初始化完成.')

app.cli.add_command(init_db_command)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000) 