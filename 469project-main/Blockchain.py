# *-* coding: utf-8 *-*
# This file was derived from the provided blockDemo.py 
import struct
from collections import namedtuple
from datetime import datetime, timedelta, timezone
import time
import hashlib
from pathlib import Path
from sys import byteorder
from uuid import UUID, uuid4
import os

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

class block:
    prev_hash=0  # 20 bytes
    timestamp=time.time()  # 08 bytes
    case_id=UUID(int=0)  # 16 bytes
    evidence_id=0  # 04 bytes
    state=STATE["init"]  # 11 bytes
    d_length=0  # 04 bytes
    data=b""

#note this may need to be changed to accept a case_id or evidence_id as an arg
#instead of, or in addition to, bytes 
def unpackBlock(rawBytes):
    block_head_fmt = "20s d 16s I 11s I"
    block_head_struct = struct.Struct(block_head_fmt)
    
    blockContents = block_head_struct.unpack(rawBytes)
    newBlock = block()
    newBlock.prev_hash = blockContents[0]
    #***TODO will probbably give bad timezone or format with other code****
    newBlock.timestamp = datetime.utcfromtimestamp(blockContents[1])
    #***TODO matts code will not work with this line, it expects bytes***
    newBlock.case_id = UUID(int = int.from_bytes(blockContents[2], "little"))
    newBlock.evidence_id = blockContents[3]
    newBlock.state = blockContents[4]
    newBlock.d_length = blockContents[5]
    #print(newBlock.__dict__)
    return newBlock
    

def packBlock(block):
    block_head_fmt = "20s d 16s I 11s I"
    block_head_struct = struct.Struct(block_head_fmt)
    #print("timestamp is", datetime.fromtimestamp(block.timestamp, timezone.utc))
    if(block.state == STATE["init"]):
        hashvalue = bytes(20)
    else:
        hashvalue = block.prev_hash
        
    block_bytes = block_head_struct.pack(
         hashvalue,
         block.timestamp,
         block.case_id.int.to_bytes(16, byteorder="little"), #or "big"
         block.evidence_id,
         block.state,
         block.d_length
    )
    return block_bytes

#returns the index of the start of last block  
def traverseChain(filepath):
    index=0
    with open(filepath, 'rb') as fd:
        while fd.read(0x40): #skip over inital 68 bytes of block so long as not EOF
            dataLegth = int.from_bytes(fd.read(4), byteorder="little")  #read the d_length integer
            #print("data length of block", dataLegth)
            fd.read(dataLegth)  #skip over the data
            index += 0x44 + dataLegth
    index -= (0x44 + dataLegth)
    return (index, dataLegth)

def addToChain(case_id, evidence_id, state, dataLegth, data, filepath):
    lastIndex, prevDataLegth = traverseChain(filepath)
    # print("lastIndex is", hex(lastIndex))
    # print("dataLegth is", dataLegth)
    #check if latest block is init 
    with open(filepath, 'rb') as fd:
        fd.read(lastIndex) #skip over anything before last block 
        parentBlock = unpackBlock(fd.read(68))
    if(parentBlock.state == STATE["init"]):
        lastBlockHash = bytes(20)   #all null if first real block 
    else:
        with open(filepath, 'rb') as fd:
            fd.read(lastIndex)
            lastBlockHash = hashlib.sha1()
            lastBlockHash.update(fd.read(68+prevDataLegth))
            lastBlockHash = lastBlockHash.digest()
        
    newBlock = block()
    newBlock.prev_hash = lastBlockHash
    newBlock.case_id = case_id
    newBlock.evidence_id = evidence_id
    newBlock.state = state
    newBlock.d_length = dataLegth
    with open(filepath, 'ab') as fd:
        fd.write(packBlock(newBlock))
        fd.write(data)
    
    return newBlock #wont always be needed

#tells whether or not an evidence id exists already
def evidenceInChain(evidence_id, filepath):
    index=0
    with open(filepath, 'rb') as fd:
        while fd.read(0x30): #skip over inital 0x30 bytes of block so long as not EOF
            currID = int.from_bytes(fd.read(4), byteorder="little")  #read the d_length integer
            if(currID == evidence_id):
                return True
            fd.read(0xc)        #skip over the state of block 
            dataLegth = int.from_bytes(fd.read(4), byteorder="little")
            fd.read(dataLegth)  #skip over the data
    return False

        
#to be used only by the init command when no blockchain exits
def startChain():
    fd = open(str(os.environ.get('BCHOC_FILE_PATH')), 'ab')   
    start_block = block()
    start_block.d_length = 14
    start_block.data = b"Initial block\0" 
    fd.write(packBlock(start_block)+start_block.data)
    fd.close()