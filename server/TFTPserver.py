# 109306062 資管三 黃宥荃
import struct
import socket
from threading import Thread
import pathlib
print(pathlib.Path().absolute())

# Client download thread
def download_thread(fileName, clientInfo):
    print("Responsible for processing client download files")
    ## 下載線程
    # Create a UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    ## 開啟socket
    
    fileNum = 0 #Indicates the serial number of the received file
    ## 使用計數器計算當前傳到第幾個檔案
    
    try:
        f = open('server/'+fileName,'rb')
        ## 伺服器嘗試創建檔案並使用二進制讀取
        
        
        
        
    except:
        errorData = struct.pack('!HHHb', 5, 5, 5, fileNum)
        ## short,short,short,char
        
        # Send an error message
        s.sendto(errorData, clientInfo)  #Sent the message when the file does not exist
        print("download ERR:",errorData)
        exit()  #Exit the download thread
        
        ## 如果發生錯誤，傳送錯誤訊息給客戶端，並且結束下載線程
        
    while True:
            # Read file contents 512 bytes from local server
            readFileData = f.read(512)
            print("READFILE:",readFileData)
            print("reading...:",fileNum)
            ## 如果成功讀取檔案，一次讀取512bytes檔案
            
            # The block number starts at 0 and increments by one each time. Its range is [0, 65535]
            fileNum += 1
            ## 讀取完後fileNum+1
            
            if fileNum>65535:
                ## 如果blockNum>65535則需要從0開始計算
                fileNum=0

            sendData = struct.pack('!HH', 3, fileNum) + readFileData 
            ## short,short,data
            # print("download packet:",struct.unpack("!%ds"%len(readFileData),sendData[4:]))
            
            
            # Send file data to the client
            s.sendto(sendData, clientInfo)  #Data sent for the first time
            ## 將讀取到的資料傳送出去
            
            
            # When the data received by the client is less than 516 bytes, it means that the transmission is completed!
            if len(sendData) < 516:
                print("User"+str(clientInfo), end='')
                print('：Download '+fileName+' completed！')
                break
            ## 如果傳送出去的資料長度小於516bytes，則印出conpleted
                    
            
                        
            # Receiving data for the second time
            recvData, clientInfo = s.recvfrom(1024)
            #print(recvData, clientInfo)
            ## 接收客戶端傳來的DATA(ACK)

            # Unpacking
            packetOpt = struct.unpack("!H", recvData[:2])  #Opcode
            packetNum = struct.unpack("!H", recvData[2:4]) #Block number
            ## 接收客戶端傳送回來的opcode,block num
            #print(packetOpt, packetNum)
            print("download client ACK:",packetOpt,packetNum)
            
            
            
            if packetOpt[0] != 4 or packetNum[0] != fileNum:
                print("File transfer error！")
                break
            ## 如果收到的DATA opcode開頭不是ACK或者block num不等於當前的fileNum則跳出迴圈，關閉線程、socket
            
            
    # Close file
    f.close()
    
    # Close UDP port
    s.close()

    # Exit the download thread
    exit()


# Client uploading thread
def upload_thread(fileName, clientInfo):
    print("Responsible for processing client upload files")
    ## 進入上傳線程(WRQ)
    fileNum = 0 #Indicates the serial number of the received file
    
    # Open the file in binary mode
    f = open(fileName, 'wb')
    ## 開啟並寫入檔案
    
    # Create a UDP port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    sendDataFirst = struct.pack("!HH", 4, fileNum) 
    ## 送給客戶端opcode=4,fileNum(ACK)，表示可以開始上傳資料

    # Reply to the client upload request
    s.sendto(sendDataFirst, clientInfo)  #Sent with a random port at first time

    while True:
        # Receive data sent by the client
        recvData, clientInfo = s.recvfrom(1024) #Client connects to my random port at second time
        ## 接收客戶上傳的DATA，一次最多接收1024
        
        #print(recvData, clientInfo)
        
        # Unpacking
        packetOpt = struct.unpack("!H", recvData[:2])  #Identify opcode
        packetNum = struct.unpack("!H", recvData[2:4]) #Block number
        ## 將收到的DATA unpack，將opcode,blockNum記錄下來
        
        #print(packetOpt, packetNum)
        
        # Client upload data
        # opcode == 3 means Data
        if packetOpt[0] == 3 and packetNum[0] == fileNum:
            ## 如果接受到的opcode=3，且blockNum=fileNum，則寫入檔案
            #　Save data to file
            f.write(recvData[4:])
            
            # Packing
            sendData = struct.pack("!HH", 4, fileNum)
            ## 將ACK訊息傳給客戶端
            # Reply client's ACK signal
            s.sendto(sendData, clientInfo) #The second time using a random port to sent
            
            fileNum += 1
            ## 傳完之後fileNum+1，代表傳送第1個DATA packet
            
            if fileNum>65535:
                ## 如果blockNum>65535則需要從0開始計算
                fileNum=0
            
            #If len(recvData) < 516 means the file goes to the end
            if len(recvData) < 516:
                print("User"+str(clientInfo), end='')
                print('：Upload '+fileName+' complete!')
                break
            ## 如果接受到要寫入的DATA小於516，表示檔案傳送完畢
                
    # Close the file
    f.close()
    
    # Close UDP Port
    s.close()
    
    # Exit upload thread
    exit()

# Main function
def main():
    # Create a UDP port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
  
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ## 重新設定socket
    
    ## Bind local host and port number 6969 ##
    s.bind(('127.0.0.1', 6969))
    
    print("TFTP Server start successfully!")
    print("Server is running...")
    
    ## 上面都是開啟伺服器
    
    while True:
        
        # Receive messages sent by the client
        recvData, clientInfo = s.recvfrom(1024)  #　Client connects to port 69 at the first time
        #print(clientInfo) 
        ## 接收客戶端傳輸的資料，一次最多收1024bytes
        
        
        
       
        if struct.unpack('!b5sb', recvData[-7:]) == (0, b'octet', 0):
            opcode = struct.unpack('!H',recvData[:2])  #　Opcode
            fileName = recvData[2:-7].decode('ascii') #　Filename
            ## 將客戶端的二進制DATA unpack 
            ## char,5chars,char,只檢查封包最後7個bytes是否=0,octet,0
            ## 將opcode先解出來
            ## 在將fileName解出來
            print("(1)opcode==",opcode)
            
            # Request download
            # opcode == 1 means download
            if opcode[0] == 1:
                t = Thread(target=download_thread, args=(fileName, clientInfo))
                t.start() # Start the download thread
                ## 如果opcode=1，代表RRQ，開啟下載線程，傳入檔案名稱和客戶端資訊
                print("(2)opcode==",opcode)
                
                
            # Request uploading
            # opcode == 2 means uploading
            elif opcode[0] == 2:
                t = Thread(target=upload_thread, args=(fileName, clientInfo))
                t.start() # Start uploading thread
                ## 如果opcode=2，代表WRQ，開啟上傳線程，傳入檔案名稱和客戶端資訊
                print("(3)opcode==",opcode)
    # Close UDP port
    s.close()
    ## 跳出迴圈後才會close

# Call the main function
if __name__ == '__main__':
    main()