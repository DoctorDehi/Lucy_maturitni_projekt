import serial
ser = serial.Serial('/dev/ttyACM0') # rozhraní na které je micro připojeno 
# -> dá se zjistit pomocí "ls /dev"
ser.flushInput()

while True:
    try:
        ser_bytes = ser.readline()
        decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
        print(decoded_bytes)
    except Exception as e:
        print(e)
        print("Keyboard Interrupt")
        break
