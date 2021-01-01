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

        self.sequence = self.get_sequence(filename)
        self.bits_original = self.get_bits("original")
        self.bits_plunger = self.get_bits("plunger")

    def get_sequence(self, filename):

        with open(filename) as file:
            seq = self.translate_csv(file)
            return seq

    def __del__(self):

        if( hasattr(self,'file') and self.file ):

            self.file.close()

    def translate_csv(self, file):

        # put operations in a vector
        sequence=[]

        for row in csv.DictReader(file):

            sequence.append(TimeSlot(row))

        return sequence

    def potential_0(self, seq, idx, bits):

        slot = seq[idx]
        previous = seq[idx-1]

        if( slot.square ):

            if( slot.reduce and not ( previous.square and previous.reduce ) ):
                return 2, bits
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

    def filter_translation_sequence(self):

        seq = [ i for i in self.sequence ]

        for i in range(len(seq)-1, -1, -1):

            if( seq[i].empty ):
                del seq[i]
            elif( seq[i] == seq[i-1] ):
                del seq[i]

        return seq

    def get_bits(self, encoding_alg):

        bits=[]
        potential_bit_size=0
        recent_empty_slots=0

        bit_ops = {

            0: self.potential_0,
            1: self.potential_1,
            2: self.potential_2,
            3: self.potential_3,
        }

        seq = self.filter_translation_sequence()

        if( encoding_alg=="plunger" ):

            return ''.join(self._to_binary(seq))

        else:

            for slot_idx in range(1, len(seq)-1):

                potential_bit_size, bits = bit_ops[potential_bit_size](seq, slot_idx, bits)

            return ''.join(bits) #self._to_binary(seq)

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

        d = {"plunger": cracker.bits_plunger, "original": cracker.bits_original}
        fieldnames = d.keys()
        has_header = os.path.exists("scripts/bits.csv")

        with open("scripts/bits.csv", "a") as file:

            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if( not has_header ): writer.writeheader()

            writer.writerow(d)

        #print(''.join(map(str, cracker.bits)))
