import hashlib
import time
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class Block:
    """Individual block in the blockchain"""
    
    def __init__(self, index: int, timestamp: float, transactions: List[Dict], 
                 previous_hash: str, nonce: int = 0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self, algorithm: str = 'sha256') -> str:
        """Calculate block hash using specified algorithm"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'nonce': self.nonce,
            'previous_hash': self.previous_hash
        }, sort_keys=True)
        
        if algorithm == 'sha1':
            return hashlib.sha1(block_string.encode()).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(block_string.encode()).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(block_string.encode()).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(block_string.encode()).hexdigest()
        else:
            return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'nonce': self.nonce,
            'previous_hash': self.previous_hash,
            'hash': self.hash
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Block':
        """Reconstruct a Block from a dictionary"""
        block = Block(
            index=data['index'],
            timestamp=data['timestamp'],
            transactions=data['transactions'],
            previous_hash=data['previous_hash'],
            nonce=data['nonce']
        )
        block.hash = data['hash']
        return block


class Blockchain:
    """Main blockchain class with persistence"""
    
    def __init__(self, difficulty: int = 4, mining_reward: float = 50.0, 
                 consensus: str = 'pow', hash_algorithm: str = 'sha256',
                 storage_file: str = 'blockchain_data.json'):
        self.difficulty = difficulty
        self.mining_reward = mining_reward
        self.consensus = consensus
        self.hash_algorithm = hash_algorithm
        self.total_supply = 10_000_000
        self.storage_file = storage_file
        
        # Try to load existing blockchain, otherwise create new one
        if not self.load_from_file():
            self.chain: List[Block] = []
            self.pending_transactions: List[Dict] = []
            self.create_genesis_block()
            self.save_to_file()
        
        print(f"📦 Blockchain loaded: {len(self.chain)} blocks, {len(self.pending_transactions)} pending transactions")
    
    def create_genesis_block(self):
        """Create genesis block"""
        genesis_transactions = [{
            'sender': 'SYSTEM',
            'receiver': 'GENESIS_POOL',
            'amount': self.total_supply,
            'timestamp': time.time(),
            'transaction_hash': self._generate_transaction_hash('SYSTEM', 'GENESIS_POOL', self.total_supply, time.time())
        }]
        
        genesis_block = Block(0, time.time(), genesis_transactions, "0", 0)
        genesis_block.hash = genesis_block.calculate_hash(self.hash_algorithm)
        self.chain.append(genesis_block)
    
    def save_to_file(self):
        """Save blockchain to file for persistence"""
        try:
            data = {
                'chain': [block.to_dict() for block in self.chain],
                'pending_transactions': self.pending_transactions,
                'settings': {
                    'difficulty': self.difficulty,
                    'mining_reward': self.mining_reward,
                    'consensus': self.consensus,
                    'hash_algorithm': self.hash_algorithm,
                    'total_supply': self.total_supply
                }
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving blockchain: {e}")
            return False
    
    def load_from_file(self) -> bool:
        """Load blockchain from file"""
        if not os.path.exists(self.storage_file):
            print("📝 No existing blockchain found, creating new one...")
            return False
        
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
            
            # Load settings
            settings = data.get('settings', {})
            self.difficulty = settings.get('difficulty', self.difficulty)
            self.mining_reward = settings.get('mining_reward', self.mining_reward)
            self.consensus = settings.get('consensus', self.consensus)
            self.hash_algorithm = settings.get('hash_algorithm', self.hash_algorithm)
            self.total_supply = settings.get('total_supply', self.total_supply)
            
            # Reconstruct blockchain
            self.chain = [Block.from_dict(block_data) for block_data in data['chain']]
            self.pending_transactions = data.get('pending_transactions', [])
            
            print(f"✅ Blockchain loaded from {self.storage_file}")
            return True
        except Exception as e:
            print(f"❌ Error loading blockchain: {e}")
            return False
    
    def get_latest_block(self) -> Block:
        return self.chain[-1]
    
    def _generate_transaction_hash(self, sender: str, receiver: str, amount: float, timestamp: float) -> str:
        tx_string = f"{sender}{receiver}{amount}{timestamp}"
        return hashlib.sha256(tx_string.encode()).hexdigest()
    
    def add_transaction(self, sender: str, receiver: str, amount: float) -> Dict:
        timestamp = time.time()
        transaction = {
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
            'timestamp': timestamp,
            'transaction_hash': self._generate_transaction_hash(sender, receiver, amount, timestamp)
        }
        self.pending_transactions.append(transaction)
        
        # Save after adding transaction
        self.save_to_file()
        return transaction
    
    def mine_pending_transactions(self, miner_address: str, wallets: Dict = None) -> Optional[Block]:
        if not self.pending_transactions:
            return None
        
        reward_tx = {
            'sender': 'SYSTEM',
            'receiver': miner_address,
            'amount': self.mining_reward,
            'timestamp': time.time(),
            'transaction_hash': self._generate_transaction_hash('SYSTEM', miner_address, self.mining_reward, time.time())
        }
        
        transactions = self.pending_transactions.copy()
        transactions.append(reward_tx)
        
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=transactions,
            previous_hash=self.get_latest_block().hash,
            nonce=0
        )
        
        if self.consensus == 'pow':
            new_block = self._proof_of_work(new_block)
        elif self.consensus == 'pos':
            new_block = self._proof_of_stake(new_block, miner_address, wallets)
        
        self.chain.append(new_block)
        self.pending_transactions = []
        
        # Save after mining
        self.save_to_file()
        return new_block
    
    def _proof_of_work(self, block: Block) -> Block:
        target = '0' * self.difficulty
        while block.hash[:self.difficulty] != target:
            block.nonce += 1
            block.hash = block.calculate_hash(self.hash_algorithm)
        return block
    
    def _proof_of_stake(self, block: Block, validator: str, wallets: Dict = None) -> Block:
        for _ in range(100):
            block.nonce += 1
            block.hash = block.calculate_hash(self.hash_algorithm)
        return block
    
    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if current_block.hash != current_block.calculate_hash(self.hash_algorithm):
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
            if self.consensus == 'pow' and not current_block.hash.startswith('0' * self.difficulty):
                return False
        return True
    
    def get_block_by_index(self, index: int) -> Optional[Dict]:
        if 0 <= index < len(self.chain):
            return self.chain[index].to_dict()
        return None
    
    def get_all_transactions(self) -> List[Dict]:
        all_transactions = []
        for block in self.chain:
            for tx in block.transactions:
                tx_copy = tx.copy()
                tx_copy['block_index'] = block.index
                tx_copy['block_hash'] = block.hash
                all_transactions.append(tx_copy)
        return all_transactions
    
    def get_transactions_for_address(self, address: str) -> List[Dict]:
        transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if tx['sender'] == address or tx['receiver'] == address:
                    tx_copy = tx.copy()
                    tx_copy['block_index'] = block.index
                    tx_copy['block_hash'] = block.hash
                    transactions.append(tx_copy)
        return transactions
    
    def get_balance(self, address: str) -> float:
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx['receiver'] == address:
                    balance += tx['amount']
                if tx['sender'] == address:
                    balance -= tx['amount']
        return balance
    
    def get_chain_info(self) -> Dict:
        total_transactions = sum(len(block.transactions) for block in self.chain)
        return {
            'length': len(self.chain),
            'total_transactions': total_transactions,
            'pending_transactions': len(self.pending_transactions),
            'difficulty': self.difficulty,
            'consensus': self.consensus,
            'hash_algorithm': self.hash_algorithm,
            'mining_reward': self.mining_reward,
            'is_valid': self.is_chain_valid()
        }
    
    def to_dict(self) -> Dict:
        return {
            'chain': [block.to_dict() for block in self.chain],
            'pending_transactions': self.pending_transactions,
            'info': self.get_chain_info()
        }
    
    def update_settings(self, difficulty=None, mining_reward=None, consensus=None, hash_algorithm=None):
        """Update blockchain settings and save"""
        if difficulty is not None:
            self.difficulty = difficulty
        if mining_reward is not None:
            self.mining_reward = mining_reward
        if consensus is not None:
            self.consensus = consensus
        if hash_algorithm is not None:
            self.hash_algorithm = hash_algorithm
        
        # Save updated settings
        self.save_to_file()