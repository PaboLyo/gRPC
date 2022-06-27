import os
# from tabnanny import check
import greet_pb2_grpc
import greet_pb2
import time
import grpc
from datetime import datetime
import threading



def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = greet_pb2_grpc.GreeterStub(channel)
        print("----- SafeEntry -----")
        print("1. Users ")
        print("2. Staffs ")
        print("3. Exit ")
        mmInput = input("Enter an input: ")
        while mmInput == "":
            mmInput = input("Enter a valid input: ")

        if mmInput == "1":
            print("-----------------------")
            nric_call = input("Enter NRIC: ")
            print("-----------------------")
            threading.Thread(target=checkExposure, args=(stub, nric_call,)).start()
            UsersMode(stub, nric_call)

        elif mmInput == "2":
            StaffsMode(stub)

        elif mmInput == "3":
            exit()

# Users Main Menu
def UsersMode(stub, nric_call):
    today = datetime.now()
    today = today.strftime("%Y-%m-%d %H:%M:%S")
    print("Current Time: " + today)  # '2018-12-05 22:13:25'
    print("-----------------------")
    print("1. User Check IN")
    print("2. User Check OUT")
    print("3. Group Check IN")
    print("4. Group Check OUT")
    print("5. Manage Group Info")
    print("6. View All Records")
    rpc_call = input("Which rpc would you like to make: ")
    print("-----------------------")
    # Calls the checkIn stub (Individual)
    if rpc_call == "1":
        checkIn(stub, nric_call)

    # Calls the checkOut stub (Individual)
    elif rpc_call == "2":
        checkOut(stub, nric_call)

    # Calls the checkIn stub (Group)
    elif rpc_call == "3":
        checkInGroup(stub, nric_call)

    # Calls the checkOut stub (Group)
    elif rpc_call == "4":
        checkOutGroup(stub, nric_call)

    # Calls the manageGroupInfo stub (Manages the group settings)
    elif rpc_call == "5":
        manageGroupInfo(stub, nric_call)

    # Calls the viewAllRecords which calls up all the saved history based on the NRIC
    elif rpc_call == "6":
        viewAllRecords(stub, nric_call)

# Staff Main Menu
def StaffsMode(stub):
    # location = input("COVID visited location")
    # time = input("visit time")
    visitInTime = "2022-06-20 00:00:00"
    visitOutTime = "2022-07-01 00:00:00"
    visitLocation = " Testing"
    locationRequest = greet_pb2.LocationDetails(datein=visitInTime, dateout=visitOutTime, location=visitLocation)
    reply = stub.DeclareLocation(locationRequest)
    print("Possible Exposure:")
    print(reply)
    # Insert Staff UI which is just adding infected location and date

# User CheckIN (Solo)
def checkIn(stub, nric_call):
    # Gets Input Location
    print("Enter check-in location:")
    destination = input("")
    while destination == "":
        destination = input("Please enter a valid location: ")
    today = datetime.now()
    today = today.strftime("%Y-%m-%d %H:%M:%S")
    # Sends a request to the server to write to the database (txt file)
    check_in_request = greet_pb2.CheckInRequest(nric=nric_call, date=today, location=destination)
    check_in_reply = stub.CheckIn(check_in_request)
    print("CheckIn Data Received:")
    print(check_in_reply)
    # Checks if the user wants to return to the main menu
    checkExit = input("Enter 'Y' to return to main menu: ")
    while checkExit == "":
        checkExit = input("Please enter a valid input: ")
    if checkExit.upper() == "Y":
        UsersMode(stub, nric_call)

# User CheckOUT (Solo)
def checkOut(stub, nric_call):
    today = datetime.now()
    today = today.strftime("%Y-%m-%d %H:%M:%S")
    # Sends a request to the server to write to the database (txt file)
    check_out_request = greet_pb2.CheckOutRequest(nric=nric_call, date=today)
    check_out_reply = stub.CheckOut(check_out_request)
    print("CheckOut Data Received:")
    print(check_out_reply)
    # Checks if the user wants to return to the main menu
    checkExit = input("Enter 'Y' to return to main menu: ")
    while checkExit == "":
        checkExit = input("Please enter a valid input: ")
    if checkExit.upper() == "Y":
        UsersMode(stub, nric_call)

# User CheckIN (Group)
def checkInGroup(stub, nric_call):
    # Gets Input Location (Group)
    print("Enter check-in location (Group):")
    destination = input("")
    while destination == "":
        destination = input("Please enter a valid location: ")
    today = datetime.now()
    today = today.strftime("%Y-%m-%d %H:%M:%S")
    # Sends a request to the server to write to the database (txt file)
    check_in_group_request = greet_pb2.CheckInGroupRequest(nric=nric_call, date=today, location=destination)
    check_in_group_reply = stub.CheckInGroup(check_in_group_request)
    print("Group CheckIn Data Received:")
    print(check_in_group_reply)
    # Checks if the user wants to return to the main menu
    checkExit = input("Enter 'Y' to return to main menu: ")
    while checkExit == "":
        checkExit = input("Please enter a valid input: ")
    if checkExit.upper() == "Y":
        UsersMode(stub, nric_call)

# User CheckOUT (Group)
def checkOutGroup(stub, nric_call):
    today = datetime.now()
    today = today.strftime("%Y-%m-%d %H:%M:%S")
    # Sends a request to the server to write to the database (txt file)
    check_out_group_request = greet_pb2.CheckOutGroupRequest(nric=nric_call, date=today)
    check_out_group_reply = stub.CheckOutGroup(check_out_group_request)
    print("Group CheckOut Data Received:")
    print(check_out_group_reply)
    # Checks if the user wants to return to the main menu
    checkExit = input("Enter 'Y' to return to main menu: ")
    while checkExit == "":
        checkExit = input("Please enter a valid input: ")
    if checkExit.upper() == "Y":
        UsersMode(stub, nric_call)

# Manage Group Info
def manageGroupInfo(stub, nric_call):
    print("------- Manage SafeEntry Group -------")
    print("1. Add people into group")
    print("2. View group members")
    print("3. Delete Group")
    print("4. Back to User Screen")
    gpInput = input("Enter the option: ")
    # Adds a new group and insert names into it
    if gpInput == "1":
        groupName = "group/" + nric_call + "_Group.txt"
        with open(groupName, "a+") as f:
            if not nric_call in f.read():
                f.write(nric_call + "\n")
        f.close()

        responses = stub.AddGroup(add_group_info(stub, nric_call))

        for response in responses:
            print("AddGroup Response Received: ")
            print(response)
    # View all the group members
    elif gpInput == "2":
        viewGroupRecords(stub, nric_call)
    # Delete the group records
    elif gpInput == "3":
        deleteGroupRecords(stub, nric_call)
    # Back to User Main Menu
    elif gpInput == "4":
        UsersMode(stub, nric_call)
    # Exit the program
    else:
        exit()

# Add Group Members. Process name if users enters an input. Else it will exit to menu
def add_group_info(stub, nric_call):
    while True:
        nric_input = input("Please enter a NRIC to be added into group (or nothing to stop chatting): ")

        if nric_input == "":
            break

        addgroup_request = greet_pb2.AddGroupRequest(nric=nric_call, nricMember=nric_input)
        yield addgroup_request
        time.sleep(1)
    # Checks if the user wants to return to the main menu
    checkExit = input("Enter 'Y' to return to main menu: ")
    while checkExit == "":
        checkExit = input("Please enter a valid input: ")
    if checkExit.upper() == "Y":
        UsersMode(stub, nric_call)

# View Group Members
def viewGroupRecords(stub, nric_call):
    groupName = "group/" + nric_call + "_Group.txt"
    if os.path.exists(groupName):
        with open(groupName) as fp:
            print("------ SafeEntry Group Members -----")
            print("| NRIC |")
            for line in fp:
                print(line)
    else:
        print("No group records found on the user")
    # Checks if the user wants to return to the main menu
    checkExit = input("Enter 'Y' to return to main menu: ")
    if checkExit.upper() == "Y":
        UsersMode(stub, nric_call)

# Delete Group Records
def deleteGroupRecords(stub, nric_call):
    # Sends request to the server to delete the group records
    delete_group_request = greet_pb2.DeleteGroupRequest(nric=nric_call)
    delete_group_reply = stub.DeleteGroup(delete_group_request)

    print("CheckOut Data Received:")
    print(delete_group_reply)
    # Checks if the user wants to return to the main menu
    checkExit = input("Enter 'Y' to return to main menu: ")
    while checkExit == "":
        checkExit = input("Please enter a valid input: ")
    if checkExit.upper() == "Y":
        UsersMode(stub, nric_call)

# View all checkIns and checkOuts for the user (NRIC)
def viewAllRecords(stub, nric_call):
    with open('safeentry.txt') as fp:
        print("------ SafeEntry History -----")
        print("| NRIC | CheckIn DateTime | Location | Checkout DateTime | Group |")
        for line in fp:
            if (line.split(",")[0].strip().casefold() == nric_call.casefold()):
                print(line.split(",")[0].strip() + ", " + line.split(",")[1].strip() + ", " + line.split(",")[
                    2].strip() + ", " + line.split(",")[3].strip() + ", " + line.split(",")[4].strip())

    checkExit = input("Enter 'Y' to return to main menu: ")
    if checkExit.upper() == "Y":
        UsersMode(stub, nric_call)


def checkExposure(stub, nric_call):
    while True:
        pollRequest = greet_pb2.NRIC(nric=nric_call)
        pollReply = stub.ExposurePoll(pollRequest)
        if pollReply.message != "":
            print("\nALERT, YOU HAVE POTENTIALLY BEEN EXPOSED AT THE FOLLOWING INSTANCE(S):")
            print(pollReply.message)
            print("\n")
        time.sleep(5)

if __name__ == "__main__":
    run()
