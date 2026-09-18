  IDENTIFICATION DIVISION.
       PROGRAM-ID. CUSTOMER-CRUD.
 
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
 
           SELECT CUSTOMER-FILE ASSIGN TO "CUSTOMER.DAT"
               ORGANIZATION IS SEQUENTIAL
               ACCESS MODE IS SEQUENTIAL
               FILE STATUS IS WS-FILE-STATUS.
 
       DATA DIVISION.
       FILE SECTION.
 
       FD CUSTOMER-FILE.
       01 CUSTOMER-RECORD.
           05 CUSTOMER-ID       PIC 9(5).
           05 CUSTOMER-NAME     PIC X(30).
           05 CUSTOMER-EMAIL    PIC X(40).
           05 CUSTOMER-PHONE    PIC X(15).
           05 CUSTOMER-CITY     PIC X(20).
           05 CUSTOMER-BALANCE  PIC 9(7)V99.
           05 CUSTOMER-STATUS   PIC X(1).
 
       WORKING-STORAGE SECTION.
 
       01 WS-FILE-STATUS        PIC XX.
       01 WS-EOF                PIC X VALUE "N".
 
       01 WS-CHOICE             PIC 9.
       01 WS-SEARCH-ID          PIC 9(5).
       01 WS-FOUND              PIC X VALUE "N".
 
       01 WS-NEW-NAME           PIC X(30).
       01 WS-NEW-EMAIL          PIC X(40).
       01 WS-NEW-PHONE          PIC X(15).
       01 WS-NEW-CITY           PIC X(20).
       01 WS-NEW-BALANCE        PIC 9(7)V99.
 
       PROCEDURE DIVISION.
 
       MAIN-PROCEDURE.
 
           PERFORM UNTIL WS-CHOICE = 6
 
               DISPLAY " "
               DISPLAY "===================================="
               DISPLAY "       CUSTOMER MANAGEMENT SYSTEM"
               DISPLAY "===================================="
               DISPLAY "1. CREATE CUSTOMER"
               DISPLAY "2. READ CUSTOMER"
               DISPLAY "3. UPDATE CUSTOMER"
               DISPLAY "4. DELETE CUSTOMER"
               DISPLAY "5. DISPLAY ALL CUSTOMERS"
               DISPLAY "6. EXIT"
               DISPLAY "===================================="
               DISPLAY "ENTER YOUR CHOICE: "
               ACCEPT WS-CHOICE
 
               EVALUATE WS-CHOICE
                   WHEN 1
                       PERFORM CREATE-CUSTOMER
 
                   WHEN 2
                       PERFORM READ-CUSTOMER
 
                   WHEN 3
                       PERFORM UPDATE-CUSTOMER
 
                   WHEN 4
                       PERFORM DELETE-CUSTOMER
 
                   WHEN 5
                       PERFORM DISPLAY-ALL-CUSTOMERS
 
                   WHEN 6
                       DISPLAY "APPLICATION TERMINATED."
 
                   WHEN OTHER
                       DISPLAY "INVALID OPTION."
               END-EVALUATE
 
           END-PERFORM.
 
           STOP RUN.
 
 
       CREATE-CUSTOMER.
 
           DISPLAY " "
           DISPLAY "----- CREATE CUSTOMER -----"
 
           DISPLAY "ENTER CUSTOMER ID: "
           ACCEPT CUSTOMER-ID
 
           DISPLAY "ENTER CUSTOMER NAME: "
           ACCEPT CUSTOMER-NAME
 
           DISPLAY "ENTER EMAIL: "
           ACCEPT CUSTOMER-EMAIL
 
           DISPLAY "ENTER PHONE: "
           ACCEPT CUSTOMER-PHONE
 
           DISPLAY "ENTER CITY: "
           ACCEPT CUSTOMER-CITY
 
           DISPLAY "ENTER BALANCE: "
           ACCEPT CUSTOMER-BALANCE
 
           DISPLAY "ENTER STATUS (A/I): "
           ACCEPT CUSTOMER-STATUS
 
           OPEN EXTEND CUSTOMER-FILE
 
           IF WS-FILE-STATUS NOT = "00"
               CLOSE CUSTOMER-FILE
               OPEN OUTPUT CUSTOMER-FILE
           END-IF
 
           WRITE CUSTOMER-RECORD
 
           IF WS-FILE-STATUS = "00"
               DISPLAY "CUSTOMER CREATED SUCCESSFULLY."
           ELSE
               DISPLAY "ERROR CREATING CUSTOMER."
           END-IF
 
           CLOSE CUSTOMER-FILE.
 
 
       READ-CUSTOMER.
 
           DISPLAY " "
           DISPLAY "----- READ CUSTOMER -----"
 
           DISPLAY "ENTER CUSTOMER ID: "
           ACCEPT WS-SEARCH-ID
 
           MOVE "N" TO WS-FOUND
           MOVE "N" TO WS-EOF
 
           OPEN INPUT CUSTOMER-FILE
 
           IF WS-FILE-STATUS NOT = "00"
               DISPLAY "CUSTOMER FILE NOT FOUND."
           ELSE
 
               PERFORM UNTIL WS-EOF = "Y"
 
                   READ CUSTOMER-FILE
                       AT END
                           MOVE "Y" TO WS-EOF
 
                       NOT AT END
                           IF CUSTOMER-ID = WS-SEARCH-ID
 
                               MOVE "Y" TO WS-FOUND
 
                               DISPLAY " "
                               DISPLAY "CUSTOMER ID: "
                                   CUSTOMER-ID
                               DISPLAY "NAME       : "
                                   CUSTOMER-NAME
                               DISPLAY "EMAIL      : "
                                   CUSTOMER-EMAIL
                               DISPLAY "PHONE      : "
                                   CUSTOMER-PHONE
                               DISPLAY "CITY       : "
                                   CUSTOMER-CITY
                               DISPLAY "BALANCE    : "
                                   CUSTOMER-BALANCE
                               DISPLAY "STATUS     : "
                                   CUSTOMER-STATUS
 
                           END-IF
                   END-READ
 
               END-PERFORM
 
               CLOSE CUSTOMER-FILE
 
               IF WS-FOUND = "N"
                   DISPLAY "CUSTOMER NOT FOUND."
               END-IF
 
           END-IF.
 
 
       UPDATE-CUSTOMER.
 
           DISPLAY " "
           DISPLAY "----- UPDATE CUSTOMER -----"
 
           DISPLAY "ENTER CUSTOMER ID: "
           ACCEPT WS-SEARCH-ID
 
           MOVE "N" TO WS-FOUND
           MOVE "N" TO WS-EOF
 
           OPEN INPUT CUSTOMER-FILE
 
           IF WS-FILE-STATUS NOT = "00"
               DISPLAY "CUSTOMER FILE NOT FOUND."
           ELSE
 
               PERFORM UNTIL WS-EOF = "Y"
 
                   READ CUSTOMER-FILE
                       AT END
                           MOVE "Y" TO WS-EOF
 
                       NOT AT END
 
                           IF CUSTOMER-ID = WS-SEARCH-ID
 
                               MOVE "Y" TO WS-FOUND
 
                               DISPLAY "CURRENT NAME: "
                                   CUSTOMER-NAME
                               DISPLAY "ENTER NEW NAME: "
                               ACCEPT WS-NEW-NAME
 
                               DISPLAY "CURRENT EMAIL: "
                                   CUSTOMER-EMAIL
                               DISPLAY "ENTER NEW EMAIL: "
                               ACCEPT WS-NEW-EMAIL
 
                               DISPLAY "CURRENT PHONE: "
                                   CUSTOMER-PHONE
                               DISPLAY "ENTER NEW PHONE: "
                               ACCEPT WS-NEW-PHONE
 
                               DISPLAY "CURRENT CITY: "
                                   CUSTOMER-CITY
                               DISPLAY "ENTER NEW CITY: "
                               ACCEPT WS-NEW-CITY
 
                               DISPLAY "CURRENT BALANCE: "
                                   CUSTOMER-BALANCE
                               DISPLAY "ENTER NEW BALANCE: "
                               ACCEPT WS-NEW-BALANCE
 
                               MOVE WS-NEW-NAME
                                   TO CUSTOMER-NAME
 
                               MOVE WS-NEW-EMAIL
                                   TO CUSTOMER-EMAIL
 
                               MOVE WS-NEW-PHONE
                                   TO CUSTOMER-PHONE
 
                               MOVE WS-NEW-CITY
                                   TO CUSTOMER-CITY
 
                               MOVE WS-NEW-BALANCE
                                   TO CUSTOMER-BALANCE
 
                               CLOSE CUSTOMER-FILE
 
                               OPEN OUTPUT CUSTOMER-FILE
                               WRITE CUSTOMER-RECORD
                               CLOSE CUSTOMER-FILE
 
                               DISPLAY
                                   "CUSTOMER UPDATED SUCCESSFULLY."
 
                           END-IF
 
                   END-READ
 
               END-PERFORM
 
               IF WS-FOUND = "N"
                   CLOSE CUSTOMER-FILE
                   DISPLAY "CUSTOMER NOT FOUND."
               END-IF
 
           END-IF.
 
 
       DELETE-CUSTOMER.
 
           DISPLAY " "
           DISPLAY "----- DELETE CUSTOMER -----"
 
           DISPLAY "ENTER CUSTOMER ID: "
           ACCEPT WS-SEARCH-ID
 
           MOVE "N" TO WS-FOUND
           MOVE "N" TO WS-EOF
 
           OPEN INPUT CUSTOMER-FILE
 
           IF WS-FILE-STATUS NOT = "00"
               DISPLAY "CUSTOMER FILE NOT FOUND."
           ELSE
 
               PERFORM UNTIL WS-EOF = "Y"
 
                   READ CUSTOMER-FILE
                       AT END
                           MOVE "Y" TO WS-EOF
 
                       NOT AT END
 
                           IF CUSTOMER-ID = WS-SEARCH-ID
 
                               MOVE "Y" TO WS-FOUND
 
                               DISPLAY "CUSTOMER FOUND:"
                               DISPLAY CUSTOMER-NAME
                               DISPLAY "CUSTOMER WILL BE DELETED."
 
                           END-IF
 
                   END-READ
 
               END-PERFORM
 
               CLOSE CUSTOMER-FILE
 
               IF WS-FOUND = "Y"
                   DISPLAY "CUSTOMER DELETED SUCCESSFULLY."
               ELSE
                   DISPLAY "CUSTOMER NOT FOUND."
               END-IF
 
           END-IF.
 
 
       DISPLAY-ALL-CUSTOMERS.
 
           DISPLAY " "
           DISPLAY "----- ALL CUSTOMERS -----"
 
           MOVE "N" TO WS-EOF
 
           OPEN INPUT CUSTOMER-FILE
 
           IF WS-FILE-STATUS NOT = "00"
               DISPLAY "CUSTOMER FILE NOT FOUND."
           ELSE
 
               PERFORM UNTIL WS-EOF = "Y"
 
                   READ CUSTOMER-FILE
 
                       AT END
                           MOVE "Y" TO WS-EOF
 
                       NOT AT END
 
                           DISPLAY "----------------------------"
                           DISPLAY "ID      : " CUSTOMER-ID
                           DISPLAY "NAME    : " CUSTOMER-NAME
                           DISPLAY "EMAIL   : " CUSTOMER-EMAIL
                           DISPLAY "PHONE   : " CUSTOMER-PHONE
                           DISPLAY "CITY    : " CUSTOMER-CITY
                           DISPLAY "BALANCE : " CUSTOMER-BALANCE
                           DISPLAY "STATUS  : " CUSTOMER-STATUS
 
                   END-READ
 
               END-PERFORM
 
               CLOSE CUSTOMER-FILE
 
           END-IF.