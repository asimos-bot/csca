#!/usr/bin/env python3
import sys
import csv

class TimeSlot():

    def cast_to_bool(self, row, key):
        return bool(int(row[key]))

    def __init__(self, row):

        self.square = self.cast_to_bool(row, 'square')
        self.multiply = self.cast_to_bool(row, 'multiply')
        self.reduce = self.cast_to_bool(row, 'reduce')
        self.empty = not self.square and not self.multiply and not self.reduce

    def __repr__(self):

        l = []

        if( self.square ): l.append('S')
        if( self.multiply ): l.append('M')
        if( self.reduce ): l.append('R')

        return str(l)

class GPGCracker():

    def __init__(self, filename):

        self.file = open(filename)

        self.sequence = self.translate_csv()

        self.bits = []

    def __del__(self):

        if( hasattr(self,'file') and self.file ):

            self.file.close()

    def translate_csv(self):

        # put operations in a vector
        self.sequence=[]

        for row in csv.DictReader(self.file):

            self.sequence.append(TimeSlot(row))

        return self.sequence

    def potential_0(self, idx):

        slot = self.sequence[idx]
        previous = self.sequence[idx-1]
        next = self.sequence[idx+1]

        if( slot.square ):

            if( slot.reduce ):

                if( slot.multiply and not previous.multiply ):
                    self.bits.append(1)
                    return 0

                if( not next.square ):
                    self.bits.append(0)
                    return 0

                return 2
            return 1
        return 0

    def potential_1(self, idx):

        slot = self.sequence[idx]
        previous = self.sequence[idx-1]
        next_slot = self.sequence[idx+1]

        if( slot.reduce ):

            if( slot.multiply and not previous.multiply ):
                self.bits.append(1)
                return 0

            elif( not slot.square and next_slot.square):
                self.bits.append(0)
                return 0
            return 2
        return 1

    def potential_2(self, idx):

        slot = self.sequence[idx]
        previous = self.sequence[idx-1]

        if( slot.multiply ):

            if( slot.reduce ):

                self.bits.append(1)
                return 0

            return 3

        elif( slot.square and not previous.square):

            self.bits.append(0)
            return 1

        return 2

    def potential_3(self, idx):

        slot = self.sequence[idx]

        if( slot.reduce ):

            self.bits.append(1)

            if( slot.square ):

                return 1
            return 0
        return 3

    def translate_sequence(self):

        self.bits=[]
        potential_bit_size=0
        recent_empty_slots=0

        bit_ops = {

            0: self.potential_0,
            1: self.potential_1,
            2: self.potential_2,
            3: self.potential_3,
        }

        for slot_idx in range(len(self.sequence)):

            # don't allow more than one empty slot in a sequence
            # of a potential bit
            if( not self.sequence[slot_idx] ):

                recent_empty_slots+=1

                if( recent_empty_slots == 2 ):
                    recent_empty_slots = potential_bit_size = 0
                    continue

            elif( slot_idx != len(self.sequence) - 1 ):

                potential_bit_size = bit_ops[potential_bit_size](slot_idx)

        return self.bits

if( __name__ == "__main__" ):

    if( len(sys.argv) != 2 ):
        print("Expected use: python3 crack.py <csv with Square-Reduce-Multiply detections>")
        print("the csv file should have 'square', 'reduce' and 'multiply' fieldnames")
    else:
        cracker = GPGCracker(sys.argv[1])
        print(cracker.sequence)
        bits = cracker.translate_sequence()
        print(bits)

        print(len(bits))
        print(bits.count(1)/len(bits))
        print(bits.count(0)/len(bits))
