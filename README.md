# ⛓️ EduChain - Educational Blockchain Platform

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A fully functional educational blockchain web application built from scratch to help students and developers learn blockchain technology through hands-on experience.

## 🎯 Overview

EduChain is an interactive blockchain platform that implements core blockchain concepts including distributed ledger, consensus mechanisms, mining, and cryptocurrency transactions. Built with Python and Flask, it provides a user-friendly interface to explore how blockchains work under the hood.

## ✨ Features

### Core Blockchain Features
- **Complete Blockchain Implementation** - Built from scratch without external blockchain libraries
- **Proof of Work (PoW)** - Adjustable mining difficulty (1-6)
- **Proof of Stake (PoS)** - Alternative consensus mechanism
- **Multiple Hash Algorithms** - MD5, SHA-1, SHA-256, SHA-512
- **Chain Validation** - Real-time blockchain integrity verification
- **Genesis Block** - Automated initialization with 10M EDU token supply
- **Persistent Storage** - Blockchain data saved to JSON files

### User Features
- **Wallet System** - Secure user accounts with encrypted passwords
- **Transaction Processing** - Send and receive EDU tokens
- **Mining Rewards** - Earn tokens by mining blocks
- **Block Explorer** - View complete blockchain history
- **Transaction History** - Track all wallet transactions
- **Dashboard** - Real-time balance and activity monitoring
- **Profile Customization** - Avatar selection and settings

### UI/UX Features
- **Modern Glass-morphism Design** - Beautiful floating pill interface
- **Dark/Light Mode** - Toggle between themes with persistence
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Real-time Updates** - Live balance synchronization
- **Flash Messages** - User-friendly notifications
- **Smooth Animations** - Enhanced user experience

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd educhain
```

2. **Create a virtual environment**
```bash
python -m venv venv
```

3. **Activate the virtual environment**
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install flask
```

5. **Run the application**
```bash
python app.py
```

6. **Open your browser**
```
http://127.0.0.1:5000
```

## 🧪 Test Account

For quick testing, use the pre-configured test account:

- **Username:** `bad`
- **Password:** `admin123`
- **Initial Balance:** 10,000 EDU tokens

## 📁 Project Structure

```
educhain/
├── app.py                    # Main Flask application
├── blockchain.py             # Blockchain implementation
├── wallet.py                 # Wallet management system
├── blockchain_data.json      # Persistent blockchain storage
├── wallets.json              # User wallet storage
├── templates/                # HTML templates
│   ├── base.html            # Base template with navigation
│   ├── home.html            # Landing page
│   ├── dashboard.html       # User dashboard
│   ├── send.html            # Send transactions
│   ├── mine.html            # Mining interface
│   ├── explorer.html        # Blockchain explorer
│   ├── transactions.html    # Transaction list
│   ├── block_detail.html    # Block details
│   ├── transaction_detail.html
│   ├── settings.html        # Blockchain settings
│   ├── profile.html         # User profile
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   └── about.html           # About/documentation
└── static/                   # Static assets
    ├── css/
    │   └── style.css        # Main stylesheet
    └── js/
        └── educhain.js      # Frontend JavaScript
```

## 🎓 How It Works

### Blockchain Basics

1. **Blocks** - Each block contains:
   - Index (position in chain)
   - Timestamp
   - List of transactions
   - Hash (unique identifier)
   - Previous hash (link to previous block)
   - Nonce (proof of work)

2. **Transactions** - Transfer of EDU tokens between addresses
   - Stored in pending pool until mined
   - Confirmed when included in a mined block

3. **Mining** - Process of adding new blocks
   - PoW: Find nonce that produces hash with required leading zeros
   - PoS: Simplified validator selection
   - Miner receives block reward (default: 50 EDU)

4. **Consensus** - Ensures all nodes agree on blockchain state
   - Proof of Work (computational)
   - Proof of Stake (stake-based)

## 💡 Usage Guide

### Creating an Account

1. Click "Register" in the navigation
2. Choose a unique username (min 3 characters)
3. Create a password (min 6 characters)
4. Your wallet address is automatically generated

### Sending Transactions

1. Navigate to "Send" in the sidebar
2. Enter recipient's wallet address
3. Enter amount to send
4. Click "Send Transaction"
5. Transaction enters pending pool

### Mining Blocks

1. Navigate to "Mine" in the sidebar
2. View pending transactions
3. Click "Start Mining"
4. Wait for mining to complete
5. Receive mining reward + transaction confirmations

### Exploring the Blockchain

1. Click "Explorer" to view all blocks
2. Click on any block for detailed information
3. View "Transactions" for complete transaction history
4. Click individual transactions for full details

## ⚙️ Configuration

### Blockchain Settings

Adjust blockchain parameters in the "Blockchain" settings page:

- **Consensus Mechanism:** PoW or PoS
- **Mining Difficulty:** 1-6 (higher = more secure, slower)
- **Hash Algorithm:** MD5, SHA-1, SHA-256, SHA-512
- **Mining Reward:** Amount earned per block

### Profile Settings

- **Avatar:** Choose from 12 emoji avatars
- **Password:** Change account password
- **Account Info:** View wallet address and balance

## 🔧 Technical Details

### Technology Stack

- **Backend:** Python 3.8+ with Flask framework
- **Storage:** JSON file-based persistence
- **Frontend:** HTML5, CSS3 (CSS Variables), Vanilla JavaScript
- **Security:** SHA-256 password hashing with salt

### Key Classes

**Block** - Individual blockchain block
```python
Block(index, timestamp, transactions, previous_hash, nonce)
```

**Blockchain** - Main blockchain manager
```python
Blockchain(difficulty, mining_reward, consensus, hash_algorithm)
```

**Wallet** - User wallet with authentication
```python
Wallet(username, password, balance)
```

### API Endpoints

- `GET /api/blockchain` - Complete blockchain data
- `GET /api/balance/<address>` - Check address balance
- `GET /api/chain-info` - Blockchain statistics

## 🎨 UI Themes

### Light Mode
- Clean, professional design
- High contrast for readability
- Soft shadows and glass effects

### Dark Mode
- Reduced eye strain
- Neon accents and glowing effects
- Gradient overlays

Toggle between themes using the sun/moon icon in the sidebar.

## 🔒 Security Features

- **Password Hashing:** SHA-256 with unique salt per user
- **Session Management:** Secure Flask sessions
- **Input Validation:** Server-side form validation
- **Address Verification:** Ensures recipient exists before sending

## ⚠️ Educational Limitations

This is a **simplified blockchain for learning purposes**. Production blockchains include:

- Peer-to-peer network communication
- Merkle trees for efficient verification
- Digital signatures (ECDSA)
- Transaction fees and gas systems
- Smart contract execution
- Advanced consensus protocols (PBFT, PoA, etc.)
- Network security and attack prevention

## 🐛 Known Limitations

- **Single Server:** No distributed nodes
- **No Signatures:** Transactions aren't cryptographically signed
- **Simple PoS:** Proof of Stake is simplified for education
- **No Network:** No P2P communication between nodes
- **Memory Storage:** Limited scalability with JSON files

## 🤝 Contributing

This is an educational project. Feel free to:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📚 Learning Resources

To better understand blockchain technology:

- **Bitcoin Whitepaper** - Original blockchain concept
- **Ethereum Documentation** - Smart contracts and dApps
- **Blockchain Basics** - Cryptographic principles
- **Consensus Algorithms** - PoW, PoS, PBFT, etc.

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## ⚠️ Disclaimer

**This application is for educational purposes only.**

- EDU tokens have **no real-world value**
- Do not use for actual financial transactions
- Not suitable for production use
- No warranty or guarantees provided

## 👨‍💻 Author

Created for educational purposes to teach blockchain concepts through hands-on learning.

## 🙏 Acknowledgments

- Flask framework for web development
- Python community for excellent libraries
- Blockchain pioneers for the technology

---

**Happy Learning! ⛓️**

For questions or issues, please open an issue on GitHub.
