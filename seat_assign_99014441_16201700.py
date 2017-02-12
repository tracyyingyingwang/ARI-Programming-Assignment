"""
# -*- coding: utf-8 -*-
@authors: Niall Daly and Ying Wang
"""

def get_avail_seats(c, row_num):
    """returns unoccupied NUMBERED seats in a row e.g. 13 means first and third seats in row"""
    row_query = "select instr(seats, seat) from rows_cols join seating where row = ? and name = '' order by 1 asc;"
    return c.execute(row_query, [row_num]).fetchall()

def get_consec_avail(c, avail, seats):
    """returns max consecutive set of unoccupied LETTERED seats in a row"""    
    consec = []
    max_consec_seats = avail[0]
    cur_consec_seats = avail[0]
    for i in range(0, len(avail)-1):
        if avail[i][0] + 1 != avail[i+1][0]:
            cur_consec_seats = avail[i+1]
        else:
            cur_consec_seats = cur_consec_seats + avail[i+1]
        if len(cur_consec_seats) > len(max_consec_seats):
            max_consec_seats = cur_consec_seats
    #max_consec_seats is NUMBERED so switch here to LETTERED
    for neighbour in max_consec_seats:
        consec+=seats[neighbour-1]
    return consec

def reject_remaining(conn, c, df, pos, end):
    """the plane is full, reject the remaining bookings from position POS"""
    query = "UPDATE metrics SET passengers_refused = passengers_refused + ? ;"
    for booking in range(pos, end):
        num_pass = df[1][booking]
        c.execute(query, str(num_pass))
        conn.commit()
        
def reject_one(conn, c, num_pass):
    "the plane is not full but there are too few seats for this booking"
    query = "UPDATE metrics SET passengers_refused = passengers_refused + ? ;"
    c.execute(query, str(num_pass))
    conn.commit()

def passengers_separated(conn, c, num_pass):
    """
    a booking that does not fit into consecutive seats on a row is considered fully separated
    from spec: "how many passengers are seated away from any other member of their party"
    in this case passengers get seated individually in the next available seat
    incidentally they are likely to be well-grouped but in some cases they will not   
    """
    query = "UPDATE metrics SET passengers_separated = passengers_separated + ? ;"
    c.execute(query, (str(num_pass),))
    conn.commit()

def prepare_seating_from_rows_cols(conn, c):
    """this function is for testing only: change rows_cols and rebuild seating"""    
    seats = c.execute("SELECT seats FROM rows_cols;").fetchall()[0][0];
    nrows = c.execute("SELECT nrows FROM rows_cols;").fetchall()[0][0];
    c.execute("DELETE FROM seating");
    for seat in range(0, len(seats)):
        for row in range(1, nrows+1):
            query = "INSERT INTO seating (row, seat, name) VALUES (? , ? , '');"
            c.execute(query, (str(row),seats[seat]))
    conn.commit()

def process_booking(conn, c, df, booking, name, num_pass, level):
    """
    first try to assign consecutive seats in a row
    then either reject the booking if there are too few seats in total
    or split the booking and seat passengers individually in next available seat
    """
    print(name, "has a booking for", num_pass)
    seats = c.execute("SELECT seats FROM rows_cols;").fetchall()[0][0];
    nrows = c.execute("SELECT nrows FROM rows_cols;").fetchall()[0][0];
    upd_seat = "UPDATE seating SET name= ? WHERE row = ? AND seat = ? ;"
    seated = "F"
    check_row = "F"
    row = 1          
    total_avail = 0
    while (seated == "F" and row <= nrows):
        avail = get_avail_seats(c, str(row))
        if avail:
            total_avail+=len(avail)
            check_row = "T" #purpose of flag is to prevent error below when avail is empty
        if row == nrows:
            if total_avail == 0:
                print("INFO: No more seats on the plane")
                reject_remaining(conn, c, df, booking, len(df))
                return "FULL"
            elif total_avail < num_pass:
                print("INFO: Not enough seats for this booking")
                reject_one(conn, c, num_pass)
                return
            elif len(avail) < num_pass:
                print("INFO: Row 15 too few consecutive seats. Split..")
                for i in range(1, num_pass+1):
                    #recursive call for ONE passenger, handles any number fewer than num_pass tho
                    process_booking(conn, c, df, booking, name, 1, level+1)
                #level required here to prevent double-counting separation
                if level == 1:
                    passengers_separated(conn, c, num_pass)
                return                                   
        if check_row == "T":
            consec = get_consec_avail(c, avail, seats)
            if len(consec) >= num_pass:
                print("INFO: BOOKED", name, "row", row)
                for seat in consec[0:num_pass]:
                    c.execute(upd_seat, (name, str(row), seat))
                    conn.commit()              
                    seated = "T"                    
            else:
                print("INFO: Row", row, "too few consecutive seats:", len(consec))
        else:
            print("INFO: No available seats in row", row)
        check_row = "F"
        row+=1
    return
    

def main():

    """loop through the bookings and process individually"""

    import sys
    import sqlite3
    import pandas as pd

    try:
        if(len(sys.argv) == 3):
            print("INFO: filenames specified are", sys.argv[1], sys.argv[2])
            db_name = sys.argv[1]
            df_name = sys.argv[2]
            df = pd.read_csv(df_name, sep=",", skiprows=0, header=None)
        else:
            print("WARNING: Unexpected parameters provided, proceeding with default filenames")
            db_name = './airline_seating.db'
            df = pd.read_csv("bookings.csv", sep=",", skiprows=0, header=None)
            
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        #prepare_seating_from_rows_cols(conn, c)   #only used for testing changes to rows_cols
        for booking in range(0, len(df)):
            if process_booking(conn, c, df, booking, df[0][booking], df[1][booking], 1) == "FULL":
                return
    except Exception as err:
        print("ERROR: ",err.args[0])
            
    return

if __name__ == "__main__":
    main()
