from concurrent import futures
import os
import time

import grpc
import greet_pb2
import greet_pb2_grpc

class GreeterServicer(greet_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        print("SayHello Request Made:")
        print(request)
        hello_reply = greet_pb2.HelloReply()
        hello_reply.message = f"{request.greeting} {request.name}"

        return hello_reply
    
    def ParrotSaysHello(self, request, context):
        print("ParrotSaysHello Request Made:")
        print(request)

        for i in range(3):
            hello_reply = greet_pb2.HelloReply()
            hello_reply.message = f"{request.greeting} {request.name} {i + 1}"
            yield hello_reply
            time.sleep(3)

    def ChattyClientSaysHello(self, request_iterator, context):
        delayed_reply = greet_pb2.DelayedReply()
        for request in request_iterator:
            print("ChattyClientSaysHello Request Made:")
            print(request)
            delayed_reply.request.append(request)

        delayed_reply.message = f"You have sent {len(delayed_reply.request)} messages. Please expect a delayed response."
        return delayed_reply

    def InteractingHello(self, request_iterator, context):
        for request in request_iterator:
            print("InteractingHello Request Made:")
            print(request)

            hello_reply = greet_pb2.HelloReply()
            hello_reply.message = f"{request.greeting} {request.name}"

            yield hello_reply

    def CheckIn (self, request, context):
        print("Check In Details:")
        print(request)
        checkInMessage = request.nric + ", " + request.date + ", " + request.location
        
        f = open("safeentry.txt", "a")
        f.write("\n")
        f.write(checkInMessage + ", checkoutDT, -")
        f.close()
        
        check_in_reply = greet_pb2.CheckResponse()
        check_in_reply.message = checkInMessage
        return check_in_reply

    def CheckOut (self, request, context):
        print("Check Out Details:")
        print(request)
        tempfile = 'temp.txt'
        currentfile = 'safeentry.txt'

        f = open(tempfile, "a")
        with open(currentfile) as fp:
            for line in fp:
                if (line.split(",")[0].strip().casefold() == request.nric.casefold() and line.split(",")[3].strip().casefold() == "checkoutDT".casefold() and line.split(",")[4].strip().casefold() == "-"):
                    updatedLine = line.split(",")[0].strip() + ", " + line.split(",")[1].strip() + ", " + line.split(",")[2].strip() + ", " + request.date + ", " + line.split(",")[4].strip()
                    f.write(updatedLine + "\n")
                else:
                    f.write(line)
        f.close()
        os.remove(currentfile)
        os.rename(tempfile, currentfile)
    

        checkOutMessage = request.nric + " checked out successfully!"
        
        check_out_reply = greet_pb2.CheckResponse()
        check_out_reply.message = checkOutMessage
        return check_out_reply
    
    def AddGroup(self, request_iterator, context):
        for request in request_iterator:
            print("AddGroup Request Made:")
            print(request)
            currentfile = "group/" + request.nric + "_Group.txt"

            with open(currentfile, "a+") as fp:
                updateline = request.nricMember
                print(updateline)
                if request.nricMember in fp.read():
                    add_group_reply = greet_pb2.CheckResponse()
                    add_group_reply.message = request.nricMember + " is already in the group!"

                else:
                    fp.write(updateline + "\n")
                    add_group_reply = greet_pb2.CheckResponse()
                    add_group_reply.message = request.nricMember + " has been added into the group!"

            fp.close()

            yield add_group_reply

    def DeleteGroup (self, request, context):
        print("Check In Details:")
        print(request)
        currentfile = "group/" + request.nric + "_Group.txt"
        print(currentfile)
        print(request.nric)
        if os.path.exists(currentfile):
            os.remove(currentfile)
            deleteGroupMessage = request.nric + " group has been deleted"
        else:
            deleteGroupMessage = "file does not exists!"
        
        
        delete_group_reply = greet_pb2.CheckResponse()
        delete_group_reply.message = deleteGroupMessage
        return delete_group_reply

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greet_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
    server.add_insecure_port("localhost:50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
