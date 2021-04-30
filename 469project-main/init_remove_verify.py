#!/usr/bin/env python3
import Blockchain
from uuid import UUID, uuid4
import os
import hashlib
from datetime import datetime, timedelta, timezone


def initblock(filepath):
    os.environ['BCHOC_FILE_PATH'] = filepath
    if os.path.exists(filepath):
        with open(filepath, 'rb') as file:
            length_of_file = os.path.getsize(filename=filepath)
            if length_of_file > 0:
                file_bytes = file.read(68)
                try:
                    current_block = Blockchain.unpackBlock(file_bytes)
                except:
                    print("error in blockchain file")
                    exit(1)
                if current_block.state.find(b"INITIAL") == 0:
                    print("Blockchain file found with INITIAL block.")
                else:
                    print("error")
                    exit(1)
            else:
                print("error")
                exit(1)
    else:
        print("Blockchain file not found. Created INITIAL block.")
        Blockchain.startChain()


def verify(filepath):
    hash_dict_list = []
    with open(filepath, 'rb') as file:
        counter = 0
        data_length = 0
        while True:
            file_bytes = file.read(68)
            if len(file_bytes) != 68:
                break
            current_block = Blockchain.unpackBlock(file_bytes)
            curr_data_size = current_block.d_length
            if curr_data_size >= 1:
                file.seek(counter * 68 + data_length)
                alldata = file.read(68 + curr_data_size)
                currentBlockHash = hashlib.sha1()
                currentBlockHash.update(alldata)
                hash_dict = {"item id": current_block.evidence_id, "current hash": currentBlockHash.digest(),
                             "prev hash": current_block.prev_hash, "status": current_block.state}
                hash_dict_list.append(hash_dict)
            else:
                currentBlockHash = hashlib.sha1()
                currentBlockHash.update(file_bytes)
                hash_dict = {"item id": current_block.evidence_id, "current hash": currentBlockHash.digest(),
                             "prev hash": current_block.prev_hash,
                             "status": current_block.state}
                hash_dict_list.append(hash_dict)
            counter = counter + 1
            data_length = data_length + curr_data_size
    counter2 = 0
    sorted(hash_dict_list, key=lambda i: i['item id'])
    current_item = 0
    current_state = ""
    print(f"Transactions in blockchain: {len(hash_dict_list)-1}")
    for hashval in hash_dict_list:
        if counter2 == 0:
            if hashval["item id"] != 0 or hashval["status"].find(b"INITIAL") != 0:
                print("error")
                exit(1)
        else:
            if current_item != hashval['item id']:
                current_item = hashval['item id']
                if hashval['status'].find(b'CHECKEDIN') == 0 or hashval['status'].find(b'CHECKEDOUT') == 0:
                    current_state = hashval['status']
                else:
                    print("error")
                    exit(1)
            else:
                if hashval['status'].find(b'CHECKEDIN')==0:
                    if current_state.find(b'CHECKEDOUT')==0:
                        current_state = hashval['status']
                    else:
                        print("error")
                        exit(1)
                elif hashval['status'].find(b'CHECKEDOUT')==0:
                    if current_state.find(b'CHECKEDIN')==0:
                        current_state = hashval['status']
                    else:
                        print("error")
                        exit(1)
                elif hashval['status'].find(b'RELEASED') == 0 or hashval['status'].find(b'DESTROYED')==0 or hashval['status'].find(b'DISPOSED')==0:
                    if current_state.find(b'CHECKEDIN') == 0:
                        current_state = hashval['status']
                    else:
                        print("error")
                        exit(1)
                else:
                    print("error")
                    exit(1)

        counter2 = counter2 + 1


def remove(item_id, reason, owner, filepath):
    if item_id is None:
        item_id = 0
    else:
        item_id = int(item_id[0])

    if owner is None:
        if (reason == "RELEASED"):
            print("error, need owner if released")
            exit(1)
        owner = b''
    else:
        owner = str.encode(owner) + b'\0'
    # print("owner is", owner)
    block_to_remove = None
    with open(filepath, 'rb') as file:
        while True:
            file_bytes = file.read(68)
            if len(file_bytes) != 68:
                break
            current_block = Blockchain.unpackBlock(file_bytes)
            curr_data_size = current_block.d_length
            file.seek(curr_data_size, 1)
            if current_block.evidence_id == item_id:
                block_to_remove = current_block
    if block_to_remove is None:
        print("error could not find block")
        exit(1)
    if block_to_remove.state.find(b"CHECKEDIN") == 0 and (
            reason == "RELEASED" or reason == "DESTROYED" or reason == "DISPOSED"):
        print(f"Case:  {block_to_remove.case_id}")
        print(f"Removed item: {block_to_remove.evidence_id}")
        print("  Status: " + block_to_remove.state.decode().strip('\0'))
        print("  Owner:" + owner.decode().strip('\0'))
        time = str(datetime.utcnow()) + 'Z'
        time = time[:10] + 'T' + time[11:]
        print("  Time of action: " + time)
        Blockchain.addToChain(block_to_remove.case_id, block_to_remove.evidence_id,
                              Blockchain.STATE[reason], len(owner), owner, filepath)
    else:
        print("some other weird error")
        exit(1)

verify("test_block")