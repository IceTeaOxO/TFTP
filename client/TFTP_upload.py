#coding=utf-8
 
import sys
import struct
from socket import *
# import pathlib
# print(pathlib.Path().absolute())

 
def run_test():
	if len(sys.argv) != 1:
		print('-'*30)
		print("tips: if you path is /TFTP")
		print("python3 client/TFTP_upload.py")
		print('-'*30)
		exit()
		
 
#主程序
def main():
	run_test()
	g_server_ip = input("Please key in the IP to upload(If your server is local, key in 127.0.0.1)：")
	g_uploadFileName = input("Please key in the file's name(ex: Test.txt)：")
	print(g_server_ip, g_uploadFileName)
 
	# 打包
	sendDataFirst = struct.pack('!H%dsb5sb'%len(g_uploadFileName), 2, g_uploadFileName.encode('gb2312'), 0, 'octet'.encode('gb2312'), 0)
 
	s = socket(AF_INET, SOCK_DGRAM)
 
	s.sendto(sendDataFirst, (g_server_ip, 6969)) #第一次發送，連接伺服器
 
	fileNum = 0 #表示上傳文件的序號
 
	# 以二進制方式讀取文件
	f = open('client/'+g_uploadFileName, 'rb')
 
	# 第一次接收
	responseData = s.recvfrom(1024)
 
	recvData, serverInfo = responseData

	# 解包
	packetOpt = struct.unpack("!H", recvData[:2])  #opcode
	packetNum = struct.unpack("!H", recvData[2:4]) #blockNum
	
	#print(packetOpt, packetNum)
 
	if packetOpt[0] == 5:
		print("tftp server error!")
		exit()
 
	while True:
		#　從文件中讀取512bytes
		readFileData = f.read(512)
		
		if fileNum > 65535:
			fileNum = 0
		## 如果序號大於65535，需要從0開始計算
		
		#　打包
		sendData = struct.pack('!HH', 3, fileNum) + readFileData
		
		# 發送到tftp server
		s.sendto(sendData, serverInfo) 
 
		# 接收回傳訊息
		recvData, serverInfo = s.recvfrom(1024)
 
		#print(recvData)
 
		# 解包
		packetOpt = struct.unpack("!H", recvData[:2])  #opcode
		packetNum = struct.unpack("!H", recvData[2:4]) #blockNum
 
		if packetOpt[0] == 5:
			print("tftp server error!")
			exit()
 
		if len(sendData) < 516 or packetNum[0] != fileNum:
			print("%sfile upload completed!"%g_uploadFileName)
			break
		
		fileNum += 1
 
	f.close()
 
	s.close()
 
 
if __name__ == '__main__':
	main()