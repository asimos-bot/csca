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

    d=0x2bc0c551d685c79916b20742fcd986bd7b79e1b859c1e587095b300479ece8dff833a480985cb3849d74663cb8a867eb434015db0f2da675eef9a9df3fe9b0938759ae0301c9328ca92c176a2ee86c6d23707d878cfa6f703493c37400a8dc67e601c8fa91207d6a82f48823503c9b9acbb2b2c19cdfbcd0d3fa9a8d4dffe98d0bf68fd3234a935d1e90e9904598ac8f51c4378a10caafff3f4d48ddfcf3ae764524c0b252dfac6f4d76120b63861d95eaef64e4607263069cfef677da289dd2b1b5ebface5a275a770d6d062ac33e373c3becd9a29feceeef106102dfa0e7820023e158bb2c613860caedd839710f830aa9d47f1c08030b6f4aebc09d4349c1
    q=0xfa3af4db32dbc5e832d16702b5e69f6a2de99137e1000727a43fdbf30bdd4edade9271096263bcecbe9cd826bd9a7011e09fa1e417b1168b22b3d1334ef6cd6bdb3e8af4a397fbe71553fed85ee10c3981923c457be89ce0da8a44d3c04b096c2346c29fd634630c6b636ba38572b13075f94e7d4a70b76f9fbc92409a5a698b
    p=0xc918077010717cffdab8e8d2936401e3b69206f62b35d0f5fe9a3b1bd54fcfe85da988cb97cd6c8b611112eb3a04d71ff3c94dd71713cb43dc699bf8fbd02bd38bce7f382042462acfcb6242c406830a1a4a9cdc65e2de42bfbab131a72ca81d85ef335577d17c6f47a30c09adecf5868bea4000dd2187fd6251d5f362189229

    def __init__(self, filename):

        self.sequence = []

        self.bits, self.bits_no_repetition = self.get_bits(filename)

        self.dp = GPGCracker.d % (GPGCracker.p-1)
        self.dq = GPGCracker.d % (GPGCracker.q-1)

        self.dp = [x for x in '{:0{size}b}'.format(self.dp,size=1024)]
        self.dq = [x for x in '{:0{size}b}'.format(self.dq,size=1024)]

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

        dp_bits = factor_bits[:1024]
        dq_bits = factor_bits[1024:]

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

            if( slot.reduce ):
                return 2, bits

                if( slot.multiply ):
                    bits.append(1)
                    return 0, bits
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

            if( slot.square and not previous.square ):
                bits.append(0)
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

        """
        for slot_idx in range(1, len(seq)-1):

            potential_bit_size, bits = bit_ops[potential_bit_size](seq, slot_idx, bits)
        """

        return self._to_binary(seq)

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

        print(''.join(map(str, cracker.bits)))
