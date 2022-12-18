# 109306062 資管三 黃宥荃

import os
import struct
import socket
# import pathlib
# print(pathlib.Path().absolute())
## 查詢當前路徑

#Main function
def main():
    ## ip 要連接上的設備ip位置
    ## FileName要下載的檔案名稱
    # g_server_ip = input("Please key in the IP to download(If your server is local, key in 127.0.0.1)：")
    g_downloadFileName = input("Please key in the file's name(ex: Test.txt)：")
    # print(g_server_ip, g_downloadFileName)
    g_server_ip="127.0.0.1"
    # g_downloadFileName="bigfile.txt"
    
    
    
    sendDataFirst = struct.pack('!H%dsb5sb'%len(g_downloadFileName), 1, g_downloadFileName.encode('ascii'), 0, 'octet'.encode('ascii'), 0)
    ## pack成network,short,十進制整數(這裡是檔案名稱大小)chars,char,5chars,char
    ## 01,fileName,0,octet,0
    
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ## 使用網路傳輸DATA
    ## 一對一使用UDP

    ## 6969: port number##
    s.sendto(sendDataFirst, (g_server_ip, 6969)) #First send, connect to tftp server
    ## 傳輸封包內容到特定(IP,port)
    
    
    # Indicates that the data can be downloaded, if it is false then delete the file
    downloadFlag = True
    # Indicates the serial number of the received file
    fileNum = 0 
    ## block編號，從1開始，超過65535則從0計算
    
    
    # Open file in binary format
    print(g_downloadFileName)
    f = open('client/'+g_downloadFileName, 'wb')
    ## 在客戶端創建fileName的檔案，使用二進制方式寫入
    
    
    while True:
        # Receive response data sent back by the server
        recvData, serverInfo = s.recvfrom(1024)
        #print(responseData)
        # print(recvData)
        # print(serverInfo)
        ## 接收伺服器的DATA


        # Unpacking
        packetOpt = struct.unpack("!H", recvData[:2])  #Opcode
        packetNum = struct.unpack("!H", recvData[2:4]) #Block number
        ## 將收到的封包前兩位元使用short unpack，是opcode
        ## 將收到的封包2-4位元使用short unpack，是block number
        
        
        #print(packetOpt, packetNum)
        
        # Received packet
        if packetOpt[0] == 3: #Opcode is a tuple(3,), and 3 means DATA
            # Calculate the serial number of this file, which is the last received +1
            ## opcode=03表示現在傳送的是DATA
            
            fileNum += 1
            ## 只要收到DATA，計數器就+1
            if fileNum>65535:
                ## 如果>65535，則從0開始計算
                fileNum=0
            
            # Whether the packet number is equal to the previous time
            if fileNum == packetNum[0]:
                f.write(recvData[4:]) #Write into file
                ## 確定當前的計數器號碼=傳送過來的block號碼，如果相同則把除了前4位元組的資料寫入檔案

            # Organize ACK packets
            ackData = struct.pack("!HH", 4, packetNum[0])
            s.sendto(ackData, serverInfo)
            ## 收到後傳送ACK DATA 給server
            
            
            
        # Error response
        elif packetOpt[0] == 5: # 5 means error happen
            print("Sorry, there is no this file!")
            downloadFlag = False # Delete the file
            break

        else:
            print(packetOpt[0])
            break
            ## 如果都不是上述則print 出 opcode
            
        if len(recvData) < 516:
            ## 2+2+512=516
            downloadFlag = True
            print("%s File download completed!"%g_downloadFileName)
            break
            ## 如果從伺服器接收到的檔案大小小於516bytes，代表檔案已經傳送完畢
            
    if downloadFlag == True:
        f.close()
        ## 如果傳送完畢則關閉寫入檔案
        
    else:
        f.close()
        os.remove(g_downloadFileName)
        ## 如果有任何錯誤，關閉寫入檔案，並且移除
        

if __name__ == '__main__':
    main()