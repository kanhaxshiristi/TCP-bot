from flask import Flask, request, Response
import asyncio
import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import threading

app = Flask(__name__)

# توكنات الحسابات
SPAM_TOKENS = {
    "3849913366": "FDD8A9206919D728DA6F8F5927317BFF425680851A04F488F7BBC526992F3CB4",
    "3849915829": "7239404EF06C63A3677379AB4D01B3F1AC8A4A2E3FE894F1520CAA41BC039369",
    "3849916557": "3F584A49CB73D20D74FFA1AF3E3A82F9B3C8F71CFD7B3A9BF181D47067845E5C",
    "3849917256": "38E5E59C112A0C11A1EB49C9DA655EDE6D1C4237D4F7E20AE609D0C9A4ABB024",
    "3849917941": "88AAD96689F4CC7A452D3E66D32953DF0F293BF824480311E39C4DCAB0C6EEF8",
    "3849918646": "4D29237BE56DA8794625DEF86F9B0014571F15D775DBECF0100AA8D2E7948594",
    "3849919377": "13AE99C7C65D6E2488C8ADA76EE06D0DECA95C3C3D604891B2D7B9FF794EFD79",
    "3849920108": "E885838B6585169F508A905CD877A410004747B31A87BB0913834D1AD22A94A7",
    "3849920858": "3EF6C2EA2E2C244C7355FCC0B7587708B7446563396E6FB1CDF083D36A55EF7B",
    "3849921551": "7CF2322921C2310A98A8DD6ED5D8532459240FB1CE17E72ED2F9A8A39B36F3E5",
    "3849922288": "FF11CA07842511C5A86F4CF142653097A6991A437A8961A5E253B53060DF1F45",
    "3849922979": "233BC432395D64C70E051D6CC75A1A1CFEE6B9EA5ECF11F52EDAB472382C66C7",
    "3849923672": "FCB436C5442F256BDB0E170DCD53252DA9DE703A1C0197C909795CAB10B4C85A",
    "3849924391": "971B223533A4951B3B680857D3939DA97818DF27F272747DD0CF7C8D8ED55C12",
    "3849925111": "09F8B2E87F75027A60793EA55DE3DE4B4C669E3630F0134DC3326D073EE5F046",
    "3849925814": "3AB00F4CF1A372C8C23873A0F4141C3C2FEB6B6C2D9CADA3C4688F641619057E",
    "3849926523": "D12699D802D6DABEF3B9BC0DDC454F15AEFD8395745F7BFAEB09C7CE443610F4",
    "3849927215": "8A6D7D7B011CEB092776547E5495F3BB67DDF7EEA399B85F7E2E6694BC907BF1",
    "3849927929": "CF2C73180C82CE08D313164098F360EB5EA9D2EDC1BF725BBBFD860C5BF3CE40",
    "3849928630": "448C0634519F1E1F4BF706AA0BA72B029AF1EB78FF9FFB88103B909B76FF6BDC",
    "3849929381": "EC0E4F4ED512CE44224559ED895531FCA4FE3CFC63C203ED2ED68527F99BA39E",
    "3849930123": "A21743D8F1546D4564247EC5CD9F829401F9DF93133D610A78968A6D6C0D85C6",
    "3849930829": "D024CF5B893CEBE0E951CEA5325953C0142D3915B0E5E84635E465C3A062DEB5",
    "3849931568": "65024ADBCB0C5839776D5D4EEBED185429E4A126935CE0D4EBF79CB7AD59D44A",
    "3849932267": "19620892103DBA34A6466C99B14DF927262598F34D7956A1EE011CAB79929FA4",
    "3849933023": "11DDD43A3FB389FF437D74BD574A41A119FB1105FA2EC44DB126D3A85459A85E",
    "3849933722": "3F70A851223DFA7FCC286EA0BD2D4D4D3B9E257948F29555709C4F75C027791D",
    "3849934480": "8AB9B90A7DB388280C595FF6D3C90C631BB0D427F06A1268F255D4DCA1A551C8"
}





# تعريف دالة Encrypt_ID المفقودة
def Encrypt_ID(x):
    x = int(x)
    dec = ['80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9a', '9b', '9c', '9d', '9e', '9f', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 'db', 'dc', 'dd', 'de', 'df', 'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']
    xxx = ['1', '01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', '2b', '2c', '2d', '2e', '2f', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', '4c', '4d', '4e', '4f', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', '6d', '6e', '6f', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '7e', '7f']
    x = x / 128
    if x > 128:
        x = x / 128
        if x > 128:
            x = x / 128
            if x > 128:
                x = x / 128
                strx = int(x)
                y = (x - int(strx)) * 128
                stry = str(int(y))
                z = (y - int(stry)) * 128
                strz = str(int(z))
                n = (z - int(strz)) * 128
                strn = str(int(n))
                m = (n - int(strn)) * 128
                return dec[int(m)] + dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
            else:
                strx = int(x)
                y = (x - int(strx)) * 128
                stry = str(int(y))
                z = (y - int(stry)) * 128
                strz = str(int(z))
                n = (z - int(strz)) * 128
                strn = str(int(n))
                return dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]

# وظيفة التشفير
def encrypt_api(plain_text):
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(bytes.fromhex(plain_text), AES.block_size)).hex()

# بقية الكود يبقى كما هو...

# وظيفة التشفير
def encrypt_api(plain_text):
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(bytes.fromhex(plain_text), AES.block_size)).hex()

# جلب التوكن
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

# إرسال طلب الصداقة
async def send_friend_request(id, token):
    url = 'https://client.ind.freefiremobile.com/RequestAddingFriend'
    headers = {
        'X-Unity-Version': '2018.4.11f1',
        'ReleaseVersion': 'OB49',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-GA': 'v1 1',
        'Authorization': f'Bearer {token}',
        'Content-Length': '16',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
        'Host': 'clientbp.ggblueshark.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }
    encrypted_data = encrypt_api(f'08a7c4839f1e10{Encrypt_ID(id)}1801')
    data = bytes.fromhex(encrypted_data)
    
    try:
        async with httpx.AsyncClient(verify=False, timeout=60) as client:
            response = await client.post(url, headers=headers, data=data)
            if response.status_code == 200:
                return f"Sent to{id}"
            return f"mistake: {response.text}"
    except Exception as e:
        return f"to fail: {str(e)}"

# العملية الرئيسية
async def process_account(uid, pw, id):
    token = await get_jwt_async(uid, pw)
    if token:
        return await send_friend_request(id, token)
    return f"Failed to fetch token for{uid}"

async def process_all_accounts(id):
    tasks = []
    for uid, pw in SPAM_TOKENS.items():
        task = asyncio.create_task(process_account(uid, pw, id))
        tasks.append(task)
    return await asyncio.gather(*tasks)

def run_async(id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(process_all_accounts(id))
    loop.close()
    print("Results:", results)

@app.route('/spam')
def spam():
    id = request.args.get('id')
    if id:
        thread = threading.Thread(target=run_async, args=(id,))
        thread.start()
        return "Sending friend requests..."
    return "You must enter a valid ID"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8398)