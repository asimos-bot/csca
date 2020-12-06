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

    #ubuntu
    #d=0x2bc0c551d685c79916b20742fcd986bd7b79e1b859c1e587095b300479ece8dff833a480985cb3849d74663cb8a867eb434015db0f2da675eef9a9df3fe9b0938759ae0301c9328ca92c176a2ee86c6d23707d878cfa6f703493c37400a8dc67e601c8fa91207d6a82f48823503c9b9acbb2b2c19cdfbcd0d3fa9a8d4dffe98d0bf68fd3234a935d1e90e9904598ac8f51c4378a10caafff3f4d48ddfcf3ae764524c0b252dfac6f4d76120b63861d95eaef64e4607263069cfef677da289dd2b1b5ebface5a275a770d6d062ac33e373c3becd9a29feceeef106102dfa0e7820023e158bb2c613860caedd839710f830aa9d47f1c08030b6f4aebc09d4349c1
    #2048
    #d=0x56a325fcdd434d3d9c1d1519271ad9ffcfbbb0cac2164ae67761293d8a2a743beb3619fe41a8dec22fcc7193acdd1898fb0b1194e41a8349dd8a38d27b25ee134921c449616013034766959c0c70772fe5e524e9d087441ab391b782b98f843199f78b5ad1e7605e647a73ea27c8591fbf7154d36a7af3470ca76424338b3dff63f8f36c54e12524a191d9b101db83b317fd2990c35f126bc359f0c3d1bc558c0d09310bad349ae7775326357d42bbbbcf022abd095bb5c1ddf4ee9f9fab0b8b034c540cfde1701be844e1a8efc6c1c522b0a1494ad68ac5ffafd11a177e4fd726eaf297ff18cf3da0fc486d6647114e632657a66464a3e49e8835b6d6649da9
    d=0x0f36e696eacaeb391658a1900ce0ee671cf9c64e17f6ca90db0127936d7565783bca2e4378fd812084db5969657c431e11d43848bb4531459ff31af83e7b73921333b6e0c4ed09d15ef1186fec36782116c5e4792f3d374df5b72d38ef10c7458d065941b63662434fbd1b51cf02ff50c152f794d281b836591b8673a3bee4e1
    #ubuntu
	#q=0xfa3af4db32dbc5e832d16702b5e69f6a2de99137e1000727a43fdbf30bdd4edade9271096263bcecbe9cd826bd9a7011e09fa1e417b1168b22b3d1334ef6cd6bdb3e8af4a397fbe71553fed85ee10c3981923c457be89ce0da8a44d3c04b096c2346c29fd634630c6b636ba38572b13075f94e7d4a70b76f9fbc92409a5a698b
    #2048
    #q=0xefc8623bb22fe5d1b7e7a1f9e059738450dd6243a29d5911252efdc7153abbb7e3cd1a81510e776ee15bdcee672112963cc6b44441e4c4ed93c8348314879cb6e9443141b10b46ba41fbbb6b31ab48f6025f3c8936fe2d3d44fa6430c484533afe00e9d7e719a8c8fd2d56e409050c25be41c934cf58f08a5234badf49c1c59f
    q=0xdcb64d059b611dbba2e8aafc83c8042de69d551ae692329e5f27af26c72a9e60559807f7f9177dbdad1df82d6fa5944ce9c0dcde38d03e47731fb7d5bfca1efd
    #ubuntu
	#p=0xc918077010717cffdab8e8d2936401e3b69206f62b35d0f5fe9a3b1bd54fcfe85da988cb97cd6c8b611112eb3a04d71ff3c94dd71713cb43dc699bf8fbd02bd38bce7f382042462acfcb6242c406830a1a4a9cdc65e2de42bfbab131a72ca81d85ef335577d17c6f47a30c09adecf5868bea4000dd2187fd6251d5f362189229
    #2048
    #p=0xe7009f96bb93846ed6b6d50202557fe8f2ac5598729493014344c8898404117848c3c213c025157053a347352685e9c7b59dd298ff36487825f91e15cecca407d56917c4059ab259a5e310458e8d47c43325b4e65808253da54a147fb74c1e927c8cc7d733194655ea2a49fce16a6e394bec52064c09ded872e6dd34ea3824f7
    p=0xc2278bd426d455b27f7f087dba93a846008125c66f6e5a53484633e792aa6a5a2f22a8b48732b014e01359bfdeeb0734b5845321ecdbbe3968623c98f5b26461
    def __init__(self, filename):

        self.sequence = []

        self.bits, self.bits_no_repetition = self.get_bits(filename)

        self.dp = GPGCracker.d % (GPGCracker.p-1)
        self.dq = GPGCracker.d % (GPGCracker.q-1)

        self.dp = [x for x in '{:0{size}b}'.format(self.dp,size=512)]
        self.dq = [x for x in '{:0{size}b}'.format(self.dq,size=512)]

    def get_bits(self, filename):

        with open(filename) as file:
            self.sequence = self.translate_csv(file)

        return self.translate_sequence(True), self.translate_sequence(True)

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

    def LCS(self, s1, s2):
        #https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Longest_common_substring#Python
        m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
        longest, x_longest = 0, 0
        for x in range(1, 1 + len(s1)):
            for y in range(1, 1 + len(s2)):
                if s1[x - 1] == s2[y - 1]:
                    m[x][y] = m[x - 1][y - 1] + 1
                    if m[x][y] > longest:
                        longest = m[x][y]
                        x_longest = x
                else:
                    m[x][y] = 0
        return s1[x_longest - longest: x_longest], x_longest - longest, x_longest - 1

    def get_statistics(self):

        d = dict()

        m = min(len(self.bits), len(self.bits_no_repetition))
        d['bits_len'] = len(self.bits)
        d['bits_no_repetition_len'] = len(self.bits_no_repetition)
        #d['bits'] = ''.join(map(lambda x: str(x), self.bits))
        #d['bits_no_repetition'] = ''.join(map(lambda x: str(x), self.bits_no_repetition))
        d['hamming_distance'] = sum( [ self.bits[i] != self.bits_no_repetition[i] for i in range(m) ] )
        d['levensthein'] = self.levensthein(self.bits, self.bits_no_repetition)

        factor_bits = self.bits

        dp_bits = factor_bits[:512]
        dq_bits = factor_bits[512:]

        print(''.join(map(str,dp_bits)))
        print(''.join(self.dp))

        dp_LCS, dp_begin, dp_end = self.LCS(self.dp, dp_bits)
        dq_LCS, dq_begin, dq_end = self.LCS(self.dq, dq_bits)
        d['LCS_dp'] = ''.join(dp_LCS)
        d['LCS_begin_dp'] = dp_begin
        d['LCS_end_dp'] = dp_end
        d['LCS_dq'] = ''.join(dq_LCS)
        d['LCS_begin_dq'] = dq_begin
        d['LCS_end_dq'] = dq_end
        d['levensthein_dp'] = self.levensthein(self.dp, dp_bits)
        d['levensthein_dq'] = self.levensthein(self.dq, dq_bits)

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

            if( slot.reduce and not ( previous.square and previous.reduce ) ):
                return 2, bits

                if( slot.multiply and not previous.multiply ):
                    bits.append('1')
                    return 0, bits

            return 1, bits
        return 0, bits

    def potential_1(self, seq, idx, bits):

        slot = seq[idx]
        previous = seq[idx-1]

        if( slot.reduce ):

            if( slot.multiply ):

                bits.append('1')
                if( slot.square and not previous.square ):
                    return 1, bits
                return 0, bits

            if( slot.square and not previous.square ):
                bits.append('0')
                return 0, bits
            return 2, bits

        return 1, bits

    def potential_2(self, seq, idx, bits):

        slot = seq[idx]
        previous = seq[idx-1]

        if( slot.multiply and not previous.multiply):

            bits.append('1')
            if( slot.square and not previous.square ):
                return 1, bits
            return 0, bits

        elif( slot.square ):

             if( not previous.square or ( previous.reduce and not slot.reduce ) ):
                bits.append('0')
                if( slot.reduce ):
                    return 2, bits
                return 1, bits

        elif( slot.empty ):

            bits.append('0')
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

        for i in range(len(seq)-1, -1, -1):

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

        return bits #self._to_binary(seq)

    def _to_binary(self, time_slots):

        # We're building a state machine here
        START = 0
        AFTER_SQUARE = 1
        AFTER_SQUARE_MOD = 2
        AFTER_MULTIPLY = 3
        AFTER_SQUARE_MOD_EMPTY = 5

        current_state = START
        output = []
        modulo_count = 0
        for time_slot in time_slots:
            square = time_slot.square
            modulo = time_slot.reduce
            multiply = time_slot.multiply

            if current_state == START:
                modulo_count = 0
                if time_slot.empty:
                    continue

                # If we see a multiply, then we don't know what we're looking at.
                if multiply:
                    output.append('_')

                # Only advance if we see a square
                elif square and not multiply:
                    current_state = AFTER_SQUARE

            elif current_state == AFTER_SQUARE:
                # Could end up missing a modulo here
                # If we miss a slot, we probably won't see another square
                if time_slot.empty:
                    current_state = AFTER_SQUARE_MOD

                # If we see a multiply so soon after square, it might be invalid
                if multiply:
                    current_state = START
                    output.append('_')

                # Stay if we see another square. Advance if we only see a modulo.
                elif not square and modulo:
                    current_state = AFTER_SQUARE_MOD

            elif current_state == AFTER_SQUARE_MOD:
                if time_slot.empty:
                    current_state = AFTER_SQUARE_MOD_EMPTY

                # If we see both square and multiply, it might be invalid
                elif square and multiply:
                    current_state = START
                    output.append('_')

                # If we see a square, return to start and output a 0
                elif square:
                    current_state = START
                    output.append('0')

                elif multiply:
                    current_state = AFTER_MULTIPLY

                elif modulo:
                    modulo_count += 1

            elif current_state == AFTER_SQUARE_MOD_EMPTY:
                if time_slot.empty:
                    continue

                # We missed only a modulo
                if multiply:
                    current_state = AFTER_MULTIPLY

                elif modulo:
                    modulo_count += 1

                elif square:
                    current_state = START
                    # If we've seen three modulos already, might be worth marking
                    # this as unknown
                    if modulo_count >= 3:
                        output.append('?')
                    else:
                        # Otherwise, we probably didn't really miss anything
                        # important
                        output.append('0')

            elif current_state == AFTER_MULTIPLY:
                # If we see only a modulo, return to start and output a 1
                # Alternatively, a missed slot could be a modulo
                if time_slot.empty or (modulo and not square and not multiply):
                    current_state = START
                    output.append('1')

                # If we see a square so soon, this might be invalid
                elif square:
                    current_state = START
                    output.append('_')

        return output

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

        #print(''.join(map(str, cracker.bits)))
