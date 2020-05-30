import requests
from orionsdk import SwisClient
import json
import time

requests.packages.urllib3.disable_warnings()




class Solarwinds_Interface():
    def __init__(self, name):
        """
        In Solarwinds, Interfaces of devices are represented with name and id, but primary variable and unique identifier is id
        """
        self.name = name
        self.interfaceID = ""
        self.interfaceTraffic = {}
        self.tempJson = {}
        self.adminState = 0
        self.operationalState = 0
        
class Solarwinds_Node():
    def __init__(self, nodeIP):
        """
        In Solarwinds, Devices are represented with ip and id, but primary variable and unique identifier is id
        """
        self.managementIP = nodeIP
        self.monitoredInterfaces = []
        self.nodeID = ""
        #If a device has not any configuration in your Solarwinds, this variable is 'False' again
        self.existence = False


class Solar():
    def __init__(self, npm_server, username, password):
        """
        This class mainly aims to represent information in your Solarwinds with consuming abilities of Orion sdk
        """
        #Creating an instance for Your solarwinds
        self.swis = SwisClient(npm_server, username, password)

    def getInterfacesByIp(self, nodeIP):
        """
        This function get information of device in Solarwinds with ip parameter,
        For doing this, It get if of node, if it exists,
        If device exist in Solarwinds, It finds interfaces of it, and return this Solarwinds_Node with interface information and set 'True' to existence.existence variable
        """
        #Creating a temporary Solarwinds node to collect information with proper  
        tempNode = Solarwinds_Node(nodeIP)
        stepNumber = 0
        try:
            #Step 1 is performed for taking ID information of device with ip address given as parameter to this function, if device exists in Solarwinds
            print("Step 1 for " + nodeIP )
            nodeIDGetter = self.swis.query("SELECT n.NodeID FROM Orion.Nodes n WHERE n.IPAddress = '" + nodeIP+ "'")
            print("NodeID of " + nodeIP + " is " + str(nodeIDGetter['results'][0]['NodeID']))
            #If the above line doesn't throw an error, next line says that there is a device this ip in Solarwinds
            tempNode.existence = True
            #And step 1 is completed
            stepNumber = 1
            #In step 2, interfaces of device are searched with device Solarwinds id
            print("Step 2 for " + nodeIP )
            queryForInterfaces = self.swis.query("SELECT I.InterfaceID, I.Name, I.AdminStatus, I.OperStatus, I.Status FROM Orion.NPM.Interfaces I WHERE I.NodeID=" + str(nodeIDGetter['results'][0]['NodeID']))
            tempNode.nodeID = str(nodeIDGetter['results'][0]['NodeID'])
            #print(queryForInterfaces)
            for interfaceInfo in queryForInterfaces['results']:
                tempInterface = Solarwinds_Interface(interfaceInfo['Name'])
                tempInterface.interfaceID = interfaceInfo['InterfaceID']
                if interfaceInfo['Status'] == 1:
                    tempInterface.adminState = 'up'
                    tempInterface.operationalState = 'up'
                else:
                    tempInterface.adminState = 'down'
                    tempInterface.operationalState = 'down'

                tempNode.monitoredInterfaces.append(tempInterface)
        except Exception,e:
            print("Failed process for " + nodeIP + " on step of " + str(stepNumber))
            print(str(e))
        finally:
            print("Done for " + nodeIP)
            return tempNode

    

        
        
    
