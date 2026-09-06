import hashlib
import time

class BlockchainLedger:
    @staticmethod
    def compute_block_hash(index: int, timestamp: float, previous_hash: str, cert_uuid: str, payload_hash: str, nonce: int) -> str:
        block_string = f"{index}{timestamp}{previous_hash}{cert_uuid}{payload_hash}{nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    @staticmethod
    def mine_block(index: int, previous_hash: str, cert_uuid: str, payload_hash: str, difficulty: int = 2) -> dict:
        timestamp = time.time()
        nonce = 0
        target_prefix = "0" * difficulty
        while True:
            block_hash = BlockchainLedger.compute_block_hash(index, timestamp, previous_hash, cert_uuid, payload_hash, nonce)
            if block_hash.startswith(target_prefix):
                break
            nonce += 1
        
        tx_hash = "0x" + hashlib.sha256(f"{block_hash}{time.time()}".encode()).hexdigest()
        
        return {
            "index": index,
            "timestamp": timestamp,
            "previous_hash": previous_hash,
            "certificate_uuid": cert_uuid,
            "payload_hash": payload_hash,
            "nonce": nonce,
            "block_hash": block_hash,
            "tx_hash": tx_hash
        }
