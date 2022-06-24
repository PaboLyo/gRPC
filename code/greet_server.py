from concurrent import futures
import os
import sys
import time
from turtle import update
import grpc
import greet_pb2
import greet_pb2_grpc
import datetime


class GreeterServicer(greet_pb2_grpc.GreeterServicer):

    def __init__(self):
        self.exposureDict = {}

    def CheckIn(self, request, context):
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

    def CheckOut(self, request, context):
        print("Check Out Details:")
        print(request)
        tempfile = 'temp.txt'
        currentfile = 'safeentry.txt'

        f = open(tempfile, "a")
        with open(currentfile) as fp:
            for line in fp:
                if (line.split(",")[0].strip().casefold() == request.nric.casefold() and line.split(",")[
                    3].strip().casefold() == "checkoutDT".casefold() and line.split(",")[4].strip().casefold() == "-"):
                    updatedLine = line.split(",")[0].strip() + ", " + line.split(",")[1].strip() + ", " + \
                                  line.split(",")[2].strip() + ", " + request.date + ", " + line.split(",")[4].strip()
                    f.write(updatedLine)
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

    def DeleteGroup(self, request, context):
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

    def CheckInGroup(self, request, context):
        print("Group Check In Details:")
        print(request)
        currentfile = "group/" + request.nric + "_Group.txt"
        print(currentfile)
        print(request.nric)

        if os.path.exists(currentfile):
            f = open("safeentry.txt", "a")
            with open(currentfile) as fp:
                for line in fp:
                    f.write("\n")
                    checkInGroupMessage = line.strip() + ", " + request.date + ", " + request.location
                    print(checkInGroupMessage)
                    f.write(checkInGroupMessage + ", checkoutDT, " + request.nric + "_Group")

            f.close()
        else:
            checkInGroupMessage = "NRIC Group does not exists!"

        check_in_group_reply = greet_pb2.CheckResponse()
        check_in_group_reply.message = checkInGroupMessage
        return check_in_group_reply

    def CheckOutGroup(self, request, context):
        print("Group Check Out Details:")
        print(request)
        tempfile = 'temp.txt'
        currentfile = 'safeentry.txt'
        nricfile = "group/" + request.nric + "_Group.txt"

        if os.path.exists(nricfile):
            f = open(tempfile, "a")
            with open(nricfile) as nr, open(currentfile) as fp:
                for nricline in nr:
                    for line in fp:
                        if not line.isspace():
                            if (line.split(",")[3].strip() == "checkoutDT" and line.split(",")[
                                4].strip() == nricline.strip() + "_Group"):
                                updatedLine = line.split(",")[0].strip() + ", " + line.split(",")[1].strip() + ", " + \
                                            line.split(",")[2].strip() + ", " + request.date + ", " + line.split(",")[
                                                4].strip()
                                print(updatedLine)
                                f.write(updatedLine + "\n")
                            else:
                                f.write(line)

            f.close()
            os.remove(currentfile)
            os.rename(tempfile, currentfile)
            checkOutGroupMessage = request.nric + " Group CheckOut completed!"
        else:
            checkOutGroupMessage = "NRIC Group does not exists!"

        check_out_group_reply = greet_pb2.CheckResponse()
        check_out_group_reply.message = checkOutGroupMessage
        return check_out_group_reply

    def determine_period(self, location, timeIN, timeOut, patientLocation, patientTimeIn, patientTimeOut, NRIC):
        key = patientLocation + ":" + datetime.datetime.strftime(patientTimeIn, "%Y-%m-%d %H:%M:%S")
        if location == patientLocation:
            if timeOut is not None:
                # print("the max of {} and {} is {}".format(timeIN, patientTimeIn, max(timeIN, patientTimeIn)))
                latestStart = max(timeIN, patientTimeIn)
                # print("latest start is {}".format(max(timeIN, patientTimeIn)))
                earliestEnd = min(timeOut, patientTimeOut)
                # print("earliest end is {}".format(min(timeOut, patientTimeOut)))
                delta = earliestEnd - latestStart
                # print(delta)
                if delta >= datetime.timedelta(hours=0, minutes=0, seconds=0):
                    # print("POTENTIAL EXPOSURE")
                    self.exposureDict.setdefault(key, set()).add(NRIC)
            elif patientTimeIn <= timeIN <= patientTimeOut:
                # print("POTENTIAL EXPOSURE")
                self.exposureDict.setdefault(key, set()).add(NRIC)

    def DeclareLocation(self, request, context):
        print("Declare a location visited by covid patient:")
        print(request)
        visitLocation = request.location
        visitInDateTime = datetime.datetime.strptime(request.datein, "%Y-%m-%d %H:%M:%S")
        visitOutDateTime = datetime.datetime.strptime(request.dateout, "%Y-%m-%d %H:%M:%S")
        # nricfile = "group/" + request.nric + "_Group.txt"

        with open("safeentry.txt") as infile:
            for line in infile:
                print(line)
                lineList = line.split(",")
                ic = lineList[0]
                inTimeString = lineList[1]
                location = lineList[2]
                outTimeString = lineList[3]
                inDate = datetime.datetime.strptime(inTimeString, " %Y-%m-%d %H:%M:%S")
                if lineList[3] != " checkoutDT":
                    outDate = datetime.datetime.strptime(outTimeString, " %Y-%m-%d %H:%M:%S")
                else:
                    outDate = None
                self.determine_period(location, inDate, outDate, visitLocation, visitInDateTime, visitOutDateTime, ic)
            infile.close()
        print("Possible Exposure:")
        print(self.exposureDict)
        reply = greet_pb2.CheckResponse()
        reply.message = "success"
        return reply

    def ExposurePoll(self, request, context):
        message = ""
        nric = request.nric
        for k, v in self.exposureDict.items():
            if nric in v:
                self.exposureDict[k].remove(nric)
                message += k
                if len(v) == 0:
                    self.exposureDict.pop(k)
        reply = greet_pb2.CheckResponse()
        reply.message = message
        return reply


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greet_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
    server.add_insecure_port("localhost:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
