import json
import aiohttp
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class DataEncrypt:
    """
    The real-time data needs to be AES encrypted
    """

    def __init__(self, serial_number: str, url: str):
        self.url = url
        self.iv = bytes(
            [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f])
        self.serial_number = str(serial_number)
        self.login_request_body = "optType=newParaSetting&subOption=pwd&Value=" + self.serial_number
        self.real_time_body = "optType=ReadRealTimeData&pwd=" + self.serial_number
        self.key = ""
        self.token = ""

    async def encrypt(self, plain_text: bytes):
        aes = AES.new(self.key, AES.MODE_CBC, self.iv)
        cipher_text = aes.encrypt(pad(plain_text, AES.block_size))
        return cipher_text

    async def decrypt(self, cipher_text: bytes):
        aes = AES.new(self.key, AES.MODE_CBC, self.iv)
        decrypted_text = unpad(aes.decrypt(cipher_text), AES.block_size)
        return decrypted_text

    async def get_token_key(self, datahub_sn: str):
        """
        Generate AES encrypted key based on SN number
        """
        ret = ''
        mqtt_login_password = [0] * 8
        mqtt_login_password[0] = datahub_sn[7]
        mqtt_login_password[1] = datahub_sn[4]
        mqtt_login_password[2] = datahub_sn[3]
        mqtt_login_password[3] = datahub_sn[6]
        mqtt_login_password[4] = datahub_sn[5]
        mqtt_login_password[5] = datahub_sn[2]
        mqtt_login_password[6] = datahub_sn[9]
        mqtt_login_password[7] = datahub_sn[8]
        for i in range(0, len(mqtt_login_password)):
            mqtt_login_password[i] = chr(ord(mqtt_login_password[i]) ^ 11)
            if mqtt_login_password[i].isalpha() or mqtt_login_password[i].isdigit():
                ret += mqtt_login_password[i]
            else:
                ret += 'A'

        return ret.encode('utf-8').hex()

    async def fill_16_byte(self, original_hex: str):
        """
        Complete the string length to 16 bits
        """
        byte_string = bytes.fromhex(original_hex)
        padding_bytes = 16 - len(byte_string)
        padded_byte_string = byte_string + bytes([0] * padding_bytes)
        padded_hex_string = padded_byte_string.hex()
        return bytes.fromhex(padded_hex_string)

    async def get_token(self, encodebytes: bytes):
        decrypted_text = await self.decrypt(encodebytes)
        res_data = decrypted_text.decode()
        res_data_json = json.loads(res_data)
        self.token = res_data_json.get("data").get("token")

    async def get_real_time(self) -> bytes:
        headers = {
            "token": self.token,
            "Content-Type": "application/json"
        }
        real_time_text = await self.encrypt(self.real_time_body.encode('utf8'))

        real_time_base64 = base64.b64encode(real_time_text)

        real_time_data = real_time_base64.decode('utf8')
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=headers, data=real_time_data) as req:
                response = await req.text()

        real_time = response
        encode_bytes = base64.decodebytes(real_time.encode('utf-8'))
        decrypted_text = await self.decrypt(encode_bytes)

        return decrypted_text

    async def get_encrypt_data(self) -> bytes:
        """
        Decrypt data By AES
        """
        self.key = await self.fill_16_byte(await self.get_token_key(self.serial_number))

        encrypt_text = await self.encrypt(self.login_request_body.encode('utf8'))

        encode_strs = base64.b64encode(encrypt_text)

        login_data = encode_strs.decode('utf8')
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=login_data) as req:
                response = await req.text()

        encodebytes = base64.decodebytes(response.encode('utf-8'))
        await self.get_token(encodebytes)
        return await self.get_real_time()
