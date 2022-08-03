"""
JSON FORMAT
{
    'success': '[TRUE OR FALSE]', 
    'name': '[NAME IDENTIFICATOR OF MODULE]', 
    'display_name': '[NAME THAT WILL BE DISPLAYED IN GUI]', 
    'description' : [NOT REQUIRED -> DESCRIPTION OF MODULE],
    'error': '[NOT REQUIRED -> ERROR MESSAGES]', 
    'variables': [
        {
            'name': '[STRING]', 
            'type': '[DATA TYPE OF VALUE]', 
            'value': [VALUE],
            'unit' : [NOT REQUIRED -> MEASURING UNIT],
        }, 
        {       
            'name': '[STRING]', 
            'type': '[DATA TYPE OF VALUE]', 
            'value': [VALUE],
            'unit' : [NOT REQUIRED -> MEASURING UNIT],
        }, 
        ... optional amount of variables
    ]
}

"""


import time, json, serial, random, os, sys, psycopg2
from datetime import datetime, timezone
from pprint import pprint


def config():
    return {
        "dbname" : "lucy_main",
        "user" : "lucy_modules",
        "password" : "lucy1234",
        "host"  : "localhost",
    }

# UNUSED
def add_module_to_db(name, display_name, description=" ", error=" "):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor() 
        cur.execute('INSERT INTO app_module (name, display_name, description, error, last_update) VALUES(%s, %s, %s, %s, %s)', (name, display_name, description, error, datetime.now(timezone.utc)))
        conn.commit()  
        cur.close()      
        
    except (Exception, psycopg2.DatabaseError) as error:
        print("-> ERROR while adding module: %s" % error)

    finally:
        if conn is not None:
            conn.close()

# UNUSED
def save_value_to_db(module_name, variable, data_type, value):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor() 
        cur.execute('INSERT INTO app_modulevalue (module_id, variable, data_type, value, unit, timestamp) VALUES((SELECT id from app_module WHERE name=%s), %s, %s, %s, %s, %s)', (module_name, variable, data_type, value, unit, datetime.now(timezone.utc)))
        conn.commit()  
        cur.close()      
        
    except (Exception, psycopg2.DatabaseError) as error:
        print("-> ERROR while adding module value: %s" % error)

    finally:
        if conn is not None:
            conn.close()



def is_module_in_db(module_name, conn):
    cur = conn.cursor()
    cur.execute('SELECT id FROM app_module WHERE name=%s', (module_name, ))
    rows = cur.fetchall()

    if rows:
        return True
    else:
        return False    


def save_data_to_db(data):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        module_name = data["name"]
        if not is_module_in_db(module_name, conn):
            cur.execute('INSERT INTO app_module (name, display_name, description, error, last_update)' \
                'VALUES(%s, %s, %s, %s, %s)', (module_name, data["display_name"], data.get("description", ""), data.get("error", ""), datetime.now(timezone.utc)))
        for variable in data["variables"]:
            cur.execute('INSERT INTO app_modulevalue (module_id, variable, data_type, value, unit, timestamp) VALUES((SELECT id FROM app_module WHERE name=%s), %s, %s, %s, %s, %s)', (module_name, variable["name"], variable["type"], variable["value"], variable.get("unit", ""), datetime.now(timezone.utc)))
        conn.commit()  
        cur.close()    

        print("-> data saved to database")  
        
    except (Exception, psycopg2.DatabaseError) as error:
        print("-> ERROR while saving data to database: %s" % error)

    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    print ("Ready...")
    sys.stdout.flush()

    while True:
        time.sleep(0.2)
        listOfInterfaces = [i for i in os.listdir('/dev') if (i.startswith('ttyUSB') or i.startswith('ttyACM'))]

        for interface in listOfInterfaces:
            sys.stdout.flush()
            time.sleep(2)
            for jk in range(1):
                try:
                    ser  = serial.Serial("/dev/%s" % interface, baudrate= 9600, 
                       timeout=2.5, 
                       parity=serial.PARITY_NONE, 
                       bytesize=serial.EIGHTBITS, 
                       stopbits=serial.STOPBITS_ONE
                    )
                    print("interface: %s" %  interface)
                    data = {}
                    data["operation"] = "REQUEST_DATA"


                    data = json.dumps(data)
                    buf = []

                    if ser.isOpen():
                        for x in (data):
                            buf.append(ord(x))

                        ser.write(bytearray(buf))
                        time.sleep(2)
                        ser.write(bytearray(buf))
                        try:
                            incoming = ser.readline().decode("utf-8")
                            
                            data = json.loads(incoming)
                            #print(data)

                            if data.get("success") == "true":
                                print("-> data recieved")
                                save_data_to_db(data)
                            elif data.get("success") == "false":
                                print("-> getting data wasn't sucessfull")
                            else:
                                print("-> data isn't valid")
                            
                            # print recieved data
                            # print("## RECIEVED DATA ##")
                            # print('Name: %s' % data["name"])
                            # print('Display_name: %s' % data["display_name"])
                            # for variable in data["variables"]:
                            #     print(variable["name"] + ": " + str(variable["value"]))
                            # print()
                        except Exception as e:
                            print (e)
                            ser.close()
                    else:
                        print ("-> opening error")
                except Exception as e:
                    print (e)
