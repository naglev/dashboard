from dashboard import create_app
import config


app = create_app(config.DevConfig)


if __name__ == '__main__':
    app.run()