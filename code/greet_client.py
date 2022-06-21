import os
from tabnanny import check
import greet_pb2_grpc
import greet_pb2
import time
import grpc
from datetime import datetime

def get_client_stream_requests():
    while True:
        name = input("Please enter a name (or nothing to stop chatting): ")

        if name == "":
            break

        hello_request = greet_pb2.HelloRequest(greeting = "Hello", name = name)
        yield hello_request
        time.sleep(1)

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
            UsersMode(stub, nric_call)

        elif mmInput == "2":
            StaffsMode(stub)

        elif mmInput == "3":
            exit()

           
def UsersMode(stub, nric_call):
        today = datetime.now()
        today = today.strftime("%Y-%m-%d %H:%M:%S")
        print("Current Time: " + today)  # '2018-12-05 22:13:25'
        print("-----------------------")
        print("1. SayHello - Unary")
        print("2. ParrotSaysHello - Server Side Streaming")
        print("3. ChattyClientSaysHello - Client Side Streaming")
        print("4. InteractingHello - Both Streaming")
        print("5. User Check IN")
        print("6. User Check OUT")
        print("7. Group Check IN")
        print("8. Group Check OUT")
        print("9. Manage Group Info")
        print("10. View All Records")
        rpc_call = input("Which rpc would you like to make: ")
        print("-----------------------")
        if rpc_call == "1":
            hello_request = greet_pb2.HelloRequest(greeting = "Bonjour", name = nric_call)
            hello_reply = stub.SayHello(hello_request)
            print("SayHello Response Received:")
            print(hello_reply)

        elif rpc_call == "2":
            hello_request = greet_pb2.HelloRequest(greeting = "Bonjour", name = "YouTube")
            hello_replies = stub.ParrotSaysHello(hello_request)

            for hello_reply in hello_replies:
                print("ParrotSaysHello Response Received:")
                print(hello_reply)
        elif rpc_call == "3":
            delayed_reply = stub.ChattyClientSaysHello(get_client_stream_requests())

            print("ChattyClientSaysHello Response Received:")
            print(delayed_reply)
        elif rpc_call == "4":
            responses = stub.InteractingHello(get_client_stream_requests())

            for response in responses:
                print("InteractingHello Response Received: ")
                print(response)
        
        # Calls the checkIn stub (Individual)
        elif rpc_call == "5":
            checkIn(stub, nric_call)
        
        # Calls the checkOut stub (Individual)
        elif rpc_call == "6":
            checkOut(stub, nric_call)

        # Calls the checkIn stub (Group)
        elif rpc_call == "7":
            checkInGroup(stub, nric_call)
        
        # Calls the checkOut stub (Group)
        elif rpc_call == "8":
            checkOutGroup(stub, nric_call)
        
        # Calls the manageGroupInfo stub (Manages the group settings)
        elif rpc_call == "9":
            manageGroupInfo(stub, nric_call)

        # Calls the viewAllRecords which calls up all the saved history based on the NRIC    
        elif rpc_call == "10":
            viewAllRecords(stub, nric_call)

def StaffsMode(stub):
    pass
    # Insert Staff UI which is just adding infected location and date

def checkIn(stub, nric_call):
    print("Enter check-in location:")
    destination = input("")
    while destination == "":
        destination = input("Please enter a valid location: ")
    today = datetime.now()
    today = today.strftime("%Y-%m-%d %H:%M:%S")
    
    check_in_request = greet_pb2.CheckInRequest(nric = nric_call, date = today, location= destination)
    check_in_reply = stub.CheckIn(check_in_request)
    print("CheckIn Data Received:")
    print(check_in_reply)
    checkExit = input ("Enter 'Y' to return to main menu: ")
    while checkExit == "":
        checkExit = input("Please enter a valid input: ")
    if checkExit.upper() == "Y":
        UsersMode(stub, nric_call)

def checkOut(stub, nric_call):
    today = datetime.now()
    today = today.strftime("%Y-%m-%d %H:%M:%S")
    
    check_out_request = greet_pb2.CheckOutRequest(nric = nric_call, date = today)
    check_out_reply = stub.CheckOut(check_out_request)
    print("CheckOut Data Received:")
    print(check_out_reply)
    checkExit = input ("Enter 'Y' to return to main menu: ")
    while checkExit == "":
        checkExit = input("Please enter a valid input: ")
    if checkExit.upper() == "Y":
        UsersMode(stub, nric_call)


def checkInGroup(stub, nric_call):
    print("Enter check-in location (Group):")
    destination = input("")
    while destination == "":
        destination = input("Please enter a valid location: ")
    today = datetime.now()
    today = today.strftime("%Y-%m-%d %H:%M:%S")
    
    check_in_group_request = greet_pb2.CheckInGroupRequest(nric = nric_call, date = today, location= destination)
    check_in_group_reply = stub.CheckInGroup(check_in_group_request)
    print("Group CheckIn Data Received:")
    print(check_in_group_reply)
    checkExit = input ("Enter 'Y' to return to main menu: ")
    while checkExit == "":
        checkExit = input("Please enter a valid input: ")
    if checkExit.upper() == "Y":
        UsersMode(stub, nric_call)

def checkOutGroup(stub, nric_call):
    today = datetime.now()
    today = today.strftime("%Y-%m-%d %H:%M:%S")
    
    check_out_group_request = greet_pb2.CheckOutGroupRequest(nric = nric_call, date = today)
    check_ou_group_reply = stub.CheckOutGroup(check_out_group_request)
    print("Group CheckOut Data Received:")
    print(check_ou_group_reply)
    checkExit = input ("Enter 'Y' to return to main menu: ")
    while checkExit == "":
        checkExit = input("Please enter a valid input: ")
    if checkExit.upper() == "Y":
        UsersMode(stub, nric_call)

def manageGroupInfo(stub, nric_call):
    print("------- Manage SafeEntry Group -------")
    print("1. Add people into group")
    print("2. View group members")
    print("3. Delete Group")
    print("4. Back to User Screen")
    gpInput = input("Enter the option: ")

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

    elif gpInput == "2":
        viewGroupRecords(stub, nric_call)

    elif gpInput == "3":
        deleteGroupRecords(stub, nric_call)

    elif gpInput == "4":
        UsersMode(stub, nric_call)

    else:
        exit()

def add_group_info(stub, nric_call):
    while True:
        nric_input = input("Please enter a NRIC to be added into group (or nothing to stop chatting): ")

        if nric_input == "":
            break

        addgroup_request = greet_pb2.AddGroupRequest(nric = nric_call, nricMember = nric_input)
        yield addgroup_request
        time.sleep(1)

    checkExit = input ("Enter 'Y' to return to main menu: ")
    while checkExit == "":
        checkExit = input("Please enter a valid input: ")
    if checkExit.upper() == "Y":
        UsersMode(stub, nric_call)

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
    
    checkExit = input ("Enter 'Y' to return to main menu: ")
    if checkExit.upper() == "Y":
       UsersMode(stub, nric_call)

def deleteGroupRecords(stub, nric_call):
    delete_group_request = greet_pb2.DeleteGroupRequest(nric = nric_call)
    delete_group_reply = stub.DeleteGroup(delete_group_request)

    print("CheckOut Data Received:")
    print(delete_group_reply)
    checkExit = input ("Enter 'Y' to return to main menu: ")
    while checkExit == "":
        checkExit = input("Please enter a valid input: ")
    if checkExit.upper() == "Y":
        UsersMode(stub, nric_call)

def viewAllRecords(stub, nric_call):
    with open('safeentry.txt') as fp:
        print("------ SafeEntry History -----")
        print("| NRIC | CheckIn DateTime | Location | Checkout DateTime | Group |")
        for line in fp:
            if (line.split(",")[0].strip().casefold() == nric_call.casefold()):
                print(line.split(",")[0].strip() + ", " + line.split(",")[1].strip() + ", " + line.split(",")[2].strip() + ", " + line.split(",")[3].strip() + ", " + line.split(",")[4].strip())
    
    checkExit = input ("Enter 'Y' to return to main menu: ")
    if checkExit.upper() == "Y":
       UsersMode(stub, nric_call)

if __name__ == "__main__":
    run()