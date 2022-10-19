from flask import Flask


def create_app(config_type):

    app = Flask(__name__)

    app.config.from_object(config_type)

    register_blueprints(app)
    initialize_extensions(app)

    # Do not cache due to cached thumbnail loading issues
    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-cache, no-store'
        return response

    return app


def register_blueprints(app):
    from dashboard.general_literature.routes import general_literature
    from dashboard.license_status.routes import license_status
    from dashboard.home.routes import home

    app.register_blueprint(general_literature)
    app.register_blueprint(license_status)
    app.register_blueprint(home)


def initialize_extensions(app):
    pass


    
