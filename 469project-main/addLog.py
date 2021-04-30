#!/usr/bin/env python3
import Blockchain
from uuid import UUID, uuid4
from math import log
import os
from init_remove_verify import initblock

import pytz
from datetime import datetime, timedelta, timezone

def checkUUID(id):
    valid_uuid = False
    #try as a base 10 uuid 
    try:
        case_id = UUID(int=int(id))
        valid_uuid = True
    except:
        pass
    #try as hex uuid
    if(not valid_uuid):    
        try:
            case_id = UUID(int=int(id,base=16))
            valid_uuid = True
        except:
            pass
    #try as legitimate uuid 
    if(not valid_uuid):
        try:
            case_id = UUID(id)
            valid_uuid = True
        except:
            pass
    #if not any of the above, print and exit. else return uuid object
    if(not valid_uuid):
        print("case_id is not a valid uuid")
        exit(1)
    else:
        return case_id
        

def commandAdd(case_id, item_id, filepath):
    if not os.path.exists(filepath):
        initblock(filepath)
    if case_id is None:
        print("error, need case_id")
        exit(1)
    if item_id is None:
        print("error, need item_id")
        exit(1)   
        
    case_id = checkUUID(case_id)
    evidence_ids =[]
    i=0 #start i at the first item_id
    while(i < len(item_id)):
        evidence_id = int(item_id[i])
        #make sure evidence_id can be stored as 4 bytes 
        if(int(log(evidence_id, 256))+1 > 4):
            print("evidence_id", evidence_id, "is too long")
            exit(1)
        evidence_ids.append(evidence_id)
        i += 1
        
    print("Case:", case_id)
    for i in range(0, len(evidence_ids)):
        if(Blockchain.evidenceInChain(evidence_ids[i], filepath)):
            print("Error cannot add evidence_id", evidence_ids[i], ". item already exists")
            exit(1)
        newBlock = Blockchain.addToChain(case_id, evidence_ids[i], 
                    Blockchain.STATE["in"], 0, b"", filepath)
        
        print("Added item:", evidence_ids[i])
        print("\tStatus: CHECKEDIN")
        time = str(datetime.utcfromtimestamp(newBlock.timestamp))+'Z'
        time = time[:10] + 'T' + time[11:]
        print("\tTime of action:", time)

def printLog(currBlock):
    print("Case:", currBlock.case_id)
    print("Item:", currBlock.evidence_id)
    print("Action:",currBlock.state.decode().strip('\0'))
    time = str(currBlock.timestamp)+'Z'
    time = time[:10] + 'T' + time[11:]
    print("Time:", time)
    
def commandLog(reverse, num, case_id, item_id, filepath):
    #check which args were given
    if case_id is not None:
        case_id = checkUUID(case_id)
    if item_id is not None:
        item_id = int(item_id[0])
    if num is not None:
        num = int(num)
    else:
        num = 9999
    
    blockchain  = []    #the whole blockchain 
    filter1 = []        #the whole blockchain only matching case if provided
    filter2 = []        #the whole blockchain only matching case and item if provided
    currBlock = Blockchain.block()
    #get the entire chain into memory and sort it out from there
    with open(filepath, 'rb') as fd:
        dataLegth=0
        while True:
            fd.read(dataLegth) #skip over any free form data 
            bytes = fd.read(68)
            if(not bytes):  #if EOF
                break
            
            currBlock = Blockchain.unpackBlock(bytes)
            dataLegth = currBlock.d_length
            blockchain.append(currBlock)
    
    #apply the first filter searching by case_id. if no case_id is specified then
    #filter1 = blockchain
    for i in range(0, len(blockchain)):
        if case_id is not None:
            if(blockchain[i].case_id == case_id):
                filter1.append(blockchain[i])
        else:
            filter1 = blockchain
            break
    #apply second filter searching by item. if no item is provided then
    #filter 2 = filter1
    for i in range(0, len(filter1)):
        if item_id is not None:
            if(filter1[i].evidence_id == item_id):
                filter2.append(filter1[i])
        else:
            filter2 = filter1
            break
    #print with filters applied, figure out num and order 
    if not reverse:
        for i in range(0, len(filter2)):
            if(i == num-1 or i == len(filter2)-1):
                printLog(filter2[i])
                break
            else:
                printLog(filter2[i])
                print()
    else:
        stopIndex = len(filter2) - num
        for i in range(len(filter2)-1, -1, -1):
            if(i == stopIndex or i == 0):
                printLog(filter2[i])   #print the last one but no newline
                break
            else:
                printLog(filter2[i])
                print()  