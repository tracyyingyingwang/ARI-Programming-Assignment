@authors: Niall Daly and Ying Wang

def get_avail_seats(c, row_num):
    row_query = "select instr(seats, seat) from rows_cols join seating where row = ? and name = '' order by 1 asc;"
    return c.execute(row_query, [row_num]).fetchall()

def get_consec_avail(c, avail, seats):
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
    for neighbour in max_consec_seats:
        consec+=seats[neighbour-1]
    return consec

def reject_remaining(conn, c, df, pos, end):
    query = "UPDATE metrics SET passengers_refused = passengers_refused + ? ;"
    for booking in range(pos, end):
        num_pass = df[1][booking]
        c.execute(query, str(num_pass))
        conn.commit()

def reject_one(conn, c, num_pass):
    query = "UPDATE metrics SET passengers_refused = passengers_refused + ? ;"
    c.execute(query, str(num_pass))
    conn.commit()

#not used yet
def passengers_separated(conn, c, num_pass):
    query = "UPDATE metrics SET passengers_separated = passengers_separated + ? ;"
    c.execute(query, str(num_pass))
    conn.commit()
    
def main():

    import sqlite3
    import pandas as pd

    df = pd.read_csv("bookings.csv", sep=",", skiprows=0, header=None)
    db_name = './airline_seating.db'

    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        seats = c.execute("SELECT seats FROM rows_cols;").fetchall()[0][0];
        nrows = c.execute("SELECT nrows FROM rows_cols;").fetchall()[0][0];

        upd_seat = "UPDATE seating SET name= ? WHERE row = ? AND seat = ? ;"

        for booking in range(0, len(df)):
            print(df[0][booking], "has a booking for", df[1][booking])
            seated = "F"
            check_row = "F"
            row = 1
            total_avail = 0
            while (seated == "F" and row <= nrows):
                avail = get_avail_seats(c, str(row))
                if avail:
                    total_avail+=len(avail)
                    check_row = "T"
                if row == nrows:
                    if total_avail == 0:
                        print("INFO: No more seats on the plane")
                        reject_remaining(conn, c, df, booking, len(df))
                        return
                    elif total_avail < df[1][booking]:
                        print("INFO: Not enough seats for this booking")
                        reject_one(conn, c, df[1][booking])
                    else:
                        print("INFO: Need to split this booking")
                        #WORK TO DO - split here
                if check_row == "T":
                    consec = get_consec_avail(c, avail, seats)
                    if len(consec) >= df[1][booking]:
                        print("INFO: BOOKED", df[0][booking], "row", row)
                        for seat in consec[0:df[1][booking]]:
                            c.execute(upd_seat, (df[0][booking], str(row), seat))
                            conn.commit()                    
                            seated = "T"
                    else:
                        print("INFO: Row", row, "too few consecutive seats:", len(consec))
                else:
                    print("INFO: No available seats in row", row)
                check_row = "F"
                row+=1
        
    except Exception as err:
        print("ERROR: ",err.args[0])
            
    return

if __name__ == "__main__":
    main()
