import sys, os

sys.path.append('/home/mathieu/PycharmProjects/PokeAI' if os.name == 'posix' else 'C:\\Users\\mathi\\PycharmProjects\\PokeAI')

from src.controller.MainController import MainController


if __name__ == '__main__':

    MainController()
