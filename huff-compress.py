import sys,re,getopt
import pickle,os
import array
import time

startTime_total=time.time()

class CommandLine:
    def __init__(self):
        
        opts,args=getopt.getopt(sys.argv[1:],'s:')#'s' indicate based on character or word.
        opts=dict(opts)
        
        self.filename=args[0]
        
        if '-s' in opts :
            self.tokType=opts['-s']
        else:
            print('please input word or char')
            sys.exit()
        
        (root,file) = os.path.splitext(args[0])
        #we can test different Data file, and generate their corresponding files
        self.root=root
        
    def getSysIn(self):
        return self.filename,self.tokType,self.root



class Tokenization:
    def __init__(self,filename,TokType):
        try:
            with open(filename,'r') as fl:
                self.infile=fl.read()
        except FileNotFoundError:
            print('file not found')
        self.tokType=TokType
        self.sorted_dic=None
            
    def tokenization(self):
        tocword=re.compile('[a-zA-Z]+|[^a-zA-Z]')
        toccha=re.compile('[\s]|[\S]')
        
        if(self.tokType=='char'):
            splitingResult=toccha.findall(self.infile)
        else:
            splitingResult=tocword.findall(self.infile)
            
        #count the probability of each item
        dic={}
        totalCount=0 

        for i in splitingResult:
            if i in dic:
                dic[i]+=1
            else:
                dic[i]=1
        
        for i in dic:
            totalCount+=dic[i]

        for i in dic:
            dic[i]=dic[i]/totalCount

        # add Pseudo-EOF character
        dic[',,,,,*']=1/totalCount

        self.sorted_dic = sorted(dic.items(), key=lambda kv: kv[1])
        
        return self.sorted_dic,splitingResult


class node:
    def __init__(self,name=None,freq=None,leftsub=None,rightsub=None):
        #self.id=id
        self.name=name
        self.leftsub=leftsub
        self.rightsub=rightsub
        self.frequency=freq
        
    def setleft(self,leftsub):
        self.leftsub=leftsub
    def setright(self,rightsub):
        self.rightsub=rightsub
        
    def getleft(self):
        return self.leftsub
    def getright(self):
        return self.rightsub
    def getname(self):
        return self.name
    def getfreq(self):
        return self.frequency

    
class huff:
    def __init__(self,sortedDic):
        #declare a list whose elements are node objects, and sorted by their probability
        self.hufflist=[]
        for i in sortedDic:
            leafnode=node(name=i[0],freq=i[1])
            self.hufflist.append(leafnode)
        self.huffDic={}
        self.rootNode=None

    def generateHuff(self):
        while(len(self.hufflist)>2):
            #combine two smallest node to a new node
            newNode=node(freq=self.hufflist[0].getfreq()+self.hufflist[1].getfreq(),leftsub=self.hufflist[0],rightsub=self.hufflist[1])
    
            ##remove smallest two
            del self.hufflist[0]

            del self.hufflist[0] 
    
            #insert new node to our list
            if(newNode.getfreq()>self.hufflist[-1].getfreq()):
                self.hufflist.insert(len(self.hufflist),newNode)
            else:
                for i in range(len(self.hufflist)):
                    if(newNode.getfreq()<=self.hufflist[i].getfreq()):
                        index=i
                        break
                self.hufflist.insert(index,newNode)
        #seet root code
        self.rootNode=node(freq=self.hufflist[0].getfreq()+self.hufflist[1].getfreq(),leftsub=self.hufflist[0],rightsub=self.hufflist[1])
        
    
    #iterate our Huffman tree to get binary code of each symbol
    def getHuffCode(self,node,i):
        if(node.getleft()):
            self.getHuffCode(node.getleft(),i+"0")
        if(node.getright()):
            self.getHuffCode(node.getright(),i+"1")
        
        if(node.getleft()==None and node.getright()==None):
            self.huffDic[node.getname()]=i
    
    # get binary code of each symbol       
    def gethuffDic(self):
        self.getHuffCode(self.rootNode,"")
        return self.huffDic
        

#convert our '0','1' string into binary format, and write to the file,this is a single function without class
def tobinary(string,stride):
    codeArray=array.array('B')

    if(len(string)%stride):
        p=8-(len(string)%stride)
        #to make it can divided by 8 
        for i in range(p):
            string+='0'
        
    for i in range(int(len(string)/stride)):
        codeArray.append(int(string[i*stride:i*stride+stride],2))
    
    #write the result to the file
    f = open(root+'.bin', 'wb+')
    codeArray.tofile(f)
    
    f.close()




#==============================================================================
# MAIN

if __name__ == '__main__':
    
    #get commandLine input
    config=CommandLine()
    filename,tokType,root=config.getSysIn()
    
    buildModeStartTime=time.time()
    
    #tokenization
    token=Tokenization(filename,tokType)
    sorted_dic,splitingResult=token.tokenization()
    
    #build Huffman tree 
    huffTree=huff(sorted_dic)
    huffTree.generateHuff()
    huffDic=huffTree.gethuffDic()
    
    buildModelEndTime=time.time()
    print('\nthe duration to build the model based on %s is %fs'%(tokType,buildModelEndTime-buildModeStartTime))
   
    ###############################encode
    encodeStartTime=time.time()
    
    #compress to binary code
    binaryString=""
    for i in splitingResult:
        binaryString+=huffDic[i]

    #add Pseudo-EOF to the end 
    binaryString=binaryString+huffDic[',,,,,*']


    ##convert our '0','1' string into binary format, and write to the file
    tobinary(binaryString,8)
    
    encodeEndTime=time.time()
    print('the duration to endcode based on %s is %fs\n'%(tokType,encodeEndTime-encodeStartTime))

    #inverse the dictionary to make binary code be the key and word be the value 
    newdic={}
    newdic={huffDic[i]:i for i in huffDic}

    #store the inversed dictionary to the pkl file 
    with open(root+'-symbol-model.pkl', 'wb+') as handle:
        pickle.dump(newdic, handle, protocol=pickle.HIGHEST_PROTOCOL)
