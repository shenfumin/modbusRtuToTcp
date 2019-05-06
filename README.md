# modbusRtuToTcp
convert modbusRTU to modbusTCP base on Linux platform
# you can use it with another modbus tools to simulate one modbus device

[your modbusRTU program] <---> [serial(/dev/pts/x)] <---> [MSS Modbus-TCP Server Simulator]

[your modbusRTU program]: your program used the modbusRTU.
[serial]:created by modbus_rtu_to_tcp.py.
[MSS Modbus-TCP Server Simulator]: one third party tools,you can download the MSS Modbus-TCP Server Simulator on the page http://tdogan.net/mss.html
