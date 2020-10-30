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

    def get_dq_correctness(self, bits):

        q=0xefc8623bb22fe5d1b7e7a1f9e059738450dd6243a29d5911252efdc7153abbb7e3cd1a81510e776ee15bdcee672112963cc6b44441e4c4ed93c8348314879cb6e9443141b10b46ba41fbbb6b31ab48f6025f3c8936fe2d3d44fa6430c484533afe00e9d7e719a8c8fd2d56e409050c25be41c934cf58f08a5234badf49c1c59f
        d=0x56a325fcdd434d3d9c1d1519271ad9ffcfbbb0cac2164ae67761293d8a2a743beb3619fe41a8dec22fcc7193acdd1898fb0b1194e41a8349dd8a38d27b25ee134921c449616013034766959c0c70772fe5e524e9d087441ab391b782b98f843199f78b5ad1e7605e647a73ea27c8591fbf7154d36a7af3470ca76424338b3dff63f8f36c54e12524a191d9b101db83b317fd2990c35f126bc359f0c3d1bc558c0d09310bad349ae7775326357d42bbbbcf022abd095bb5c1ddf4ee9f9fab0b8b034c540cfde1701be844e1a8efc6c1c522b0a1494ad68ac5ffafd11a177e4fd726eaf297ff18cf3da0fc486d6647114e632657a66464a3e49e8835b6d6649da9

        dq = d % (q-1)

        dq = [int(x) for x in '{:0{size}b}'.format(dq,size=1024)]

        return sum([ dq[i] == bits[i] for i in range(min(len(bits), len(dq))) ])

    def get_dp_correctness(self, bits):

        p=0xe7009f96bb93846ed6b6d50202557fe8f2ac5598729493014344c8898404117848c3c213c025157053a347352685e9c7b59dd298ff36487825f91e15cecca407d56917c4059ab259a5e310458e8d47c43325b4e65808253da54a147fb74c1e927c8cc7d733194655ea2a49fce16a6e394bec52064c09ded872e6dd34ea3824f7
        d=0x56a325fcdd434d3d9c1d1519271ad9ffcfbbb0cac2164ae67761293d8a2a743beb3619fe41a8dec22fcc7193acdd1898fb0b1194e41a8349dd8a38d27b25ee134921c449616013034766959c0c70772fe5e524e9d087441ab391b782b98f843199f78b5ad1e7605e647a73ea27c8591fbf7154d36a7af3470ca76424338b3dff63f8f36c54e12524a191d9b101db83b317fd2990c35f126bc359f0c3d1bc558c0d09310bad349ae7775326357d42bbbbcf022abd095bb5c1ddf4ee9f9fab0b8b034c540cfde1701be844e1a8efc6c1c522b0a1494ad68ac5ffafd11a177e4fd726eaf297ff18cf3da0fc486d6647114e632657a66464a3e49e8835b6d6649da9

        dp = d % (p-1)

        dp = [int(x) for x in '{:0{size}b}'.format(dp,size=1024)]

        return sum([ dp[i] == bits[i] for i in range(min(len(bits), len(dp))) ])

    def get_statistics(self):

        d = dict()

        m = min(len(self.bits), len(self.bits_no_repetition))
        d['bits_len'] = len(self.bits)
        d['bits_no_repetition_len'] = len(self.bits_no_repetition)
        d['bits'] = ''.join(map(lambda x: str(x), self.bits))
        d['bits_no_repetition'] = ''.join(map(lambda x: str(x), self.bits_no_repetition))
        d['hamming_distance'] = sum( [ self.bits[i] != self.bits_no_repetition[i] for i in range(m) ] )
        d['levensthein'] = self.levensthein(self.bits, self.bits_no_repetition)

        d['correctness_dq'] = self.get_dq_correctness(self.bits[:1024])
        d['correctness_dp'] = self.get_dp_correctness(self.bits[1024:])

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

        d = cracker.get_statistics()
        fieldnames = sorted(d.keys())[::-1]
        has_header = os.path.exists("scripts/bits.csv")

        with open("scripts/bits.csv", "a") as file:

            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if( not has_header ): writer.writeheader()

            writer.writerow(d)
