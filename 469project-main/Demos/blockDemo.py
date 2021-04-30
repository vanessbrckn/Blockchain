# *-* coding: utf-8 *-*

import struct
from collections import namedtuple
from datetime import datetime, timedelta, timezone
from hashlib import sha1
from pathlib import Path
from sys import byteorder
from uuid import UUID, uuid4

# random.seed()

Block = namedtuple("Block", ["prev_hash", "timestamp", "case_id", "evidence_id", "state", "d_length", "data"])

STATE = {
    "init": b"INITIAL\0\0\0\0",
    "in": b"CHECKEDIN\0\0",
    "out": b"CHECKEDOUT\0",
    "dis": b"DISPOSED\0\0\0",
    "des": b"DESTROYED\0\0",
    "rel": b"RELEASED\0\0\0",
    "INITIAL": b"INITIAL\0\0\0\0",
    "CHECKEDIN": b"CHECKEDIN\0\0",
    "CHECKEDOUT": b"CHECKEDOUT\0",
    "DISPOSED": b"DISPOSED\0\0\0",
    "DESTROYED": b"DESTROYED\0\0",
    "RELEASED": b"RELEASED\0\0\0",
}
INITIAL = Block(
    prev_hash=0,  # 20 bytes
    timestamp=0,  # 08 bytes
    case_id=UUID(int=0),  # 16 bytes
    evidence_id=0,  # 04 bytes
    state=STATE["init"],  # 11 bytes
    d_length=14,  # 04 bytes
    data=b"Initial block\0",
)

block_head_fmt = "20s d 16s I 11s I"
block_head_len = struct.calcsize(block_head_fmt)
block_head_struct = struct.Struct(block_head_fmt)

fd = open('./test_block','rb')

#======================================================================
# Unpacking the block structure
#======================================================================
block = fd.read(68)
blockContents = block_head_struct.unpack(block)
timestamp = datetime.fromtimestamp(blockContents[1])

print(timestamp)
print(blockContents)
print(blockContents[4])

fd.close()


#======================================================================
# packing the structure
#======================================================================

# block_bytes = block_head_struct.pack(
#      prev_hash,
#      block.timestamp,
#      block.case_id.int.to_bytes(16, byteorder="little"), #or "big"
#      block.evidence_id,
#      state,
#      len(data)
# )
