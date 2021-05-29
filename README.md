# iot_project

## Phase I implementation of the End-to-Edge communication pipeline.

Edge Computer follows the defined protocol to perform the necessary handshake and accept the sensor-reading messages from the end-devices.

 - It assigns a unique 2-Byte ID to each end-device connected
 - To save the memory, it only saves the required fields of the end-device configurations in a form of Python Dictionary instead of complete configurations.yaml file of each end device. To do so, it momentarily holds the complete configuration file in config_holder.yaml, parses it to extract the required fields and then discards the actual file.
 - It maintains a runtime record of the mappings between assigned IDs and the configuration-dictionary of the underlying end-devices in the form of a master dictionary.
 - To persist the mappings through system reboots or system crash, it maintains a backup log of the parent dictionary in a yaml file (mapping_logs.yaml)
 - To avoid overflow of the mappings dictionary with redundant data of devices that are no longer in use, Edge computer runs a separate gaarbage collector thread periodically to free up unnecessary mappings and IDs that can now be assigned again to new connections.
 - It extracts, transforms and loads the incoming messages (sensor readings) with all the required data in a structure that is compliant with the cloud services and forwards it to other program of the Edge computer that communicates with the cloud (that program is not in this repo)
 
End device folder contains program that also follows the defined protocol to perform the necessary handshake and send the sensor-reading messages to the Edge Computer.
 - it only contains a dummy config file and a single dummy sensor reading to test out the communication pipeline. It supports communication over wifi and bluetooth, and methods to establish keep-alive connections as well as capability to disconnect, sleep for period of its transmission rate (mentioned in config file) to save power resources and then quickly connect again to the Edge for sending the next reading. 
 - This End-device folder does not contain code for setting up sensor drivers, creating config files and reading from sensors. To access the complete end-device code, please refer to the main ema-end-device repo: https://github.com/agoryelov/ema-end-device
