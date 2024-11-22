import pygame, sys, csv, math, time, os
from scripts.states import GamePlay, Results
from scripts.key import Key
from scripts.utils import days

class TypingGame:
    RETAINING_FAC = .75             # the higher the value, the less the game tend to "forget" the weights and distribute them more evenly
    TIMEREVENT = pygame.USEREVENT + 1
    W_INCREMENT_FAC = 1.05

    def __init__(self, window_width=1280, window_height=720, goal_wpm = 60):
        pygame.display.set_caption("typing game")
        self.window_width = window_width
        self.window_height = window_height
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.clock = pygame.time.Clock()

        self.states = []
        self.load_states()
        self.load_asset()

        self.actions = {'start_typing':False, 'playing':True, 'results':False, 'target-response':None, 'restart':False}

        self.goal_wpm = goal_wpm

    def game_loop(self):
        while True:
            self.get_event()
            self.update(self.actions)
            self.render()
    
    def get_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_progress()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.actions['restart'] = True
                elif event.key == pygame.K_TAB:
                    self.actions['results'] = not(self.actions['results'])
                    self.actions['playing'] = not(self.actions['playing'])
                elif isinstance(self.states[-1], GamePlay):
                    self.actions['target-response'] = (self.keys[self.states[-1].current_char_pos].value, pygame.key.name(event.key))

    def update(self, actions=None):
        self.states[-1].update(actions)
        self.actions['target-response'] = None

    def render(self):
        self.screen.fill((50,50,55))
        self.states[-1].render()
        pygame.display.flip()

    def load_states(self):
        # self.results = Results(self, goal_wpm=60)
        self.states.append(GamePlay(self, 'alpha'))

    def load_asset(self):
        # load the keys to pass to GamePlay and Results
        self.fonts = {
            'GamePlay' : pygame.font.SysFont('consolas', 144, bold=False, italic=False),
            'primary_criteria' : pygame.font.SysFont('consolas', 20, bold=False, italic=True),
            'main_figure' : pygame.font.SysFont('consolas', 32, bold=True, italic=True),
            'goal_line' : pygame.font.SysFont('consolas', 16, bold=True, italic=True),
            'bars' : pygame.font.SysFont('consolas', 16, bold=False, italic=False)
        }

        self.keys = []
        with open('user_data/alpha.csv') as file:
            for line in csv.DictReader(file):
                self.keys.append(Key(line['value'], line['finger'], line['shift'], line['weight']))
        self._weight_flatten()

    def save_progress(self):
        self._regularize_weight()

        with open('user_data/alpha.csv', 'w', newline="") as file:
            fieldnames = ['value', 'finger', 'shift', 'weight']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for key in self.keys:
                writer.writerow({'value':key.value, 'finger':key.finger, 'shift':key.shift, 'weight':key.weight})

        with open('user_data/time_record.txt','w') as file:
            file.write(str(int(time.time())))

    def _weight_flatten(self):
        with open('user_data/time_record.txt') as file:
           last_session_end = int(file.read())
        current_session_start = int(time.time())
        off_time = current_session_start - last_session_end

        flatten_fac = GamePlay.RETAINING_FAC/(GamePlay.RETAINING_FAC + days(off_time))

        weight_logs = [int(math.log(int(key.weight)/Key.INITIAL_WEIGHT, TypingGame.W_INCREMENT_FAC)) for key in self.keys]
        for i in range(len(self.keys)):
            self.keys[i].weight = \
                int(Key.INITIAL_WEIGHT * (TypingGame.W_INCREMENT_FAC ** int(weight_logs[i] * flatten_fac)))
    
    def _regularize_weight(self):
        weight_logs = [int(math.log(int(key.weight)/Key.INITIAL_WEIGHT, TypingGame.W_INCREMENT_FAC)) for key in self.keys]
        min_log = min(weight_logs)
        for i in range(len(self.keys)):
            self.keys[i].weight = \
                int(Key.INITIAL_WEIGHT * (TypingGame.W_INCREMENT_FAC ** (weight_logs[i] - min_log)))
    
TypingGame().game_loop()