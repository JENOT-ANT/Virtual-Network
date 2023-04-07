from Bot import Bot
from os import getenv, chdir
from os.path import dirname

def load_token() -> str:
    token = getenv('API_TOKEN')
    
    if token == None:
        raise KeyError("API_TOKEN not found.")
    
    return token


def main():
    chdir(f"{dirname(__file__)}/../game-data")
    
    bot = Bot()

    bot.run(load_token())

if __name__ == '__main__':
    main()
  
