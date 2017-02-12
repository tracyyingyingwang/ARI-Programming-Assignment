# ARL-Programming-Assignment
Created by Niall Daly and Ying Wang

A program that 
- reads bookings from a CSV file
- reads airplane-layout and passenger-seating info from a database
- assigns available seats to bookings, consecutively where possible
- persists the assignments to the database
- updates metrics table when passengers are rejected or separated

Key assumption:
A booking that does not fit into consecutive seats on a single row is considered fully separated in our metric. An extreme example would be a booking for 8 in a plane with 4 columns that gets seated 4 + 4 in consecutive rows. This is counted as 8 separated passengers. This might not be intuitive but it was our literal interpretation of the requirement.

Other assumptions:
The CSV file is in the same format as the one provided in the assignment i.e. comma-separated and no header row.
The database is in the same format as the one provided in the assignment; the metrics and rows_cols tables are assumed to have one row each.
The seating table is assumed to be already aligned with the rows_cols table. We do have a test function to re-align seating but it is not called by default.
Rows are assumed to be consecutively numbered starting from 1. The program is not designed to handle planes that skip 'unlucky' row 13.
Columns are assumed to be lettered but are not assumed to be consecutive.
If a booking cannot be fully accommodated then it will be rejected i.e. a booking for 3 with 2 seats remaining gets rejected.

Logic for assigning consecutive seats:
If a booking can be fully accommodated by consecutive available seats in any row then it will be booked.
If a booking cannot be fully accommodated in this way but there are sufficient available seats on the plane then the booking will be splitted and passengers will get booked individually in order of available seats, starting from the first row and column.
Our testing observed that this logic resulted in near-optimal positioning of passengers with their companions; more so than you might intially expect.

Logging:
The program generates logs for every successful and unsuccessful attempt to process a booking in a row. This is useful for auditing and was also extremely useful for testing.

Testing:
The program has been tested against differently named CSV and DB files, and different layouts for the plane. The quality of the logging led to straightforward testing and debugging of issues. Our system testing strategy was to generate different test data via SQL (using DB Browser for SQLite), run the program, analyse the logs and verify the output on the database. For this reason there is only one function in the program solely for testing - it rebuilds an empty seating table from the current values of the rows_cols table.

Sample SQL file that was created to reset the tables after a test run
UPDATE seating SET name = '' WHERE row > 1 or (row = 1 and seat not in ('A', 'C'));
UPDATE metrics SET passengers_refused = 0;
UPDATE metrics SET passengers_separated = 0;
commit;
