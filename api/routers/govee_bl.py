import asyncio
import time
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice


DEVICE_NAME = "ihoment_H615A_2956"
MODEL_NUMBER_UUID = "00002a24-0000-1000-8000-00805f9b34fb"
MSG_GET_AUTH_KEY = "aab100000000000000000000000000000000001b"
SEND_CHARACTERISTIC_UUID = "00010203-0405-0607-0809-0a0b0c0d2b11"
RECV_CHARACTERISTIC_UUID = "00010203-0405-0607-0809-0a0b0c0d2b10"


async def main():
    device, _ = await find_device(DEVICE_NAME)
    if device is None:
        print(f"Could not find device with name {DEVICE_NAME}")
        return

    async with BleakClient(device.address) as client:
        stop_event = asyncio.Event()

        async def recv_handler(charact, msg):
            if len(msg) != 20:
                return

            if msg[0] == 0xAA and msg[1] == 0xB1:
                auth_key = extract_auth_key(msg)
                if auth_key is not None:
                    print(f"Auth key: {auth_key.hex()}")
                    stop_event.set()
                else:
                    print(f"Could not extract auth key from {msg.hex()}")
                    time.sleep(1)
                    await send_get_auth_key(client)

        await client.start_notify(RECV_CHARACTERISTIC_UUID, recv_handler)
        await send_get_auth_key(client)
        await stop_event.wait()
        await client.stop_notify(RECV_CHARACTERISTIC_UUID)


async def find_device(name):
    devices = await BleakScanner.discover(timeout=5, return_adv=True)
    for _, (device, adv_data) in devices.items():
        if adv_data.local_name == name:
            return (device, adv_data)
    return (None, None)


def extract_auth_key(msg):
    if msg[2] != 0x01:
        return None
    key = msg[3:-1]
    return key


async def send_get_auth_key(client):
    ba = bytearray.fromhex(MSG_GET_AUTH_KEY)
    await client.write_gatt_char(SEND_CHARACTERISTIC_UUID, ba)


asyncio.run(main())
