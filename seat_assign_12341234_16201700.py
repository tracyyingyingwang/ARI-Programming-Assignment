# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 15:50:32 2017

@authors: Niall and Tracy
"""

def get_avail_seats(c, row_num):
    row_query = "select instr(seats, seat) from rows_cols join seating where row = ? and name = '' order by 1 asc;"
    return c.execute(row_query, [row_num]).fetchall()
