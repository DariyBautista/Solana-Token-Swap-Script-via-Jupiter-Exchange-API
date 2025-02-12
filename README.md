# Automated Solana Token Swap Script via Jupiter Exchange API

## Overview
This script performs automated token swaps on the Solana blockchain using the Jupiter API. It selects a random wallet, swaps SOL for a random token, waits for a specified period, and then swaps the token back to SOL. The cycle repeats continuously until the script is stopped.

## Features
- Randomly selects a wallet from the configuration file
- Swaps all available SOL (except 0.01 SOL for fees) to a random token
- Waits between 5 seconds and 2 minutes before swapping the token back to SOL
- Keeps track of balances and ensures enough SOL is available for transactions
- Logs transaction details, including the trading volume
- Supports multiple wallets stored in `config.json`
- Allows adding new tokens to the list (ensure correct contract address and decimals)

## Requirements
### Python Version
Ensure you have **Python 3.8 or later** installed.

## Installation

1. Clone this repository:
   ```sh
   https://github.com/DariyBautista/Solana-Token-Swap-Script-via-Jupiter-Exchange-API.git
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Configuration
Before running the script, create a `config.json` file in the same directory and configure it as follows:

```json
{
    "RPC_URL": "https://api.mainnet-beta.solana.com",
    "DEFAULT_SLIPPAGE_BPS": 50,
    "TOKENS": {
        "SOL": "So11111111111111111111111111111111111111112",
        "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        "JUP": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN"
    },
    "TOKEN_DECIMALS": {
        "SOL": 9,
        "USDC": 6,
        "USDT": 6,
        "JUP": 6
    },
    "WALLETS": [
        {
            "private_key": "...",
            "public_key": "..."
        },
        {
            "private_key": "...",
            "public_key": "..."
        }
    ]
}
```

### Configuration Details
- **RPC_URL**: The Solana RPC endpoint.
- **DEFAULT_SLIPPAGE_BPS**: Default slippage for swaps (50 basis points = 0.5%).
- **TOKENS**: Supported tokens with their mint addresses. New tokens can be added, but verify the contract address and decimals carefully.
- **TOKEN_DECIMALS**: Decimal places for each token.
- **WALLETS**: List of wallets with private and public keys.

## Running the Script
Run the script using:
```sh
python script.py
```

### User Input Commands
- Type `exit` in the console to stop the script safely.

## How It Works
1. A random wallet is chosen from the configuration.
2. The script checks the SOL balance:
   - If less than 0.01 SOL, it skips the wallet.
3. It swaps SOL (excluding 0.01 SOL for fees) for a random token.
4. Waits for a random period between **5 seconds and 2 minutes**.
5. Swaps the acquired token back to SOL.
6. Waits **10-15 seconds** before selecting the next wallet.
7. Repeats the cycle.

## Transaction Timing
- **Swap Holding Period:** 5 seconds to 2 minutes before converting tokens back to SOL.
- **Transition Delay:** 10-15 seconds before switching wallets.


### Adjusting Delays in Code
To modify the delays in the script, find the following lines in the code:
- **Swap Holding Period:** Adjust `random.randint(5, 120)` for the waiting period before swapping tokens back to SOL.
- **Transition Delay:** Change `random.randint(10, 15)` for the waiting time before selecting a new wallet.

Example:
```python
sleep_time = random.randint(5, 120)  # Time to wait before swapping back to SOL
transition_delay = random.randint(10, 15)  # Delay before switching wallets
```
Modify these values as needed to adjust timing behavior.

## Notes
- Ensure wallets have enough SOL to cover transaction fees.
- Logs all transactions and trading volumes for each wallet.
- You can add new tokens to the **TOKENS** list, but ensure you correctly set the **mint address** and **decimal places** to avoid transaction errors.

## Stopping the Script
To stop the script, type:
```sh
exit
```
Alternatively, press **Ctrl + C** to terminate it manually.

## License
This project is open-source and provided without warranty. Use at your own risk.

