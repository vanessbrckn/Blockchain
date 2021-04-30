import Blockchain
from uuid import UUID, uuid4
import os
from datetime import datetime, timedelta, timezone
from addLog import checkUUID
import time

def checkIn(evidenceID, filepath):
	search_evidenceID = int(evidenceID[0])
	block_to_checkIn = None
	with open(filepath, 'rb') as file:
		while True:
			file_bytes = file.read(68)
			if len(file_bytes) != 68:
				break
			current_block = Blockchain.unpackBlock(file_bytes)
			curr_data_size = current_block.d_length
			file.seek(curr_data_size,1) 
			if current_block.evidence_id == search_evidenceID:
				block_to_checkIn = current_block			
	if block_to_checkIn is not None:
		if block_to_checkIn.state == Blockchain.STATE["in"]:
			print("Error: Cannot check in a checked in item. Must check it out first.")
			exit(1)
		if block_to_checkIn.state == Blockchain.STATE["des"] or block_to_checkIn.state == Blockchain.STATE["dis"] or block_to_checkIn.state == Blockchain.STATE["rel"]:
			print("Error: Cannot check in a removed item.")
			exit(1)
		timestamp = time.time()
		block_to_checkIn.timestamp = timestamp
		Blockchain.addToChain(block_to_checkIn.case_id, block_to_checkIn.evidence_id, 
			Blockchain.STATE["in"], 0, b"", filepath)
		print("Case: " + str(checkUUID(block_to_checkIn.case_id)))
		print("Checked in item: " + str(block_to_checkIn.evidence_id))
		print("\tStatus: CHECKEDIN")
		currtime = str(datetime.utcfromtimestamp(block_to_checkIn.timestamp))+'Z'
		currtime = currtime[:10] + 'T' + currtime[11:]
		print("\tTime of action:", currtime)
		exit(0)
	print("Error: Item not found")
	exit(1)
	
def checkOut(evidenceID, filepath):
	search_evidenceID = int(evidenceID[0])
	block_to_checkOut = None
	with open(filepath, 'rb') as file:
		while True:	
			file_bytes = file.read(68)
			if len(file_bytes) != 68:
				break
			current_block = Blockchain.unpackBlock(file_bytes)
			curr_data_size = current_block.d_length
			file.seek(curr_data_size,1)
			if current_block.evidence_id == search_evidenceID:
				block_to_checkOut = current_block
	if block_to_checkOut is not None:
		if block_to_checkOut.state == Blockchain.STATE["out"]:
			print("Error: Cannot check out a checked out item. Must check it in first.")
			exit(1)
		#print(block_to_checkOut.state)
		if block_to_checkOut.state == Blockchain.STATE["des"] or block_to_checkOut.state == Blockchain.STATE["dis"] or block_to_checkOut.state == Blockchain.STATE["rel"]:
			print("Error: Cannot check out a removed item.")
			exit(1)
		timestamp = time.time()
		block_to_checkOut.timestamp = timestamp
		Blockchain.addToChain(block_to_checkOut.case_id, block_to_checkOut.evidence_id, 
			Blockchain.STATE["out"], 0, b"", filepath)
		print("Case: " + str(checkUUID(block_to_checkOut.case_id)))
		print("Checked out item: " + str(block_to_checkOut.evidence_id))
		print("\tStatus: CHECKEDOUT")
		currtime = str(datetime.utcfromtimestamp(block_to_checkOut.timestamp))+'Z'
		currtime = currtime[:10] + 'T' + currtime[11:]
		print("\tTime of action:", currtime)
		exit(0)
	print("Error: Item not found")
	exit(1)
