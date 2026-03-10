from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from blockchain import Blockchain
from wallet import WalletManager
from datetime import datetime
import secrets
import time

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Initialize blockchain and wallet manager
# The blockchain will now automatically load from file if it exists
blockchain = Blockchain(difficulty=4, mining_reward=50.0, consensus='pow', hash_algorithm='sha256')
wallet_manager = WalletManager('wallets.json')
wallet_manager.create_test_account(blockchain)


# Helper functions
def sync_wallet_balances():
    """Synchronize wallet balances with blockchain"""
    for wallet in wallet_manager.wallets.values():
        actual_balance = blockchain.get_balance(wallet.address)
        wallet_manager.update_balance(wallet.address, actual_balance)


def get_current_user():
    """Get currently logged in user"""
    if 'username' in session:
        return wallet_manager.get_wallet_by_username(session['username'])
    return None


def login_required(f):
    """Decorator to require login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def format_timestamp(timestamp):
    """Convert timestamp to readable format"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def format_hash(hash_string, length=16):
    """Format hash for display"""
    if len(hash_string) <= length:
        return hash_string
    return f"{hash_string[:length]}..."


app.jinja_env.filters['format_timestamp'] = format_timestamp
app.jinja_env.filters['format_hash'] = format_hash


# Routes
@app.route('/')
def home():
    """Home page"""
    chain_info = blockchain.get_chain_info()
    recent_blocks = [block.to_dict() for block in blockchain.chain[-5:]][::-1]
    return render_template('home.html', chain_info=chain_info, recent_blocks=recent_blocks, user=get_current_user())


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if wallet_manager.wallet_exists(username):
            flash('Username already exists', 'danger')
            return render_template('register.html')
        
        wallet = wallet_manager.register_wallet(username, password, 0.0)
        if wallet:
            wallet.created_at = datetime.now().isoformat()
            wallet_manager.save_wallets()
            flash(f'Account created! Your address: {wallet.address}', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed', 'danger')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        wallet = wallet_manager.authenticate(username, password)
        
        if wallet:
            session['username'] = username
            session['address'] = wallet.address
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user = get_current_user()

    # Sync balances from blockchain
    sync_wallet_balances()
    user = get_current_user()

    transactions = blockchain.get_transactions_for_address(user.address)[-10:][::-1]
    chain_info = blockchain.get_chain_info()

    # ── Recent blocks for the Latest Blocks table ──
    recent_blocks = [block.to_dict() for block in blockchain.chain[-8:]][::-1]

    # ── Network Overview Stats ──
    all_tx = blockchain.get_all_transactions()
    total_transactions = len(all_tx)

    # Unique active addresses (exclude SYSTEM / GENESIS_POOL)
    active_addresses = set()
    token_transfers = 0
    for tx in all_tx:
        if tx['sender'] not in ('SYSTEM', 'GENESIS_POOL'):
            active_addresses.add(tx['sender'])
            token_transfers += 1
        if tx['receiver'] not in ('SYSTEM', 'GENESIS_POOL'):
            active_addresses.add(tx['receiver'])

    # TPS: total_tx / elapsed time (genesis → latest block)
    if len(blockchain.chain) > 1:
        elapsed = blockchain.chain[-1].timestamp - blockchain.chain[0].timestamp
        tps = round(total_transactions / elapsed, 4) if elapsed > 0 else 0
    else:
        tps = 0

    # TVL: sum of all non-SYSTEM balances
    tvl = 0.0
    for wallet in wallet_manager.wallets.values():
        balance = blockchain.get_balance(wallet.address)
        if balance > 0:
            tvl += balance

    # Top holder
    top_holder = 0.0
    for wallet in wallet_manager.wallets.values():
        bal = blockchain.get_balance(wallet.address)
        if bal > top_holder:
            top_holder = bal

    # Circulating supply = total mined rewards
    circulating = sum(
        tx['amount'] for block in blockchain.chain
        for tx in block.transactions
        if tx['sender'] == 'SYSTEM' and tx['receiver'] not in ('GENESIS_POOL',)
    )

    # Supply % used for the bar
    supply_pct = round(min(circulating / blockchain.total_supply * 100, 100), 1)

    # Hash rate label based on difficulty
    difficulty_label = {1: '~0.1 KH/s', 2: '~1 KH/s', 3: '~10 KH/s',
                        4: '~100 KH/s', 5: '~1 MH/s', 6: '~10 MH/s'}
    hash_rate = difficulty_label.get(blockchain.difficulty, f'D{blockchain.difficulty}')

    network_stats = {
        'total_transactions': total_transactions,
        'tps': tps,
        'active_wallets': len(active_addresses),
        'hash_rate': hash_rate,
        'tvl': f'{tvl:,.2f}',
        'circulating': f'{circulating:,.2f}',
        'supply_pct': supply_pct,
        'token_transfers': token_transfers,
        'top_holder': f'{top_holder:,.2f}',
        'market_cap': f'{circulating:,.0f}',   # 1:1 for educational chain
    }

    # ── Chart data ──
    blocks = blockchain.chain
    tx_counts = [len(b.transactions) for b in blocks]

    # Unique addresses per block
    addr_counts = []
    for b in blocks:
        addrs = set()
        for tx in b.transactions:
            if tx['sender'] not in ('SYSTEM', 'GENESIS_POOL'):
                addrs.add(tx['sender'])
            if tx['receiver'] not in ('SYSTEM', 'GENESIS_POOL'):
                addrs.add(tx['receiver'])
        addr_counts.append(len(addrs))

    # Block times (seconds between consecutive blocks)
    block_times = []
    for i in range(1, len(blocks)):
        dt = round(blocks[i].timestamp - blocks[i - 1].timestamp, 1)
        block_times.append(max(0, dt))

    # Cumulative transaction count
    cumulative_tx = []
    running = 0
    for b in blocks:
        running += len(b.transactions)
        cumulative_tx.append(running)

    block_chart_data = {
        'tx_counts': tx_counts,
        'addr_counts': addr_counts,
        'block_times': block_times,
        'cumulative_tx': cumulative_tx,
    }

    return render_template(
        'dashboard.html',
        user=user,
        transactions=transactions,
        chain_info=chain_info,
        recent_blocks=recent_blocks,
        network_stats=network_stats,
        block_chart_data=block_chart_data,
    )


@app.route('/send', methods=['GET', 'POST'])
@login_required
def send_transaction():
    """Send EDU tokens"""
    user = get_current_user()
    
    if request.method == 'POST':
        receiver_address = request.form.get('receiver_address', '').strip()
        amount_str = request.form.get('amount', '0')
        
        try:
            amount = float(amount_str)
        except ValueError:
            flash('Invalid amount', 'danger')
            return render_template('send.html', user=user)
        
        sync_wallet_balances()
        user = get_current_user()
        
        if not receiver_address:
            flash('Receiver address is required', 'danger')
            return render_template('send.html', user=user)
        
        if receiver_address == user.address:
            flash('Cannot send to yourself', 'danger')
            return render_template('send.html', user=user)
        
        if amount <= 0:
            flash('Amount must be positive', 'danger')
            return render_template('send.html', user=user)
        
        if user.balance < amount:
            flash(f'Insufficient balance. Available: {user.balance} EDU', 'danger')
            return render_template('send.html', user=user)
        
        receiver_wallet = wallet_manager.get_wallet_by_address(receiver_address)
        if not receiver_wallet:
            flash('Receiver address not found', 'danger')
            return render_template('send.html', user=user)
        
        # Transaction is automatically saved to blockchain file
        transaction = blockchain.add_transaction(user.address, receiver_address, amount)
        flash(f'Transaction added! Hash: {transaction["transaction_hash"][:16]}...', 'success')
        flash('Transaction will be confirmed after mining', 'info')
        return redirect(url_for('dashboard'))
    
    return render_template('send.html', user=user)


@app.route('/mine', methods=['GET', 'POST'])
@login_required
def mine():
    """Mine blocks"""
    user = get_current_user()
    
    if request.method == 'POST':
        if not blockchain.pending_transactions:
            flash('No pending transactions to mine', 'warning')
            return render_template('mine.html', user=user, pending_count=0)
        
        pending_count = len(blockchain.pending_transactions)
        start_time = time.time()
        # Mining automatically saves the blockchain to file
        new_block = blockchain.mine_pending_transactions(user.address, wallet_manager.wallets)
        end_time = time.time()
        mining_time = round(end_time - start_time, 2)
        
        if new_block:
            sync_wallet_balances()
            flash(f'Block #{new_block.index} mined successfully!', 'success')
            flash(f'Mining time: {mining_time} seconds', 'info')
            flash(f'Transactions confirmed: {pending_count}', 'info')
            flash(f'Mining reward: {blockchain.mining_reward} EDU', 'success')
            return redirect(url_for('block_detail', index=new_block.index))
        else:
            flash('Mining failed', 'danger')
    
    pending_count = len(blockchain.pending_transactions)
    return render_template('mine.html', user=user, pending_count=pending_count, 
                         pending_transactions=blockchain.pending_transactions,
                         consensus=blockchain.consensus, difficulty=blockchain.difficulty)


@app.route('/explorer')
def explorer():
    """Blockchain explorer"""
    blocks = [block.to_dict() for block in blockchain.chain][::-1]
    chain_info = blockchain.get_chain_info()
    return render_template('explorer.html', blocks=blocks, chain_info=chain_info, user=get_current_user())


@app.route('/block/<int:index>')
def block_detail(index):
    """Block details"""
    block_data = blockchain.get_block_by_index(index)
    if not block_data:
        flash('Block not found', 'danger')
        return redirect(url_for('explorer'))
    return render_template('block_detail.html', block=block_data, user=get_current_user())


@app.route('/transactions')
def transactions():
    """All transactions"""
    all_transactions = blockchain.get_all_transactions()[::-1]
    return render_template('transactions.html', transactions=all_transactions, user=get_current_user())


@app.route('/transaction/<transaction_hash>')
def transaction_detail(transaction_hash):
    """Transaction details"""
    all_transactions = blockchain.get_all_transactions()
    transaction = None
    for tx in all_transactions:
        if tx['transaction_hash'] == transaction_hash:
            transaction = tx
            break
    if not transaction:
        flash('Transaction not found', 'danger')
        return redirect(url_for('transactions'))
    return render_template('transaction_detail.html', transaction=transaction, user=get_current_user())


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Blockchain settings"""
    user = get_current_user()
    
    if request.method == 'POST':
        try:
            new_difficulty = int(request.form.get('difficulty', blockchain.difficulty))
            new_reward = float(request.form.get('mining_reward', blockchain.mining_reward))
            new_consensus = request.form.get('consensus', blockchain.consensus)
            new_algorithm = request.form.get('hash_algorithm', blockchain.hash_algorithm)
            
            # Update settings and automatically save to file
            blockchain.update_settings(
                difficulty=max(1, min(6, new_difficulty)),
                mining_reward=max(1, new_reward),
                consensus=new_consensus if new_consensus in ['pow', 'pos'] else 'pow',
                hash_algorithm=new_algorithm if new_algorithm in ['sha1', 'md5', 'sha256', 'sha512'] else 'sha256'
            )
            
            flash('Settings updated and saved successfully!', 'success')
        except Exception as e:
            flash(f'Error updating settings: {str(e)}', 'danger')
        
        return redirect(url_for('settings'))
    
    return render_template('settings.html', user=user, blockchain=blockchain)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile settings"""
    user = get_current_user()
    
    if request.method == 'POST':
        # Handle avatar — image upload takes priority over icon selection
        avatar_image = request.form.get('avatar_image', '').strip()
        avatar_key   = request.form.get('avatar', '').strip()
        if avatar_image and avatar_image.startswith('data:image'):
            user.avatar = avatar_image
            wallet_manager.save_wallets()
            flash('Profile picture updated!', 'success')
        elif avatar_key:
            user.avatar = avatar_key
            wallet_manager.save_wallets()
            flash('Profile picture updated!', 'success')
        
        # Handle password change
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password and new_password:
            if not user.verify_password(current_password):
                flash('Current password is incorrect', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match', 'danger')
            elif len(new_password) < 6:
                flash('New password must be at least 6 characters', 'danger')
            else:
                user.password_hash = user._hash_password(new_password)
                wallet_manager.save_wallets()
                flash('Password changed successfully!', 'success')
        
        return redirect(url_for('profile'))
    
    # Set default avatar if not set
    if not hasattr(user, 'avatar') or not user.avatar:
        user.avatar = 'user'
    
    return render_template('profile.html', user=user)


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html', user=get_current_user())


# API Routes
@app.route('/api/blockchain')
def api_blockchain():
    return jsonify(blockchain.to_dict())


@app.route('/api/balance/<address>')
def api_balance(address):
    balance = blockchain.get_balance(address)
    return jsonify({'address': address, 'balance': balance})


@app.route('/api/chain-info')
def api_chain_info():
    return jsonify(blockchain.get_chain_info())


if __name__ == '__main__':
    print("=" * 60)
    print("ðŸš€ Educational Blockchain Application Starting...")
    print("=" * 60)
    print(f"ðŸ“Š Blockchain: {len(blockchain.chain)} blocks")
    print(f"ðŸ’› Wallets: {wallet_manager.get_wallet_count()}")
    print(f"âš™ï¸  Consensus: {blockchain.consensus.upper()}")
    print(f"ðŸ” Hash: {blockchain.hash_algorithm.upper()}")
    print(f"ðŸ’Ž Reward: {blockchain.mining_reward} EDU")
    print(f"ðŸ’¾ Persistence: ENABLED (blockchain_data.json)")
    print("=" * 60)
    print("ðŸ§ª Test Account: username='bad', password='admin123'")
    print("=" * 60)
    print("ðŸŒ Running at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)