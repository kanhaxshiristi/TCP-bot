from flask import Flask, request
import asyncio
import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import threading

app = Flask(__name__)

SPAM_TOKENS = {
    "3997271134": "BF9195F9C89E650DA3FB8B92795B6031E86BA2D8226B2C313252CC3566B46037",
}

def Encrypt_ID(x):
    x = int(x)
    dec = [f"{i:02x}" for i in range(128, 256)]  # ['80' to 'ff']
    xxx = [f"{i:02x}" for i in range(1, 128)]    # ['01' to '7f']
    x = x / 128
    parts = []

    for _ in range(4):
        int_part = int(x)
        frac_part = x - int_part
        next_val = int(frac_part * 128)
        parts.append(next_val)
        x = frac_part * 128

    int_x = int(x)
    if any(i >= len(dec) for i in parts) or int_x >= len(xxx):
        raise ValueError("ID value out of supported range")

    return ''.join(dec[i] for i in reversed(parts)) + xxx[int_x]

def encrypt_api(plain_text):
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(bytes.fromhex(plain_text), AES.block_size)).hex()

async def get_jwt_async(uid, password):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://uditanshu-jwt-ob49.vercel.app/token?uid={uid}&password={password}",
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get("token")
    except:
        return None

async def send_friend_request(player_id, token):
    url = 'https://client.ind.freefiremobile.com/RequestAddingFriend'
    headers = {
        'X-Unity-Version': '2018.4.11f1',
        'ReleaseVersion': 'OB49',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-GA': 'v1 1',
        'Authorization': f'Bearer {token}',
        'Content-Length': '16',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
        'Host': 'client.ind.freefiremobile.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }

    encrypted_data = encrypt_api(f'08a7c4839f1e10{Encrypt_ID(player_id)}1801')
    data = bytes.fromhex(encrypted_data)

    try:
        async with httpx.AsyncClient(verify=False, timeout=60) as client:
            response = await client.post(url, headers=headers, data=data)
            if response.status_code == 200:
                print(f"[✔] Sent Friend Request to ID: {player_id}")
                return f"Friend request sent to ID: {player_id}"
            return f"[✘] Error: {response.text}"
    except Exception as e:
        return f"[✘] Failed: {str(e)}"

async def process_account(uid, pw, player_id):
    token = await get_jwt_async(uid, pw)
    if token:
        return await send_friend_request(player_id, token)
    return f"[✘] Failed to fetch token for {uid}"

async def process_all_accounts(player_id):
    tasks = []
    for uid, pw in SPAM_TOKENS.items():
        task = asyncio.create_task(process_account(uid, pw, player_id))
        tasks.append(task)
    return await asyncio.gather(*tasks)

def run_async(player_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(process_all_accounts(player_id))
    loop.close()
    print("Results:", results)

@app.route('/addfriend')
def spam():
    player_id = request.args.get('id')
    if player_id:
        thread = threading.Thread(target=run_async, args=(player_id,))
        thread.start()
        return f"Friend request process started for ID: {player_id}"
    return "Error: You must provide a valid ID."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
