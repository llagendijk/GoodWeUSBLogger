import json
import logging


def sendInt2Domoticz(client, topic, idx, value):
    jsonString = '{ "idx" : %s, "nvalue" : %d, "svalue" : "" }' % (idx, value)
    logging.debug("Sending to domo: %s", jsonString)
    client.publish(client, topic, payload=jsonString)


def sendString2Domoticz(client, topic, idx, value):
    jsonString = '{ "idx" : %s, "nvalue" : 0, "svalue" : "%s" }' % (idx, value)
    logging.debug("Sending to domo: %s", jsonString)
    client.publish(topic, payload=jsonString)


class Inverter2Domo:

    def __init__(self, inverterConfig, logging, topicDomoticz):
        self.logging = logging
        self.topicDomoticz = topicDomoticz
        self.keyDict = {}
        for key in inverterConfig:
            idx = int(inverterConfig[key])
            self.keyDict[key] = idx
        self.logging.debug("items: %s", self.keyDict)

    def processOnline(self, online, client):
        try:
            idx = self.keyDict["online"]
        except Exception as e:
            self.logging.warning(
                "online not defined for inverteri {}. skipping".format(e))
            return

        self.logging.debug("numeric value for online: {}{}".format(
            type(online), online))
        if online == 0:
            value = "Offline"
        else:
            value = "Online"
        self.logging.debug("Online = %s", value)
        sendString2Domoticz(client, self.topicDomoticz, idx, value)

    def processData(self, inverterData, client):
        # self.logging.debug("Processing data message %s", parsedJson)
        # invertertype = inverterData.inverterType
        runningInfo = inverterData.runningInfo
        for key in self.keyDict:
            idx = self.keyDict[key]
            # TODO: fix/expand for 3 phase inverters
            if key == "online":
                # nothing to do
                dummy = key
            elif key == "power_daytotal":
                dayTotal = runningInfo.eDay
                dayTotalWh = float(dayTotal) * 1000
                value = "%.1f" % dayTotalWh
                sendString2Domoticz(client, self.topicDomoticz, idx, value)
            elif key == "power_grand_total":
                value = runningInfo.eTotal
                sendString2Domoticz(client, self.topicDomoticz, idx, value)
            elif key == "errormessage":
                value = runningInfo.errorMessage
                self.logging.debug("Errormessage = %s", value)
                if not value:
                    value = "None"
                sendString2Domoticz(client, self.topicDomoticz, idx, value)
            elif key == "mains_frequency":
                value = runningInfo.fac1
                sendString2Domoticz(client, self.topicDomoticz, idx, value)
            elif key == "total_hours":
                value = runningInfo.hTotal
                sendString2Domoticz(client, self.topicDomoticz, idx, value)
            elif key == "mains_current":
                value = runningInfo.iac1
                sendString2Domoticz(client, self.topicDomoticz, idx, value)
            elif key == "input1_current":
                value = runningInfo.ipv1
                sendString2Domoticz(client, self.topicDomoticz, idx, value)
            elif key == "input2_current":
                value = runningInfo.ipv2
                sendString2Domoticz(client, self.topicDomoticz, idx, value)
            elif key == "current_power":
                pac = runningInfo.pac
                dayTotal = runningInfo.eDay
                dayTotalWh = float(dayTotal) * 1000
                value = "%s;%.1f" % (pac, dayTotalWh)
                sendString2Domoticz(client, self.topicDomoticz, idx, value)
            elif key == "temperature":
                value = runningInfo.temp
                sendString2Domoticz(client, self.topicDomoticz, idx, value)
            elif key == "mains_voltage":
                value = runningInfo.vac1
                sendString2Domoticz(client, self.topicDomoticz, idx, value)
            elif key == "input1_voltage":
                value = runningInfo.vpv1
                sendString2Domoticz(client, self.topicDomoticz, idx, value)
            elif key == "input2_voltage":
                value = runningInfo.vpv2
                sendString2Domoticz(client, self.topicDomoticz, idx, value)
            else:
                self.logging.warning("Unknown key %s for domoticz", key)
