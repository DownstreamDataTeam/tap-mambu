from abc import ABC


class Stream(ABC):
    def sync(self):
        print("Processing for any Stream Done!")
