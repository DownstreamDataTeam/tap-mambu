from tap_mambu.streams.stream import Stream


class CardsStream(Stream):
    def sync(self):
        super(CardsStream, self).sync()
        print("Processing for Cards Stream Done!")
