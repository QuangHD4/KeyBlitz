import csv
import pygame
import time, sys, random, math
class Key:

    INITIAL_WEIGHT = 100
    

    def __init__(self, value, finger, shift:bool, weight, reflex_adj_threshold=167, inaccuracy_adj_threshold=5, weight_increment = 1.05):
        self.value = value
        self.finger = finger
        self.shift = shift

        self.error = 0
        self.total = 0

        self.REFLEX_ADJ_THRESHOLD = reflex_adj_threshold        # in miliseconds
        self.avg_reflex_time = 571

        self.INACCURACY_ADJ_THRESHOLD = inaccuracy_adj_threshold
        self.WEIGHT_INCREMENT = weight_increment
        self.weight = weight

    def update(self, key_state:bool, reflex_time):
        '''
        update total key hits and errors (if key_state=False) and calculate error rate;
        if error rate reaches a certain number of intervals, increase weight accordingly

        key_state :   True if the key was pressed correctly, False otherwise
        '''
        self.avg_reflex_time = (self.avg_reflex_time * self.total + reflex_time)/(self.total + 1)
        
        self.error += (1 - key_state)
        self.total += 1

        self._weight_adjust()

    def _weight_adjust(self):
        fac = int(self.avg_reflex_time // self.REFLEX_ADJ_THRESHOLD)
        fac *= int((self.error / self.total) // self.INACCURACY_ADJ_THRESHOLD)
        self.weight = int((Key.INITIAL_WEIGHT * self.WEIGHT_INCREMENT**fac))

    def _reset_data(self):
        self.weight = Key.INITIAL_WEIGHT

"""game = True
while game:
    #Load menu, components, loop wait for button click(advance to game, game mode), calculate off-game time -> adjust weight

    Game(game_mode='alpha'|'I'|'II'|'III'|'IV'|'V'|'VI'|'VII', test_time=60).run()
    #load resources for game mode, display game screen, gameplay, display results/score, analysis, update weight, return to menu, restart, bgm
"""