import asyncio
from bleak import BleakScanner, BleakClient
import numpy as np
import argparse

def compute_rmssd(rr_ms):
    if len(rr_ms) < 2:
        return None
    rr_diff = np.diff(rr_ms)
    squared_diff = rr_diff ** 2
    rmssd = np.sqrt(np.mean(squared_diff))
    return rmssd

async def main(collection_duration):
    print("🔍 Scanning for BLE devices...")
    devices = await BleakScanner.discover()

    # Find the XOSS device
    xoss_device = None
    for d in devices:
        if d.name and "XOSS" in d.name.upper():  # Check if name exists before using it
            xoss_device = d
            print(f"✅ Found device: {d.name} ({d.address})")
            break

    if not xoss_device:
        print("❌ XOSS device not found.")
        return

    # Connect to the device
    async with BleakClient(xoss_device.address) as client:
        print("🔗 Connected!")
        print("📡 Listing services and characteristics...")

        for service in client.services:
            print(f"Service: {service.uuid} ({service.description})")
            for char in service.characteristics:
                props = ", ".join(char.properties)
                print(f"  └─ Characteristic: {char.uuid} ({props})")

        # Heart Rate Service UUIDs
        HR_CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"  # Heart Rate Measurement
        RR_CHAR_UUID = "00002a38-0000-1000-8000-00805f9b34fb"  # Body Sensor Location

        # Store all RR intervals
        all_rr_intervals = []

        def hr_callback(sender, data):
            # Parse heart rate data according to Bluetooth specification
            # First byte contains flags
            flags = data[0]
            # Check if RR intervals are present (bit 4 of flags)
            rr_intervals_present = bool(flags & 0x10)
            
            if rr_intervals_present:
                # Calculate heart rate
                if flags & 0x01:  # 16-bit heart rate
                    hr = int.from_bytes(data[1:3], byteorder='little')
                    rr_start = 3
                else:  # 8-bit heart rate
                    hr = data[1]
                    rr_start = 2
                
                # Extract RR intervals (each RR interval is 2 bytes)
                rr_intervals = []
                for i in range(rr_start, len(data), 2):
                    if i + 1 < len(data):
                        rr = int.from_bytes(data[i:i+2], byteorder='little')
                        rr_intervals.append(rr)
                
                # Store RR intervals
                all_rr_intervals.extend(rr_intervals)
                
                print(f"❤️ Heart Rate: {hr} BPM")
                print(f"📏 RR Intervals: {rr_intervals} ms")
            else:
                print("⚠️ No RR intervals in this measurement")

        # Check if the heart rate characteristic exists in any service
        hr_char_found = False
        for service in client.services:
            for char in service.characteristics:
                if char.uuid == HR_CHAR_UUID:
                    hr_char_found = True
                    break
            if hr_char_found:
                break

        if hr_char_found:
            print("📥 Subscribing to Heart Rate notifications...")
            await client.start_notify(HR_CHAR_UUID, hr_callback)
            print(f"⏳ Waiting for heart rate data ({collection_duration} seconds)...")
            await asyncio.sleep(collection_duration)  # Keep receiving data
            await client.stop_notify(HR_CHAR_UUID)
            
            # Calculate HRV metrics
            if all_rr_intervals:
                print("\n📊 HRV Analysis:")
                print(f"Total RR intervals collected: {len(all_rr_intervals)}")
                rmssd = compute_rmssd(all_rr_intervals)
                if rmssd is not None:
                    print(f"RMSSD: {rmssd:.2f} ms")
                    print(f"HRV Score: {rmssd:.2f} ms")
                else:
                    print("⚠️ Not enough RR intervals for HRV calculation")
            else:
                print("⚠️ No RR intervals were collected")
        else:
            print("⚠️ Heart Rate Measurement characteristic not found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='HRV Monitor for XOSS heart rate straps')
    parser.add_argument('-d', '--duration', type=int, default=20,
                      help='Duration of data collection in seconds (default: 20)')
    args = parser.parse_args()
    
    asyncio.run(main(args.duration))
