# CiscoAciSolarwindsEqualizer
Original Author: Sadık Turgut - st.sadik.turgut@gmail.com

Description

ACI-Solarwinds Equalizer is a tool that mainly purpose to report unmonitored interfaces of Cisco ACI Fabric in Solarwinds.


In fact, this project consumes an operational gap in organizations. Most of time, service provisioning teams forget or ignore to configure new added ports to Monitoring systems; So, this is a step that has to be tracked.

This tool have two mode of operations: First one 'up' mode is tracking up interfaces of ACI Fabric in Solarwinds, ant then give unmonitored interfaces of switches, second one is 'configured' mode and, in this mode, tool considers like a port with deployed epg's and every port-channel have to be monitoer in Solarwinds. Each mode can be useful for your needs.

ACI-Solarwinds Equalizer can be fired from cli with some arguments, there is no need to change code except the situation a development is required,

It consumes rest api of Cisco Api and Solarwinds Api, it uses token obtained from ACI to communicate sdn, and it uses Orion SDK(Software development kit of Solarwinds) for reaching Soalrwinds.

It never changes or configure something in ACI or Solarwinds,

If you are interested with ACI http requests in code, you can look your ACI screen right top and click 'Help and Tools', then choose 'Show Api Inspector'. This screen can show what urls are used to obtain informations shown on WEB GUI where you click. Moreover, if you are interested in more deep knowledge, you can search via Managed Object Tree of Cisco ACI, you can read this: https://www.cisco.com/c/en/us/td/docs/switches/datacenter/aci/apic/sw/1-x/aci-fundamentals/b_ACI-Fundamentals/b_ACI-Fundamentals_chapter_010001.html

If you are interested in Solarwinds programming, there is easy to use software development kit like Orion SDK, and you can read informations in below links:

 Firstly, read this:
 
 https://www.networkmanagementsoftware.com/solarwinds-orion-api-sdk-getting-started-part-1/
 
 Then, try to understand samples in this repo:
 
 https://github.com/solarwinds/orionsdk-python
 
 Of course, change them according to this informations:
 
 http://solarwinds.github.io/OrionSDK/schema/?CMP=BIZ-RVW-NMS-SW_WW_X_PP_PPD_LD_EN_NETMON_SW-X-X_X_X_X-SEPT_16%20_SDK
 
 

If you have any problem to run this code, or any suggestion to develop this, you can reach me via st.sadik.turgut@gmail.com

Installation Environment

Required

Python 3.7+

Recommended:

Git (to install from github)

Downloading and installing

Just clone this repo on your platform

git clone https://github.com/networkProgrammingDevStock/CiscoAciSolarwindsEqualizer.git

and go to project folder

cd CiscoACI

Sure you can use pip to install some additional packages:

pip install -r requirements.txt

if you are using Windows, and you add python do batch, means you can run python from command prompt, try this

python -m pip install -r requirements.txt

If you have two versions of python on your platform, please be sure what command to get in python3, Sometimes, keyword 'python' can call python3 idle, and sometimes that can be 'python3'. If 'python3' calls the newer version of python, use line as below,

python3 -m pip install -r requirements.txt

Usage

First be sure, can you reach our ACI ip address over where this code placed, Let's say your ACI web url https://A.B.C.D/#, you will use A.B.C.D(of course, this is an ip address) If you reach your ACI web GUI with url like https://ourACIonProdorWhatever.domain.com/#, try to ping this section 'ourACIonProdorWhatever.domain.com' to get ip address of your ACI Web address. In fact, you can use 'ourACIonProdorWhatever.domain.com' as a credential though to code, but, sometimes, script can not use dns services, and I am not suggest or solve that yet,
After being sure about your ACI credentials, you have to obtain Solarwinds swiss api, you can get some help from your monitoring system guy for this information, because the url, you are using the reach Solarwinds Orion is not resolved the ip address, you are looking for,

There are two modes of operation in ACI-Solarwinds Equalizer,

1- UP mode: You can get all of unmonitored up interfaces of Fabric in Solarwinds in a way:

    change to directory with 'cd CiscoAciSolarwindsEqualizer'

    to run Equalizer in 'up' mode,

python ACI_Scanner.py --ip_aci IP_ADDRESS_OF_YOUR_ACI --username_aci YourACI_Username --password_aci YourACI_Password --ip_solar IP_ADDRESS_OF_YOUR_SOLARWINDS --username_solar YourSOLARWINDS_Username --password_solar YourSOLARWINDS_Password --mode up

    after running that you will outputs like:

Libraries are imported

THERE WILL BE A HASH TEXT ON HERE TO SHOW YOU TOKEN

('You are authenticated to Apic on ', u'IP_ADDRESS_OF_YOUR_ACI')

Login process to Apic on IP_ADDRESS_OF_YOUR_ACI is finished

Digging interfaces for Leaf2

Digging interfaces for Leaf1

Digging interfaces for Spine2

Digging interfaces for Spine1

Getting solarwinds information of Leaf2

Step 1 for Leaf2_IP

NodeID of Leaf2_IP is Leaf2_SolarwindsNodeID

Step 2 for Leaf2_IP

Done for Leaf2_IP

Getting solarwinds information of Leaf1

Step 1 for Leaf1_IP

NodeID of Leaf1_IP is Leaf1_SolarwindsNodeID

Step 2 for Leaf1_IP

Done for Leaf1_IP

Getting solarwinds information of Spine1

Step 1 for Spine1_IP

NodeID of Spine1_IP is Spine1_SolarwindsNodeID

Step 2 for Spine1_IP

Done for Spine1_IP

Getting solarwinds information of Spine2

Step 1 for Spine2_IP

NodeID of Spine2_IP is Spine2_SolarwindsNodeID

Step 2 for Spine2_IP

Done for Spine2_IP

Pod name is pod-1

Interface must be monitored in Solarwinds*****************************************************************************************

Pod name is pod-WhateverYouConfigured

        Interfaces have to be monitored in Leaf2(Leaf2_IP)
	
        Interfaces have to be monitored in Leaf1(Leaf1_IP)
	
				port-channelX  up      up       Last State Change: 2001-02-03
				
        Interfaces have to be monitored in Spine1(Spine1_IP)
	
        Interfaces have to be monitored in Spine2(Spine2_IP)
	
				EthernetY/Z	   up      up       Last State Change: 2004-05-06 Deployed epg:3
				
Result obtained from UP PORT MODE:

You have 0 unmonitored devices,

 2 unmonitored port and in ACI located on ip IP_ADDRESS_OF_YOUR_ACI
 
Count of device without obtained management ip address is 0

Solar state faulty interface count is 0

Process take 123.456789 seconds to complete


2- CONFIGURED mode: this 'configured' word means that an interface has deployed EPG, also, port-channel interfaces. The reason behind the inclusion of port-channels, although you can not obtain deployed epg information of port-channels, we all know a port-channel was not configured automatically, You can get all of unmonitored configured interfaces of Fabric in Solarwinds in a way:

    change to directory with 'cd CiscoAciSolarwindsEqualizer'

    to run Equalizer in 'up' mode,

python ACI_Scanner.py --ip_aci IP_ADDRESS_OF_YOUR_ACI --username_aci YourACI_Username --password_aci YourACI_Password --ip_solar IP_ADDRESS_OF_YOUR_SOLARWINDS --username_solar YourSOLARWINDS_Username --password_solar YourSOLARWINDS_Password --mode configured

    after running that you will outputs like:

Libraries are imported

THERE WILL BE A HASH TEXT ON HERE TO SHOW YOU TOKEN

('You are authenticated to Apic on ', u'IP_ADDRESS_OF_YOUR_ACI')

Login process to Apic on IP_ADDRESS_OF_YOUR_ACI is finished

Digging interfaces for Leaf2

Digging interfaces for Leaf1

Digging interfaces for Spine2

Digging interfaces for Spine1

Getting solarwinds information of Leaf2

Step 1 for Leaf2_IP

NodeID of Leaf2_IP is Leaf2_SolarwindsNodeID

Step 2 for Leaf2_IP

Done for Leaf2_IP

Getting solarwinds information of Leaf1

Step 1 for Leaf1_IP

NodeID of Leaf1_IP is Leaf1_SolarwindsNodeID

Step 2 for Leaf1_IP

Done for Leaf1_IP

Getting solarwinds information of Spine1

Step 1 for Spine1_IP

NodeID of Spine1_IP is Spine1_SolarwindsNodeID

Step 2 for Spine1_IP

Done for Spine1_IP

Getting solarwinds information of Spine2

Step 1 for Spine2_IP

NodeID of Spine2_IP is Spine2_SolarwindsNodeID

Step 2 for Spine2_IP

Done for Spine2_IP

Pod name is pod-1

Interface must be monitored in Solarwinds*****************************************************************************************

Pod name is pod-WhateverYouConfigured

        Interfaces have to be monitored in Leaf2(Leaf2_IP)
	
        Interfaces have to be monitored in Leaf1(Leaf1_IP)
	
				port-channelX  up      down       Last State Change: 2001-02-03
				
        Interfaces have to be monitored in Spine1(Spine1_IP)
	
				EthernetQ/W	   up      down       Last State Change: 2004-05-06 Deployed epg:5
				
        Interfaces have to be monitored in Spine2(Spine2_IP)
	
				EthernetY/Z	   up      up       Last State Change: 2004-05-06 Deployed epg:3
				
Result obtained from CONFIGURED PORT MODE:

You have 0 unmonitored devices,

 3 unmonitored port and in ACI located on ip IP_ADDRESS_OF_YOUR_ACI
 
Count of device without obtained management ip address is 0

Solar state faulty interface count is 0

Process take 123.456789 seconds to complete

