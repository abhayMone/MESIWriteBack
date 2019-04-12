from random import randint
import sys
import null

class Memory:
    #Class  Memory : shared memory block#
    def __init__(self):
        self.data = [randint(0, 100) for x in range(4)]
        self.status = ["fresh" for x in range(4)]



class Cache:
    #Class Cache :
    #State = Invalidate / Exclusive / Shared / Modified
    #      = Initial State : Invalidate#
    #Value = Data#
    #Address = Address of memory block#
    def __init__(self):
        self.state = "I"
        self.value = null
        self.address = null

class admin:
    #Class admin :
    #Handles processor,memory and bus#
    def __init__(self):
        self.memory = Memory()
        self.bus = Bus(self.memory)
        self.processors = {}
        for processor_number in range(4):
            self.processors= Processor(processor_number, self.bus, self.memory)

    def printStatus(self):
        print("Main Memory block and Status : ")
        print(self.bus.memory.data)
        print(self.bus.memory.status)
        print(" ")
        print("*********************")
        if (str(self.bus.instruction_type) == "reads"):

            print("Instruction  : CPU_" + str(self.bus.instruction_processor) + " " +
                  str(self.bus.instruction_type) + " from address:" + str(self.bus.instruction_address))
        elif((self.bus.instruction_type) == null):
            print("Instruction : null")
        else:
            print("Instruction : CPU_" + str(self.bus.instruction_processor) + " " +
                  str(self.bus.instruction_type) + " " + "value:" + str(
                self.bus.instruction_value) + " to address:" + str(self.bus.instruction_address))


        print(" ")
        for processor in range(len(self.bus.processors)):
            print("*********************")
            print("\tCPU"+str(processor))
            print("Cache State[" + self.bus.processors[processor].cache.state + "]")


            if(self.bus.processors[processor].cache.address == null):
                print("Cache memory address[" + "nil" + "]")
            else:
                print("Cache memory address[" + str(self.bus.processors[processor].cache.address)+ "]")

            if (self.bus.processors[processor].cache.value == null):
                print("Cache memory[" + "nil" + "]")
            else:
                print("Cache memory[" + str(self.bus.processors[processor].cache.value)+ "]")

        print("-----------------------------------------------")

class Bus:
    #Class bus :
    #Functions : read instructions#
    #          : deal with processors and memory blocks to signal them regarding changes#
    def __init__(self, memory):
        self.memory = memory
        self.processors = []       #processors
        self.instruction_processor = null
        self.instruction_type = null
        self.instruction_address = null
        self.instruction_value = null


    def instruction(self, processor, r_w, address,value):

        self.instruction_processor = processor
        self.instruction_type = ("reads" if (r_w == 0) else "writes")
        print( self.instruction_type)
        self.instruction_address = address
        self.instruction_value = value

        if r_w:
            #write instruction
            self.processors[processor].writeInstruction(address,value)

        else:
             #read instruction
             self.processors[processor].readInstruction(address)
        return


    def bus_snoop(self, processor_no ,address, value):
        flag = 0
        for processors in range(len(self.processors)):
            if(processors != processor_no):

                if(self.processors[processors].cache.address == address):
                    self.processors[processors].cache.state = "I"
                    flag = 1

        if flag == 1:
            return  True
        else:
            return False

    def read_bus_snoop(self,processor_number, address):
        flag = 0
        for processors in range(len(self.processors)):
            if (processors != processor_number):

                if (self.processors[processors].cache.address == address):
                    if (self.processors[processors].cache.state == "I"):
                        continue
                    else:
                        self.processors[processors].cache.state = "S"
                        if(self.memory.status[self.processors[processors].cache.address] == "stale"):
                            self.memory.data[self.processors[processors].cache.address] = self.processors[processors].cache.value
                            self.memory.status[self.processors[processors].cache.address] = "fresh"
                        flag = 1

        if flag == 1:
            return  True
        else:
            return False


class Processor:
    #Class processor:
    #               : read and write value from the cache
    #               : State changes
    # Invalidate State : Cache data is invalidate
    # Shared state : Updated copy of data is contained by multiple caches
    # Modified State : Updated copy of data is present in cache only(dirty) but not in memory i.e.,
    # cache value doesn't matches with main memory
    # Exclusive State : Updated copy of data is present in cache and in memory (Clean) i.e.,
    # cache value matches with main memory #

    def __init__(self, processor_number, bus, memory):

        self.cache = Cache()
        self.processor_number = processor_number
        self.bus = bus
        self.memory = memory
        self.bus.processors.append(self)


    def writeInstruction(self,address,value):
        if(self.cache.address == null):
            if(self.bus.bus_snoop(self.processor_number,address,value)):
                #if(self.memory.status[address] == "fresh"):
                #    self.memory.status[address] == "stale"
                self.cache.state = "E"
                self.cache.address = address
                self.cache.value = value
                self.memory.data[address] = value
                #self.bus.bus_snoop(self.processor_number, address, value)
            else:
                self.cache.state = "M"
                self.cache.address = address
                self.cache.value = value
                self.memory.status[address] = "stale"
                #self.bus.bus_snoop(self.processor_number, address, value)

        elif(self.cache.address == address):
            if(self.cache.state == "S"):
                self.cache.state = "E"
                self.cache.value = value
                self.cache.address = address
                self.bus.bus_snoop(self.processor_number,address,value)
            if (self.cache.state == "E"):
                self.cache.state = "M"
                self.cache.value = value
                self.cache.address = address
                if(self.memory.status[self.cache.address] == "fresh"):
                    self.memory.status[self.cache.address] = "stale"
                self.bus.bus_snoop(self.processor_number,address, value)
            if (self.cache.state == "M"):
                self.cache.value = value
                self.cache.address = address
                self.bus.bus_snoop(self.processor_number,address, value)
        else:
            if(self.bus.bus_snoop(self.processor_number,address,value)):
                if(self.memory.status[self.cache.address] == "stale" and self.cache.state != "I" ):
                    self.memory.data[self.cache.address] = self.cache.value
                    self.memory.status[self.cache.address] = "fresh"

                self.memory.status[address] = "stale"
                self.cache.state = "E"
                self.cache.value = value
                self.cache.address = address

            else:
                self.memory.data[self.cache.address] = self.cache.value
                self.memory.status[self.cache.address] = "fresh"
                self.cache.state = "M"
                self.cache.value = value
                self.cache.address = address
                self.memory.status[address] = "stale"
        return

    def readInstruction(self,address):

        if (self.bus.read_bus_snoop(self.processor_number, address)):
            if(self.cache.state == "M"):
                self.memory.data[self.cache.address] = self.cache.value
                self.memory.status[self.cache.address] = "fresh"
            self.cache.state = "S"
            self.cache.address = address
            self.cache.value = self.memory.data[address]


        else:
            #if(self.cache.state == "M" or self.cache.state == "E"):
            if(self.cache.state == "M"):
                #110 102 - example#
                if(self.memory.status[self.cache.address] == "stale"):
                    self.memory.data[self.cache.address] = self.cache.value
                    self.memory.status[self.cache.address]  = "fresh"
                    self.cache.address = address
                    self.cache.value = self.memory.data[address]
                    self.cache.state = "E"
                return
            if(self.cache.state == "E"):
                self.cache.address = address
                self.cache.value = self.memory.data[address]
                return
            else:
                self.cache.state = "E"
                self.cache.address = address
                self.cache.value = self.memory.data[address]
        return



if __name__ == "__main__":
    print("Instruction format->\n"
          "write: processor_no,value,memory_block\n"
          "read:  processor_no,memory_block")
    print(" ")
    ad = admin()
    ad.printStatus()
    flag = 1
    print(" ")
    while(flag):
        print("instruction_type(read-0/write-1)")
        instruction_type_raw = input()
        instruction_type = int(instruction_type_raw)
        print("instruction:")
        if(instruction_type == 0) :
            processor_no,memory_block =map(int,input().split(','))
            ad.bus.instruction(processor_no, instruction_type, memory_block,0)
            ad.printStatus()
        else:
            processor_no,value, memory_block = map(int, input().split(','))
            ad.bus.instruction(processor_no, instruction_type, memory_block, value)
            ad.printStatus()
