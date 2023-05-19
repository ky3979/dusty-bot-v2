"""Keep the bot instance running"""
from flask import current_app

from services import create_app
from services.extensions.bot import DustyBot

def main():
    """Run bot instance in app context"""
    app = create_app()
    with app.app_context():
        if 'dusty-bot' not in current_app.extensions:
            raise RuntimeError('Bot instance has not been initialized')
        bot: DustyBot = current_app.extensions['dusty-bot']
        bot.run()


if __name__ == "__main__":
    main()
