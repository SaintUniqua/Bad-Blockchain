import hashlib
import secrets
import json
import os
from typing import Dict, Optional, List


class Wallet:
    """Individual wallet for storing EDU tokens"""
    
    def __init__(self, username: str, password: str, balance: float = 0.0):
        self.username = username
        self.address = self._generate_address(username)
        self.password_hash = self._hash_password(password)
        self.balance = balance
        self.created_at = None
        self.avatar = '👤'  # Default avatar
    
    def _generate_address(self, username: str) -> str:
        hash_input = f"{username}{secrets.token_hex(16)}"
        address_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        return f"EDU_{address_hash.upper()}"
    
    def _hash_password(self, password: str) -> str:
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{pwd_hash}"
    
    def verify_password(self, password: str) -> bool:
        try:
            salt, stored_hash = self.password_hash.split(':')
            pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return pwd_hash == stored_hash
        except:
            return False
    
    def to_dict(self) -> Dict:
        return {
            'username': self.username,
            'address': self.address,
            'password_hash': self.password_hash,
            'balance': self.balance,
            'created_at': self.created_at,
            'avatar': self.avatar
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Wallet':
        wallet = Wallet.__new__(Wallet)
        wallet.username = data['username']
        wallet.address = data['address']
        wallet.password_hash = data['password_hash']
        wallet.balance = data.get('balance', 0.0)
        wallet.created_at = data.get('created_at')
        wallet.avatar = data.get('avatar', '👤')  # Default to user icon if not set
        return wallet


class WalletManager:
    """Manages all wallets"""
    
    def __init__(self, storage_file: str = 'wallets.json'):
        self.storage_file = storage_file
        self.wallets: Dict[str, Wallet] = {}
        self.load_wallets()
    
    def load_wallets(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    for username, wallet_data in data.items():
                        self.wallets[username] = Wallet.from_dict(wallet_data)
            except Exception as e:
                print(f"Error loading wallets: {e}")
                self.wallets = {}
    
    def save_wallets(self):
        try:
            data = {username: wallet.to_dict() for username, wallet in self.wallets.items()}
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving wallets: {e}")
    
    def register_wallet(self, username: str, password: str, initial_balance: float = 0.0) -> Optional[Wallet]:
        if username in self.wallets:
            return None
        wallet = Wallet(username, password, initial_balance)
        wallet.created_at = None
        self.wallets[username] = wallet
        self.save_wallets()
        return wallet
    
    def authenticate(self, username: str, password: str) -> Optional[Wallet]:
        wallet = self.wallets.get(username)
        if wallet and wallet.verify_password(password):
            return wallet
        return None
    
    def get_wallet_by_username(self, username: str) -> Optional[Wallet]:
        return self.wallets.get(username)
    
    def get_wallet_by_address(self, address: str) -> Optional[Wallet]:
        for wallet in self.wallets.values():
            if wallet.address == address:
                return wallet
        return None
    
    def update_balance(self, address: str, new_balance: float):
        wallet = self.get_wallet_by_address(address)
        if wallet:
            wallet.balance = new_balance
            self.save_wallets()
    
    def get_all_wallets(self) -> List[Dict]:
        return [wallet.to_dict() for wallet in self.wallets.values()]
    
    def wallet_exists(self, username: str) -> bool:
        return username in self.wallets
    
    def get_wallet_count(self) -> int:
        return len(self.wallets)
    
    def create_test_account(self, blockchain=None):
        if not self.wallet_exists('bad'):
            test_wallet = self.register_wallet('bad', 'admin123', 0.0)
            if test_wallet and blockchain:
                # Add transaction from GENESIS_POOL to test account
                blockchain.add_transaction('GENESIS_POOL', test_wallet.address, 10000.0)
                # Mine it immediately to confirm the transaction
                blockchain.mine_pending_transactions('SYSTEM', self.wallets)
                print("✓ Test account created with 10,000 EDU from genesis pool")
                return test_wallet
        else:
            # Wallet exists, but check if they have blockchain balance
            test_wallet = self.get_wallet_by_username('bad')
            if test_wallet and blockchain:
                blockchain_balance = blockchain.get_balance(test_wallet.address)
                if blockchain_balance == 0.0:
                    # Wallet exists but no blockchain balance, give them initial funds
                    blockchain.add_transaction('GENESIS_POOL', test_wallet.address, 10000.0)
                    blockchain.mine_pending_transactions('SYSTEM', self.wallets)
                    print("✓ Test account funded with 10,000 EDU from genesis pool")
                else:
                    print(f"✓ Test account already exists with balance: {blockchain_balance} EDU")
            return test_wallet