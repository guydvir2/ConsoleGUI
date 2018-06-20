import os

#My modules.
import readfile_ssh
import getip

class VerifyPigpiodByIP:
    def __init__(self, master=None, **kwargs):
        self.master = master
        #if filename != [] and path !=[]:
            #self.path = path
            #self.filename = filename

        self.local_ip=getip.get_ip()[0]
        self.valid_pis, self.non_valid_pis=[],[]
        self.load_pi_list(kwargs)
        self.check_valid_pi()


    def load_pi_list(self, args):
        self.list_pi=readfile_ssh.LoadFile(**args).data_from_file#filename=self.filename, path=self.path, **args).data_from_file
        #self.list_pi.append(['192.168.2.116','Rpi5'])
        print("IP list to check:\n",self.list_pi)
        

    def check_valid_pi(self,pi=[]):
        if pi!=[]:
            print(pi)
            self.list_pi=[pi]
        for i,current_pi in enumerate(self.list_pi):
            ping_result = os.system('ping %s -c 1 >NULL' % str(current_pi[0]))
            if ping_result == 0 :
                res= readfile_ssh.PigpiodManager(self, str(current_pi[0]),self.local_ip,'kupelu9e').get_state()
                if res[0]!='': self.valid_pis.append(str(current_pi[0]))
                else: self.non_valid_pis.append(str(current_pi[0]))
            else:
                self.non_valid_pis.append(str(current_pi[0]))
        print("IP's with Pigpiod loaded:",self.valid_pis)
        print("IP's faild to load Pigpiod/ Ping:",self.non_valid_pis)

    def check_specific_ip(self, check_ip):
        self.check_valid_pi(check_ip)
        

    def get_state(self):
        return [self.valid_pis, self.non_valid_pis]
        
        
class IPScanner():
    """This class pings to find live ip's between start_ip=1 and end_ip=256 given by user."""
    def __init__(self,start_ip,end_ip):
        self.start_ip = start_ip
        self.end_ip = end_ip
        self.lost, self.found=[],[]
        self.local_ip=getip.get_ip()[0]
        a=self.local_ip.split('.')
        self.router=a[0]+'.'+a[1]+'.'+a[2]+'.'
        self.search_ping()

    def search_ping(self):
        if self.start_ip >0 and self.end_ip<=256:
            for i in range(self.start_ip,self.end_ip+1):
                if os.system('ping %s -c 3 >NULL' % (self.router+str(i))) == 0:
                    print("success:",self.router+str(i))
                    self.found.append(self.router+str(i))
                else:
                    print("fail:",self.router+str(i))
                    self.lost.append(self.router+str(i))
                    
                    
        else: print("IP Out of range")
    def get_State(self):
        return [self.found, self.lost]
            
        
if __name__ == "__main__":
    path='/home/guy/PythonProjects/'
    filename= 'Rpi_Clients.ini'
    defaults=['192.168.2.113','Main']
    q=VerifyPigpiodByIP(path=path, filename=filename, titles=['IPs_clients','Alias'], defaults=defaults)
    q.check_specific_ip(['192.168.2.116','RPI6'])
    #q.check_specific_ip(['192.168.2.117','RPI7'])

    #b=IPScanner(113,120)
        


