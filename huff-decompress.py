from bitstring import BitArray
import pickle
import time,os
import sys

startTime=time.time()

(root,file)=os.path.splitext(sys.argv[1])  

try:
    with open(sys.argv[1],'rb') as fl:
        mybyte=fl.read()
except FileNotFoundError:
    print('file not found')
    

with open(root+'-symbol-model.pkl', 'rb') as handle:
    huffdic = pickle.load(handle)
    
b=BitArray(bytes=mybyte)
allBit=str(b.bin)

#'i' is the parameter, which help us to get every bit from binary file
i=0

# the output content
output=""

# the current bits
current=""

f=open(root+'-decompressed.txt','w+') #'w' means overwrite, 'a' means append to the end

while(True):
    current+=allBit[i:i+1]
    i=i+1
    if(current in huffdic):
        if(huffdic[current]==",,,,,*"):
            break;
        else:
            output+=huffdic[current]
            #clear the current bits
            current=""
    
            
f.write(output)
f.close()

endTime=time.time()
duratiom=endTime-startTime
print('\nthe decode consuming time is %fs\n'%(duratiom))
    