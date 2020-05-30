import sys
import time
import datetime
import requests
import json
import urllib3
import click
import solarWinderer

print("Libraries are imported")

urllib3.disable_warnings()

class Interface():
    def __init__(self, name):
        '''
        This class is representative of interfaces of dc switches
        '''
        self.name = name
        self.dn = ''
        self.adminState = ''
        self.operationalState = ''
        self.speed = ''
        self.sfpModel = 'unset'
        self.sfpSerial = 'unset'
        self.lastLinkStateChange = datetime.datetime(1970, 1, 1)
        self.deployedEPGs = []
        self.monitored = False
        self.mustBeMonitored = False
        self.solarStateFaulty = False


class Device():
    def __init__(self, name):
        '''
        This class is representative of pyhsical switches in Pod
        '''
        self.name = name
        self.serial = ''
        self.model = ''
        self.dn = ''
        self.oobmIpAddress = ''
        self.interfaces = []
        self.solarwindsNode = solarWinderer.Solarwinds_Node('')


class Pod():
    def __init__(self, name):
        '''
        This class is representative of a group of switches combined as a data centre pod
        '''
        self.name = name
        self.devices = []


class Apic:
    def __init__(self, managementIP, username, password, ip_solar, username_solar, password_solar):
        '''
        This class is representative of Cisco Aci sdn controller,
        Mainly; it holds authentication process, get and post data operations, and
        organizing obtained data with specific functions
        '''
        self.IP = managementIP
        self.username = username
        self.password = password

        self.cookies = {}
        self.headers = {
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        self.authentication = False
        self.pods = []
        self.solarwinds = solarWinderer.Solar(ip_solar,username_solar, password_solar)
    def login(self):
        try:
            AUTHENTICATION_URL = "https://%s/api/aaaLogin.json" % self.IP
            AUTHENTICATION_DATA = "{\"aaaUser\":{\"attributes\":{\"name\":\"%s\" , \"pwd\":\"%s\"}}}" % (
            self.username, self.password)
            auth = json.loads(requests.post(AUTHENTICATION_URL, AUTHENTICATION_DATA, self.headers, verify=False).text)
            auth_token = auth['imdata'][0]['aaaLogin']['attributes']['token']
            self.cookies['APIC-Cookie'] = auth_token
            print(auth_token)
            self.authentication = True
            print("You are authenticated to Apic on ", self.IP)
        except:
            e = sys.exc_info()[0]
            print("Token failed with exception: %s" % e)
        finally:
            print("Login process to Apic on %s is finished" % self.IP)

    def getData(self, URL):
        if self.authentication:
            Data = json.loads(requests.get(url=URL, cookies=self.cookies, verify=False).text)["imdata"]
            return Data
        else:
            return False

    def getPods(self):
        podsJson = self.getData("https://%s/api/node/class/fabricPod.json" % self.IP)
        if podsJson:
            #print(podsJson)
            for pod in podsJson:
                self.pods.append(Pod(pod['fabricPod']['attributes']['dn'].split('/')[1]))

    def getDevices(self):
        for pod in self.pods:
            devicesOfPodJson = self.getData("https://%s/api/node/mo/topology/%s.json?query-target=children&target-subtree-class=fabricNode" % (self.IP, pod.name))
            for fabricNode in devicesOfPodJson:
                tempDevice = Device(fabricNode['fabricNode']['attributes']['name'].replace('eth', 'Ethernet'))
                tempDevice.model = fabricNode['fabricNode']['attributes']['model']
                tempDevice.serial = fabricNode['fabricNode']['attributes']['serial']
                tempDevice.dn = fabricNode['fabricNode']['attributes']['dn']
                #Obtain device oobm management ip address
                deviceInfo = self.getData("https://%s/api/node/mo/%s.json?query-target=children&target-subtree-class=topSystem" % (self.IP, tempDevice.dn))
                if len(deviceInfo):
                    try:
                        tempDevice.oobmIpAddress = deviceInfo[0]['topSystem']['attributes']['oobMgmtAddr']
                    except:
                        pass
                    finally:
                        pass
                #Obtain physical interfaces of devices
                interfacesOfDeviceJson = self.getData("https://%s/api/node/class/%s/l1PhysIf.json?rsp-subtree=children&rsp-subtree-class=ethpmPhysIf" % (self.IP, tempDevice.dn))
                if interfacesOfDeviceJson:
                    print("Digging interfaces for " + tempDevice.name)
                    
                    for interface in interfacesOfDeviceJson:
                        tempInterface = Interface('')
                        try:
                            tempInterface = Interface(interface['l1PhysIf']['attributes']['id'].replace('eth','Ethernet'))
                            tempInterface.dn = interface['l1PhysIf']['attributes']['dn']
                            tempInterface.adminState = interface['l1PhysIf']['attributes']['adminSt']
                            tempInterface.operationalState = interface['l1PhysIf']['children'][0]['ethpmPhysIf']['attributes']['operSt']
                            timeSentence = interface['l1PhysIf']['children'][0]['ethpmPhysIf']['attributes']['lastLinkStChg']
                            tempInterface.lastLinkStateChange = datetime.date(int(timeSentence.split('T')[0].split('-')[0]), int(timeSentence.split('T')[0].split('-')[1]), int(timeSentence.split('T')[0].split('-')[2]))
                            tempInterface.speed = interface['l1PhysIf']['attributes']['speed']
                        except Exception as e:
                            pass
                        finally:
                            pass

                        #Getting deployed EPGs on interface
                        deployedEpgInfoOfInterface = self.getData("https://%s/api/node/mo/%s.json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg" % (self.IP, tempInterface.dn))
                        try:
                            for item in deployedEpgInfoOfInterface:
                                for child in item['l1PhysIf']['children'][0]['pconsCtrlrDeployCtx']['children']:
                                    #print(child['pconsResourceCtx']['attributes']['ctxDn'])
                                    tempInterface.deployedEPGs.append(child['pconsResourceCtx']['attributes']['ctxDn'])
                        except Exception as e:
                            pass
                        finally:
                            tempDevice.interfaces.append(tempInterface)
                        del tempInterface
                    
                #Obtain bundled interfaces of devices
                interfacesOfDeviceJson = self.getData('https://%s/api/node/class/%s/pcAggrIf.json?query-target-filter=not(wcard(polUni.dn, "__ui_"))&query-target=subtree&target-subtree-class=pcAggrIf,ethpmAggrIf' % (self.IP, tempDevice.dn))
                if interfacesOfDeviceJson:
                    for interface in interfacesOfDeviceJson:
                        try:
                            tempInterface = Interface(interface['pcAggrIf']['attributes']['id'].replace('po','port-channel'))
                            tempInterface.dn = interface['pcAggrIf']['attributes']['dn']
                            tempInterface.adminState = interface['pcAggrIf']['attributes']['adminSt']
                            tempDevice.interfaces.append(tempInterface)
                            del tempInterface
                        except Exception as e:
                            pass
                        finally:
                            pass
                    for port in tempDevice.interfaces:
                        for interface in interfacesOfDeviceJson:
                            try:
                                if port.dn in interface['ethpmAggrIf']['attributes']['dn']:
                                    port.operationalState = interface['ethpmAggrIf']['attributes']['operSt']
                                    timeSentence = interface['ethpmAggrIf']['attributes']['lastLinkStChg']
                                    port.lastLinkStateChange = datetime.date(int(timeSentence.split('T')[0].split('-')[0]), int(timeSentence.split('T')[0].split('-')[1]), int(timeSentence.split('T')[0].split('-')[2]))
                            except Exception as e:
                                pass
                            finally:
                                pass


                pod.devices.append(tempDevice)
                del tempDevice
    def getDataOnSolarwinds(self):
        for pod in self.pods:
            for device in pod.devices:
                if device.oobmIpAddress != '':
                    print('Getting solarwinds information of ' + device.name)
                    device.solarwindsNode = self.solarwinds.getInterfacesByIp(device.oobmIpAddress)
                else:
                    print(' %s  management port is not set with ip address or this code can not obtain this information' % (device.name))

    def getFabric(self):
        self.getPods()
        self.getDevices()
        self.getDataOnSolarwinds()





@click.group(invoke_without_command=True)
# user input ip address for ACI controller
@click.option("--ip_aci", help="Enter ip address or url of your ACI web screen")
# prompt user for input username to login ACI
@click.option("--username_aci", help="username when you use to log in your Aci", prompt=True)
# prompt user for input password to login ACI
@click.option("--password_aci", help="password when you use to log in your Aci", prompt=True)
# user input ip address for Solarwinds
@click.option("--ip_solar", help="Enter ip address or url of your Solarwinds web screen")
# prompt user for input username to login Solarwinds
@click.option("--username_solar", help="username when you use to log in your Solarwinds", prompt=True)
# prompt user for input password to login Solarwinds
@click.option("--password_solar", help="password when you use to log in your Solarwinds", prompt=True)

#mode of operation full means all of the sfp's, unused means unused sfps
@click.option("--mode", help="up: means that check monitoring state of up interfaces in fabric\nconfigured:\t means that check monitoring state of ports that have deployed epg or epg's", prompt=True)
@click.pass_context
def inputParser(ctx, ip_aci, username_aci, password_aci,ip_solar, username_solar, password_solar, mode):
    if mode == 'configured' or mode == 'up':
        # First, we get the starting time, in fact, there is no effect to take this,
        # but, I like to show what time process takes,
        startingTime = time.time()
        ACI_Fabric = Apic(ip_aci, username_aci, password_aci, ip_solar, username_solar, password_solar)
        ACI_Fabric.login()
        ACI_Fabric.getFabric()
        unmonitoredInterfaceCount = 0
        unmonitoredDeviceCount = 0
        solarStateFaultyInterfaceCount = 0
        managementIpAbsentDeviceCount = 0
        if mode == 'up':
            for pod in ACI_Fabric.pods:
                for device in pod.devices:
                    for interface in device.interfaces:
                        if interface.adminState == 'up' and interface.operationalState == 'up':
                            interface.mustBeMonitored = True
                    for interface in device.interfaces:
                        for monitored in device.solarwindsNode.monitoredInterfaces:
                            if interface.mustBeMonitored and interface.name == monitored.name:
                                interface.monitored = True
                                if interface.adminState != monitored.adminState or interface.operationalState != monitored.operationalState:
                                    interface.solarStateFaulty = True 

            print("Interface must be monitored in Solarwinds" + "*"*89)
            for pod in ACI_Fabric.pods:
                print("Pod name is " + pod.name)
                for device in pod.devices:
                    if device.oobmIpAddress != '':
                        if device.solarwindsNode.existence:
                            print("\tInterfaces have to be monitored in " + device.name + "(" + device.oobmIpAddress + ")")               
                            for interface in device.interfaces:
                                if interface.mustBeMonitored and not interface.monitored:
                                    if 'port-channel' in interface.name:
                                        print("\t\t" + interface.name + "\t" + interface.adminState + "\t" + interface.operationalState + "\t Last State Change: " + str(interface.lastLinkStateChange))
                                    else:
                                        print("\t\t" + interface.name + "\t" + interface.adminState + "\t" + interface.operationalState + "\t Last State Change: " + str(interface.lastLinkStateChange) + "\t Deployed epg:" + str(len(interface.deployedEPGs)))
                                    unmonitoredInterfaceCount += 1
                                if interface.solarStateFaulty:
                                    print("\t\t" + interface.name + "\t" + interface.adminState + "\t" + interface.operationalState + "\t Last State Change: " + str(interface.lastLinkStateChange) + "\t Deployed epg:" + str(len(interface.deployedEPGs)) + " solar state faulty")
                                    solarStateFaultyInterfaceCount += 1
                        else:
                            print("Device name: %s with oobm ip  %s is not configured in Solarwinds" % (device.name, device.oobmIpAddress))
                            unmonitoredDeviceCount += 1
                    else:
                        print("\t Management ip address of " + device.name + " can not be obtained")
                        managementIpAbsentDeviceCount += 1
            print("Result obtained from UP PORT MODE:\nYou have " + str(unmonitoredDeviceCount) + " unmonitored devices, \n "+str(unmonitoredInterfaceCount)+" unmonitored port and in ACI located on ip " + ACI_Fabric.IP)
            print("Count of device without obtained management ip address is " + str(managementIpAbsentDeviceCount))
            print("Solar state faulty interface count is " + str(solarStateFaultyInterfaceCount))
        if mode == 'configured':
            for pod in ACI_Fabric.pods:
                for device in pod.devices:
                    for interface in device.interfaces:
                        if len(interface.deployedEPGs) or ('port-channel' in interface.name):
                            interface.mustBeMonitored = True
                    if device.solarwindsNode.existence:
                        for interface in device.interfaces:
                            for monitored in device.solarwindsNode.monitoredInterfaces:
                                if interface.mustBeMonitored and interface.name == monitored.name:
                                    interface.monitored = True

            print("Interface must be monitored in Solarwinds" + "*"*89)
            
            for pod in ACI_Fabric.pods:
                print("Pod name is " + pod.name)
                for device in pod.devices:
                    if device.oobmIpAddress != '':
                        if device.solarwindsNode.existence:
                            print("\tInterfaces have to be monitored in " + device.name + "(" + device.oobmIpAddress + ")")                   
                            for interface in device.interfaces:
                                if interface.mustBeMonitored and not interface.monitored:
                                    if 'port-channel' in interface.name:
                                        print("\t\t" + interface.name + "\t" + interface.adminState + "\t" + interface.operationalState + "\t Last State Change: " + str(interface.lastLinkStateChange))
                                    else:
                                        print("\t\t" + interface.name + "\t" + interface.adminState + "\t" + interface.operationalState + "\t Last State Change: " + str(interface.lastLinkStateChange) + "\t Deployed epg:" + str(len(interface.deployedEPGs)))
                                    unmonitoredInterfaceCount += 1
                        else:
                            print("Device name: %s with oobm ip  %s is not configured in Solarwinds" % (device.name, device.oobmIpAddress))
                            unmonitoredDeviceCount += 1
                    else:
                        print("\t Management ip address of " + device.name + " can not be obtained")
                        managementIpAbsentDeviceCount += 1
            print("Result obtained from CONFIGURED PORT MODE:\nYou have " + str(unmonitoredDeviceCount) + " unmonitored devices, \n"+str(unmonitoredInterfaceCount)+" unmonitored port and in ACI located on ip " + ACI_Fabric.IP)
        print("Process take %s seconds to complete" % str(time.time() - startingTime))
    else:
        print('Invalid operation mode is written,\nPlease use "up" or "configured" keyword after --mode')

if __name__ == "__main__":
    inputParser()
