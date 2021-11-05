from tap_mambu.streams.non_unique_stream import NonUniqueStream


class AuditTrailStream(NonUniqueStream):
    def sync(self):
        super(AuditTrailStream, self).sync()
        print("Processing for Audit Trail Stream Done!")
