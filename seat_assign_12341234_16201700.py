@authors: Niall Daly and Ying Wang
import random
class Booking:
    def __init_self_():
        pass
    def get_avail_seats(c, row_num):
        row_query = "select instr(seats, seat) from rows_cols join seating where row = ? and name = '' order by 1 asc;"
        return c.execute(row_query, [row_num]).fetchall()

    def get_consec_avail(c, avail, seats):
        max_consec_seats = avail[0]
        cur_consec_seats = avail[0]
        for i in range(0, len(avail)-1):
            if avail[i][0] + 1 != avail[i+1][0]: 
                cur_consec_seats = avail[i+1]
            else:
                cur_consec_seats = cur_consec_seats + avail[i+1] 
        for neighbour in max_consec_seats:
            consec+=seats[neighbour-1]
        return consec
    def reject(conn, c, num_pass):
        query = "UPDATE metrics SET passengers_refused = passengers_refused + ? ;"
        c.execute(query, str(num_pass))
        conn.commit()

    def passengers_separated(conn, c, num_pass):
        query = "UPDATE metrics SET passengers_separated = passengers_separated + ? ;"
        c.execute(query, str(num_pass))
        conn.commit()
    
