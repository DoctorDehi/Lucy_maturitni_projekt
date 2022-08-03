"""
// COMMAND CODES
#define COMMAND_CONTINUE 0x00
#define COMMAND_STOP 0x01
#define COMMAND_RIDE_FORWARD 0x02
#define COMMAND_FORWARD_STEER_LEFT 0x03
#define COMMAND_FORWARD_STEER_RIGHT 0x04
#define COMMAND_RIDE_BACKWARD 0x05
#define COMMAND_BACKWARD_STEER_LEFT 0x06
#define COMMAND_BACKWARD_STEER_RIGHT 0x07
#define COMMAND_TURN_LEFT 0x08
#define COMMAND_TURN_RIGHT 0x09

#define COMMAND_SEND_STATE 0x11

#define COMMAND_SET_PWM_BYTE 0x21
#define COMMAND_SET_SPEED_LEVEL 0x22
#define COMMAND_SET_FREE_SPACE_MULTIPLIER 0x23

// STATE CODES
#define STOP 0x01
#define RIDE_FORWARD 0x02
#define FORWARD_STEER_LEFT 0x03
#define FORWARD_STEER_RIGHT 0x04
#define RIDE_BACKWARD 0x05
#define BACKWARD_STEER_LEFT 0x06
#define BACKWARD_STEER_RIGHT 0x07
#define TURN_LEFT 0x08
#define TURN_RIGHT 0x09
#define BARRIER_IN_FRONT_STOP 0x0A
#define BARRIER_IN_BACK_STOP 0x0B
#define NO_COMMUNICATION_STOP 0x0C

// STATUS CODES
#define OK 0x01
#define ERROR_BARRIER_IN_FRONT 0x02
#define ERROR_BARRIER_IN_BACK 0x03
#define ERROR_UKNOWN 0x11
#define ERROR_NO_VALUE 0x12
"""

import psycopg2, time, pytz, sys
from smbus2 import SMBus


addr = 0x8 # bus address
bus = SMBus(1) # indicates /dev/ic2-1

i2c_commands = {
    "COMMAND_CONTINUE" : 0x00,
    "COMMAND_STOP" : 0x01,
    "COMMAND_RIDE_FORWARD" : 0x02,
    "COMMAND_FORWARD_STEER_LEFT" : 0x03,
    "COMMAND_FORWARD_STEER_RIGHT" : 0x04,
    "COMMAND_RIDE_BACKWARD" : 0x05,
    "COMMAND_BACKWARD_STEER_LEFT" : 0x06,
    "COMMAND_BACKWARD_STEER_RIGHT" : 0x07,
    "COMMAND_TURN_LEFT" : 0x08,
    "COMMAND_TURN_RIGHT" : 0x09,

    "COMMAND_SEND_STATE" : 0x11,

    "COMMAND_SET_PWM_BYTE" : 0x21,
    "COMMAND_SET_SPEED_LEVEL" : 0x22,
    "COMMAND_SET_FREE_SPACE_MULTIPLIER" : 0x23,
}

status_codes = {
    0x01 : "OK",
    0x02 : "ERROR_BARRIER_IN_FRONT",
    0x03 : "ERROR_BARRIER_IN_BACK",
    0x11 : "ERROR_UKNOWN",
    0x12 : "ERROR_NO_VALUE",
}

state_codes = {
    0x01 : "STOP",
    0x02 : "RIDE_FORWARD", 
    0x03 : "FORWARD_STEER_LEFT", 
    0x04 : "FORWARD_STEER_RIGHT", 
    0x05 : "RIDE_BACKWARD", 
    0x06 : "BACKWARD_STEER_LEFT", 
    0x07 : "BACKWARD_STEER_RIGHT", 
    0x08 : "TURN_LEFT", 
    0x09 : "TURN_RIGHT", 
    0x0A : "BARRIER_IN_FRONT_STOP",
    0x0B : "BARRIER_IN_BACK_STOP", 
    0x0C : "NO_COMMUNICATION_STOP", 
}

def config():
    return {
        "dbname" : "lucy_main",
        "user" : "lucy_primary",
        "password" : "lucy1234",
        "host"  : "localhost",
    }


# load list of commands from database
def load_commands():
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT id, system_name FROM app_command ORDER BY id")

        rows = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print("ERROR while loading commands: %s" % error)
        rows = []
        cur.close()
    finally:
        if conn is not None:
            conn.close()

    commands = {}
    for key, val in rows: 
        commands[key] = val

    print("Commands loaded..")
    print(commands)
    return commands

# load commands to be executed from database
def load_commandexecutions(limit=20):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        if limit:
            cur.execute("SELECT id, timestamp, command_id, value FROM app_commandexecution WHERE state='Created' ORDER BY id LIMIT %i" % limit)
        else:
            cur.execute("SELECT id, timestamp, command_id, value FROM app_commandexecution WHERE state='Created' ORDER BY id")
        rows = cur.fetchall()

        # označí záznam v databázi jako načtený, zbytečně to zatěžuje SD kartu
        # for row in rows:
            #cur.execute("UPDATE app_commandexecution SET state = %s WHERE id = %s", ("Loaded", row[0]))
            # pass
        conn.commit()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("ERROR while loading command executions: %s" % error)
        rows = []
    finally:
        if conn is not None:
            conn.close()

    return rows

# set command execution̈́'s state in database to executed
def set_commandexecutions_executed(reports):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        for report in reports:
            cur.execute("UPDATE app_commandexecution SET state = %s, result = %s WHERE id = %s", ("Executed", report["result"], report["id"]))
        conn.commit()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("ERROR while marking command executions as executed: %s" % error)
        rows = []
    finally:
        if conn is not None:
            conn.close()


def do_command(command, value=0):
    try:
        command_code = i2c_commands[command]
        if command_code < 0x20:
            bus.write_byte(addr, command_code)
            # vyhodnocení příkazu někdy trvá trochu déle, zejména kvůli měření vzdálenosti, dáme tedy Micru trochu času
            time.sleep(0.05) 
        else:
            bus.write_block_data(addr, command_code, [value])
        print("Doing: %s" % command)
        return status_codes[bus.read_byte(addr)]
    except Exception as e:
        print("ERROR while doing command %s: %s" % (command, e))
        return "ERROR while doing command %s: %s" % (command, e)


def is_command_execution_valid(ce):
    if ce[1] > (time.time() - 2) * 1000: # if timestamp is created not earlier than 2 seconds ago
        return True
    else:
        # if command that should be executed isn't STOP
        if ce[2] != 2:
            return False
        else:
            return True

def main():
    commands = load_commands()
    
    # mark all command executions created before start as expired
    command_executions = load_commandexecutions(limit=None)
    reports = []
    for ce in command_executions:
        reports.append({
                "id" : ce[0],
                "result" : "ERROR: Primary circuit wasn't available",
            })
    set_commandexecutions_executed(reports)

    while True:
        try:

            sys.stdout.flush()
            command_executions = load_commandexecutions()


            
            reports = []
            for ce in command_executions:
                try:
                    if is_command_execution_valid(ce):
                        result = do_command(commands[ce[2]], ce[3])
                    else:
                        print("ERROR: Expired")
                        result = "ERROR: Expired"

                except ValueError as e:
                    print("ERROR in main loop: %s" % e)
                    result = "ERROR in primary circuit -> main loop: %s" % e

                reports.append({
                    "id" : ce[0],
                    "result" : result,
                })

            set_commandexecutions_executed(reports)

            time.sleep(0.05)
        except Exception as e:
            print(e)
            sys.stdout.flush()


if __name__ == '__main__':
    main()
