import click
from cinnabar_server import create_app as server_app

@click.command()
@click.option('--port', default=3010, help='Port number')
@click.option('--host', default='127.0.0.1', help='Host address')
def main(port, host):
    """Run the Cinnabar Flask application"""
    app = server_app()
    app.run(port=port, host=host)

if __name__ == '__main__':
    main()
