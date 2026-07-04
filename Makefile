PORT ?= /dev/cu.usbmodem2113301
FILE ?= src/main.py

## Flash MicroPython firmware via serial (erases all data first)
write-flash-micron-python:
	esptool --chip esp32 --port ${PORT} erase-flash
	esptool --chip esp32 --port ${PORT} write-flash 0x1000 bins/ESP32_GENERIC-SPIRAM-20260406-v1.28.0.bin

## Backup entire flash to backup.bin
backup-bin:
	esptool -p ${PORT} read-flash 0x0 0x400000 backup.bin

## Restore flash from origin.bin
restore-bin:
	esptool --chip esp32 --port ${PORT} write-flash 0x0000 backup.bin

## Reset the board via DTR
reboot:
	ampy --port ${PORT} reset

## Upload src/lib/* to /lib on device
put_lib:
	ampy --port ${PORT} put src/lib /lib

## Upload FILE to device root -- default src/main.py
put:
	ampy --port ${PORT} put $(FILE)

## Connect serial console -- exit with ctrl-a k
attach:
	echo "'ctrl-a k' to stop"
	sleep 2
	screen ${PORT} 115200

## Install required Python tools
install-deps:
	pip install esptool
	pip install adafruit-ampy

## List available targets with descriptions
help:
	@grep -B1 -E '^[a-zA-Z_-]+:' Makefile | grep -v '^--' | paste - - | sed 's/## //;s/\t/: /' | awk -F': ' '{printf "  \033[1m%-30s\033[0m %s\n", $$2, $$1}'

## Check that required tools are available
check-deps:
	@missing=""; \
	for cmd in esptool.py ampy screen; do \
		if ! command -v $$cmd >/dev/null 2>&1; then \
			missing="$$missing $$cmd"; \
		fi; \
	done; \
	if [ -n "$$missing" ]; then \
		echo "Missing:$$missing"; \
		exit 1; \
	else \
		echo "All dependencies satisfied."; \
	fi
