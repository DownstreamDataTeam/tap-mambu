from typing import List

from tap_mambu.streams.audit_trail import AuditTrailStream
from tap_mambu.streams.cards import CardsStream
from tap_mambu.streams.stream import Stream

stream_name_to_class_dict = {
    "audit_trail": AuditTrailStream,
    "cards": CardsStream,
}


if __name__ == '__main__':
    catalog_list = ["audit_trail", "cards"]
    streams_to_sync: List[Stream] = [stream_name_to_class_dict[catalog_stream_name]()
                                     for catalog_stream_name in catalog_list]
    for stream in streams_to_sync:
        stream.sync()
