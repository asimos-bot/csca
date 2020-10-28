#!/usr/bin/env python3
import sys
import os
import csv

class TimeSlot():

    def cast_to_bool(self, row, key):
        return bool(int(row[key]))

    def __init__(self, row):

        self.square = self.cast_to_bool(row, 'square')
        self.multiply = self.cast_to_bool(row, 'multiply')
        self.reduce = self.cast_to_bool(row, 'reduce')
        self.empty = not self.square and not self.multiply and not self.reduce

    def __eq__(self, other):

        if( isinstance(other, TimeSlot) ):

            return self.square == other.square and self.multiply == other.multiply and self.reduce == other.reduce
        return False

    def __repr__(self):

        l = []

        if( self.square ): l.append('S')
        if( self.multiply ): l.append('M')
        if( self.reduce ): l.append('R')

        return str(l)

class GPGCracker():

    def __init__(self, filename):

        self.sequence = []

        self.bits, self.bits_no_repetition = self.get_bits(filename)

    def get_bits(self, filename):

        with open(filename) as file:
            self.sequence = self.translate_csv(file)

        return self.translate_sequence(False), self.translate_sequence(True)

    def levensthein(self, list1, list2):

        matrix = [[0 for i in range(len(list2) + 1)] for i in range(len(list1) + 1)]

        for x in range(len(list1) + 1):
            matrix[x][0] = x

        for y in range(len(list2) + 1):
            matrix[0][y] = y

        for x in range(1, len(list1) + 1):
            for y in range(1, len(list2) + 1):
                if list1[x - 1] == list2[y - 1]:
                    matrix[x][y] = min(
                        matrix[x - 1][y] + 1,
                        matrix[x - 1][y - 1],
                        matrix[x][y - 1] + 1
                    )
                else:
                    matrix[x][y] = min(
                        matrix[x - 1][y] + 1,
                        matrix[x - 1][y - 1] + 1,
                        matrix[x][y - 1] + 1
                    )

        return matrix[len(list1)][len(list2)]

    def get_statistics(self):

        d = dict()

        m = min(len(self.bits), len(self.bits_no_repetition))
        d['hamming_distance'] = sum( [ self.bits[i] != self.bits_no_repetition[i] for i in range(m) ] )
        d['levensthein'] = self.levensthein(self.bits, self.bits_no_repetition)

        return d

    def __del__(self):

        if( hasattr(self,'file') and self.file ):

            self.file.close()

    def translate_csv(self, file):

        # put operations in a vector
        self.sequence=[]

        for row in csv.DictReader(file):

            self.sequence.append(TimeSlot(row))

        return self.sequence

    def potential_0(self, seq, idx, bits):

        slot = seq[idx]
        previous = seq[idx-1]

        if( slot.square ):

            if( slot.reduce ):

                if( slot.multiply and not previous.multiply ):
                    bits.append(1)
                    return 0, bits

                return 2, bits

            return 1, bits
        return 0, bits

    def potential_1(self, seq, idx, bits):

        slot = seq[idx]
        previous = seq[idx-1]

        if( slot.reduce ):

            if( slot.multiply ):

                bits.append(1)
                if( slot.square and not previous.square ):
                    return 1, bits
                return 0, bits

            return 2, bits

        return 1, bits

    def potential_2(self, seq, idx, bits):

        slot = seq[idx]
        previous = seq[idx-1]

        if( slot.multiply and not previous.multiply):

            if( slot.reduce ):
                bits.append(1)
                return 0, bits

            return 3, bits

        elif( slot.square ):

             if( not previous.square or ( previous.reduce and not slot.reduce ) ):
                bits.append(0)
                if( slot.reduce ):
                    return 2, bits
                return 1, bits

        return 2, bits

    def potential_3(self, seq, idx, bits):

        slot = seq[idx]
        previous = seq[idx-1]

        if( slot.reduce ):

            bits.append(1)

            if( slot.square and not previous.square ):

                return 1, bits
            return 0, bits
        return 3, bits

    def filter_translation_sequence(self, ignore_adjacent):

        seq = [ i for i in self.sequence ]

        for i in range(len(seq)-1, 0, -1):

            if( seq[i].empty ):
                del seq[i]
            elif( ignore_adjacent and seq[i] == seq[i-1] ):
                del seq[i]

        return seq

    def translate_sequence(self, ignore_adjacent=False):

        bits=[]
        potential_bit_size=0
        recent_empty_slots=0

        bit_ops = {

            0: self.potential_0,
            1: self.potential_1,
            2: self.potential_2,
            3: self.potential_3,
        }

        seq = self.filter_translation_sequence(ignore_adjacent)

        for slot_idx in range(1, len(seq)-1):

            potential_bit_size, bits = bit_ops[potential_bit_size](seq, slot_idx, bits)

        return bits

if( __name__ == "__main__" ):

    if( len(sys.argv) != 2 ):
        print("Expected use: python3 crack.py <csv with Square-Reduce-Multiply detections>")
        print("the csv file should have 'square', 'reduce' and 'multiply' fieldnames")
    else:
        cracker = GPGCracker(sys.argv[1])
        bits  = cracker.bits
        bits_no_repetition = cracker.bits_no_repetition

        d = cracker.get_statistics()
        for k in sorted(d.keys()):
            print(k, d[k])
