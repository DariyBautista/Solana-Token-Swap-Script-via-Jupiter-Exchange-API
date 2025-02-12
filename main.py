import json
import random
import base64
import requests
import httpx
import time
import threading

from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import to_bytes_versioned

# Load configuration
with open("config.json", "r") as f:
    config = json.load(f)

TOKENS = config["TOKENS"]
RPC_URL = config["RPC_URL"]
DEFAULT_SLIPPAGE_BPS = config["DEFAULT_SLIPPAGE_BPS"]
WALLETS = config["WALLETS"]
TOKEN_DECIMALS = config["TOKEN_DECIMALS"]

OUTPUT_TOKENS = [t for t in TOKENS.keys() if t != "SOL"]

running = True  # Global variable to control the loop

def user_input_listener():
    """Listens for user input to stop the script."""
    global running
    while True:
        command = input()
        if command.lower() == "exit":
            print("🛑 Exit command received. Stopping script...")
            running = False
            break

def get_balance(wallet, token):
    """Retrieves the balance of a specific token for a given wallet."""
    headers = {"Content-Type": "application/json"}
    if token == "SOL":
        data = {"jsonrpc": "2.0", "id": 1, "method": "getBalance", "params": [wallet["public_key"]]}
    else:
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                wallet["public_key"],
                {"mint": TOKENS[token]},
                {"encoding": "jsonParsed"}
            ]
        }
    try:
        response = httpx.post(RPC_URL, headers=headers, json=data)
        response_data = response.json()
        if "error" in response_data:
            print(f"❌ Error retrieving {token} balance: {response_data['error']['message']}")
            return None
        
        if token == "SOL":
            lamports = response_data.get("result", {}).get("value", 0)
            balance = lamports / 1_000_000_000
        else:
            accounts = response_data.get("result", {}).get("value", [])
            balance = sum(int(acc["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"]) for acc in accounts) / (10 ** TOKEN_DECIMALS[token])
        
        print(f"🪙 Balance {wallet['public_key']} - {balance} {token}")
        return balance
    except Exception as e:
        print(f"❌ Error retrieving {token} balance: {e}")
        return None

def swap(wallet, input_token, output_token, amount):
    """Performs a token swap using Jupiter API."""
    try:
        keypair = Keypair.from_base58_string(wallet["private_key"])
        amount = int(amount * (10 ** TOKEN_DECIMALS[input_token]))
        slippage_bps = DEFAULT_SLIPPAGE_BPS

        quote_url = f"https://quote-api.jup.ag/v6/quote?inputMint={TOKENS[input_token]}&outputMint={TOKENS[output_token]}&amount={amount}&slippageBps={slippage_bps}"
        quote_response = requests.get(quote_url).json()

        if "outAmount" not in quote_response:
            print("❌ Error: Missing outAmount field in API response")
            return None

        received_amount = int(quote_response["outAmount"]) / (10 ** TOKEN_DECIMALS[output_token])

        swap_url = "https://quote-api.jup.ag/v6/swap"
        swap_payload = {"quoteResponse": quote_response, "userPublicKey": str(keypair.pubkey()), "wrapAndUnwrapSol": True}
        swap_tx_response = requests.post(swap_url, json=swap_payload).json()

        if "swapTransaction" not in swap_tx_response:
            print(f"❌ Error: Missing swapTransaction in API response: {swap_tx_response}")
            return None

        swap_instruction = swap_tx_response["swapTransaction"]
        raw_tx = VersionedTransaction.from_bytes(base64.b64decode(swap_instruction))

        message_bytes = to_bytes_versioned(raw_tx.message)
        signature = keypair.sign_message(message_bytes)
        signed_tx = VersionedTransaction.populate(raw_tx.message, [signature])
        encoded_tx = base64.b64encode(bytes(signed_tx)).decode("utf-8")

        headers = {"Content-Type": "application/json"}
        data = {"jsonrpc": "2.0", "id": 1, "method": "sendTransaction", "params": [encoded_tx, {"skipPreflight": True, "preflightCommitment": "finalized", "encoding": "base64"}]}

        tx_response = httpx.post(RPC_URL, headers=headers, json=data)
        tx_hash = tx_response.json().get("result", "ERROR")
        print(f"✅ Swap {input_token} -> {output_token} completed, received: {received_amount} {output_token}")
        print(f"🔗 Transaction: https://solscan.io/tx/{tx_hash}")
        return received_amount
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    input_thread = threading.Thread(target=user_input_listener, daemon=True)
    input_thread.start()

    try:
        while running:
            wallet = random.choice(WALLETS)
            sol_balance = get_balance(wallet, "SOL")
            if sol_balance is None or sol_balance <= 0.01:
                print("❌ Not enough SOL for swapping.")
                continue

            swap_amount = sol_balance - 0.01
            output_token = random.choice(OUTPUT_TOKENS)

            swap(wallet, "SOL", output_token, swap_amount)
            sleep_time = random.randint(10, 60)
            print(f"⏳ Waiting {sleep_time} seconds before the next swap...")

            for _ in range(sleep_time):
                if not running:
                    break
                time.sleep(1)

            if not running:
                break

            new_balance = get_balance(wallet, output_token)
            if new_balance and new_balance > 0:
                swap(wallet, output_token, "SOL", new_balance)

            transition_delay = random.randint(10, 15)
            print(f"⏳ Delay of {transition_delay} seconds before selecting a new wallet...")

            for _ in range(transition_delay):
                if not running:
                    break
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Script stopped by user.")
