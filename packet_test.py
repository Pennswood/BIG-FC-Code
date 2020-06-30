import threading
import ospp
import oasis_serial

from oasis_config import ROVER_RX_PORT, ROVER_TX_PORT, TLC_RX_PORT,\
	TLC_TX_PORT, DEBUG_MODE, SD_PATH, DEBUG_FLASH_PATH, FLASH_PATH,\
	DEBUG_SD_PATH, LOGGING_INTERVAL, ROVER_BAUD_RATE, TLC_BAUD_RATE

# Talk to Tyler to learn what this line does :)
rover_serial = oasis_serial.OasisSerial("/dev/ttyS1", debug_mode=DEBUG_MODE,
		debug_tx_port=ROVER_TX_PORT, debug_rx_port=ROVER_RX_PORT, rx_print_prefix="BBB RX] ")

pm = ospp.PacketManager(rover_serial)

running = True

def print_loop(pm):
	global running
	while running:
		if len(pm._rx_buffer) != 0:
			print("Got packet:")
			print(pm._rx_buffer.pop())
			
	print("Print loop exit")

t = threading.Thread(target=print_loop, args=(pm,))
t.start()

while input() != "exit":
	print("Enter 'exit' to stop")
	
print("Exiting...")
running = False
t.join()
pm.running = False