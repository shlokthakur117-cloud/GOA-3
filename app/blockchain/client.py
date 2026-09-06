import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

class BlockchainClient:
    def __init__(self):
        self.rpc_url = os.getenv("RPC_URL", "http://127.0.0.1:8545")
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        if not self.w3.is_connected():
            raise Exception("Cannot connect to blockchain node. Is Hardhat running?")
            
        # Hardhat defaults to 20 accounts. We'll use the first one if PRIVATE_KEY is not set.
        self.private_key = os.getenv("PRIVATE_KEY")
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
        else:
            # Fallback to Hardhat default account #0
            self.account = self.w3.eth.account.from_key("0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
            
        self.contract_address = os.getenv("CONTRACT_ADDRESS")
        # Minimal ABI for our contract
        self.abi = [
            {
                "inputs": [
                    {"internalType": "bytes32", "name": "_fingerprint", "type": "bytes32"},
                    {"internalType": "string", "name": "_source", "type": "string"},
                    {"internalType": "uint256", "name": "_timestamp", "type": "uint256"}
                ],
                "name": "storeVerification",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "bytes32", "name": "_fingerprint", "type": "bytes32"}
                ],
                "name": "getVerification",
                "outputs": [
                    {"internalType": "bytes32", "name": "fingerprint", "type": "bytes32"},
                    {"internalType": "string", "name": "source", "type": "string"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "address", "name": "submitter", "type": "address"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]

        if self.contract_address:
            self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)

    def store_verification(self, fingerprint_hex: str, source: str, timestamp: int):
        """Writes the verification to the blockchain."""
        if not self.contract_address:
            raise Exception("CONTRACT_ADDRESS not configured. Did you deploy the contract?")
            
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        
        # Build transaction
        tx = self.contract.functions.storeVerification(
            bytes.fromhex(fingerprint_hex.replace("0x", "")),
            source,
            timestamp
        ).build_transaction({
            'chainId': 31337, # Hardhat local chain ID
            'gas': 2000000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': nonce,
        })
        
        # Sign transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.account.key)
        
        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": receipt.status == 1,
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt.blockNumber
        }

    def get_verification(self, fingerprint_hex: str):
        """Reads a verification from the blockchain."""
        if not self.contract_address:
            raise Exception("CONTRACT_ADDRESS not configured.")
            
        try:
            result = self.contract.functions.getVerification(
                bytes.fromhex(fingerprint_hex.replace("0x", ""))
            ).call()
            
            return {
                "success": True,
                "fingerprint": "0x" + result[0].hex(),
                "source": result[1],
                "timestamp": result[2],
                "submitter": result[3]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
