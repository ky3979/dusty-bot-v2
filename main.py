"""Keep the bot instance running"""
from src import create_bot

def main():
    """Run bot instance"""
    bot = create_bot()
    bot.run()


if __name__ == "__main__":
    main()
