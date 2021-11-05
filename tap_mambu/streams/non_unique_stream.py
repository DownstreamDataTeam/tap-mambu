from .stream import Stream


class NonUniqueStream(Stream):
    def sync(self):
        super(NonUniqueStream, self).sync()
        print("Processing for any NonUnique Stream Done!")
