import random, pygame, math, sys, csv, time, copy
from . import utils

class State:
    def __init__(self, game) -> None:
        self.game = game
        self.prev_state = None

    def update(self):
        pass

    def render(self):
        pass

    def enter_state(self):
        if len(self.game.states) > 1:
            self.prev_state = self.game.states[-1]
        self.game.states.append(self)
    
    def exit_state(self):
        self.game.states.pop()

class Results(State):
    RETAINING_FAC = .75             # the higher the value, the less the game tend to "forget" the weights and distribute them more evenly

    def __init__(self, game, goal_wpm=60):
        super().__init__(game)
        pygame.init()

        '''pygame.display.set_caption("typing game")
        # pygame.display.set_icon()
        self.window_width = window_width
        self.window_height = window_height
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))

        self.clock = pygame.time.Clock()'''

        self.fonts={
            'primary_criteria' : pygame.font.SysFont('consolas', 20, bold=False, italic=True),
            'main_figure' : pygame.font.SysFont('consolas', 32, bold=True, italic=True),
            'goal_line' : pygame.font.SysFont('consolas', 16, bold=True, italic=True),
            'bars' : pygame.font.SysFont('consolas', 16, bold=False, italic=False)
        }
        self.graph = Graph(self.game)
    
    def update(self, actions):
        if actions['playing']:
            self.exit_state()
            GamePlay(self.game, 'alpha').enter_state()
            self.game.states[-1].update(actions)

    def render(self):
        self.graph.draw()

class Graph:
    def __init__(self, game, side_margin=125, top_margin=125):
        self.keys = game.keys
        self.display_surface = game.screen
        self.label_font = pygame.font.SysFont('consolas', 16, bold=False, italic=False)

        self.side_margin = side_margin            # horizontal margin - px
        self.top_margin = top_margin            # in px

        self.area_width = game.window_width - 2 * self.side_margin
        self.area_height = game.window_height / 2 - self.top_margin

        space_proportions = .3
        self.space_between_cols = self.area_width * space_proportions/ (len(self.keys)-1)
        self.col_width = int(self.area_width *(1-space_proportions)/ (len(self.keys)))

        # if you want to change constants like avg_word_len(7) or time allowance(4), change the goal_line_text var in self.draw() to match
        self.goal_reflex_time = 60*4 / (game.goal_wpm * 7) * 1000           # 7 is assumed the avg len of a word (including space); 240 = 60*4(=round(avg_word_len/2))(extra time allowance since this measure the reflex time of one key at a time rather than a whole paragraph)

        reflex_time_table = [char.avg_reflex_time for char in game.keys]
        reflex_time_table.append(self.goal_reflex_time)

        self.max_reflex_time = max(reflex_time_table)
    
    def draw(self):

        # draw columns with respective labels
        for i, char in enumerate(self.keys):
            col_height = int(char.avg_reflex_time / self.max_reflex_time * self.area_height)
            col_bottom_center = (
                int(self.side_margin + self.col_width/2 + i*(self.col_width+self.space_between_cols)), 
                int(self.top_margin + self.area_height)
            )

            if char.avg_reflex_time > self.goal_reflex_time:
                self._draw_column(self.display_surface, (245,160,160), col_bottom_center, col_height)
                self._draw_letter_under_col(char, col_bottom_center, (245,160,160))
            else:
                self._draw_column(self.display_surface, (127,127,127), col_bottom_center, col_height)
                self._draw_letter_under_col(char, col_bottom_center, (127,127,127))

        self._draw_goal_line()

    def _draw_letter_under_col(self, char, col_bottom_center:tuple, color):
        rendered = self.label_font.render(char.value, 1, color)
        char_rect = rendered.get_rect(center=(col_bottom_center[0], col_bottom_center[1] + rendered.get_rect().h))
        self.display_surface.blit(rendered, (char_rect.x, char_rect.y))

    def _draw_column(self, display_surface, color, col_bottom_center:tuple, col_height):
        pygame.draw.line(
            display_surface, 
            color, 
            (col_bottom_center[0], col_bottom_center[1] - col_height), 
            col_bottom_center,
            width=self.col_width
        )

    def _draw_goal_line(self):
        line_width = 3
        text_offset = 7
        text = self.label_font.render(f'Goal: {int(240000/(self.goal_reflex_time*7))} wpm', 1, (242,183,14))
        line_height = self.goal_reflex_time / self.max_reflex_time * self.area_height

        # draw semi_transparent, rounded background to annotate the goal line
        # using draw.rect for rounding corner and then converting to Surface for transparency
        text_bg = self._draw_transparent_rounded_rect(
            text.get_width() + 2*text_offset,
            text.get_height() + 2*text_offset,
            self.display_surface,
            (self.side_margin-10, math.ceil(self.area_height + self.top_margin - line_height + 2*line_width)),
            border_bottom_left_radius=7,
            border_bottom_right_radius=7,
            alpha=150
        )

        self._draw_transparent_rounded_rect(
            self.area_width + 10 + 1.5*line_width,
            line_width * 3,
            self.display_surface,
            (self.side_margin-10-2*line_width, math.floor(self.area_height + self.top_margin - line_height - line_width/2)),
            border_radius = line_width,
            alpha=150
        )
        
        self._draw_horizontal_dashed_line(
            self.display_surface, 
            (242,183,14), 
            (self.side_margin-10, self.area_height + self.top_margin - line_height), 
            self.area_width, 
            intervals_num = 50, 
            space_percent = .3, 
            width=line_width
        )

        # blit goal_line_text
        text_center = text.get_rect(center=text_bg.center)
        self.display_surface.blit(text, (text_center.x, text_center.y))

    def _draw_horizontal_dashed_line(self, surface, color, start_center_pos, line_length, intervals_num:int, space_percent:float=1, width:int = 4):
        dash_len = line_length * (1-space_percent) / (intervals_num + 1)
        space_len = line_length * space_percent / intervals_num

        for i in range(intervals_num + 1):
            pygame.draw.rect(
                surface, 
                color, 
                (int(start_center_pos[0] + i*(dash_len + space_len)), int(start_center_pos[1] + width/2), int(dash_len), width), 
                border_radius=int(width/2)
            )

    def _draw_transparent_rounded_rect(self, width, height, destination_surface:pygame.Surface, coordinates:tuple, border_radius:int=-1, border_top_left_radius:int =-1, border_top_right_radius:int =-1, border_bottom_left_radius:int =-1, border_bottom_right_radius:int =-1, alpha = 255):
        temp_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(
            temp_surf, 
            pygame.Color(30,30,30), 
            (0, 0, width, height),
            border_radius = border_radius,
            border_top_left_radius = border_top_left_radius,
            border_top_right_radius = border_top_right_radius,
            border_bottom_left_radius = border_bottom_left_radius,
            border_bottom_right_radius = border_bottom_right_radius,
        )
        temp_surf.set_alpha(alpha)
        return destination_surface.blit(temp_surf, coordinates)
    
class GamePlay(State):
    RETAINING_FAC = .75             # the higher the value, the less the game tend to "forget" the weights and distribute them more evenly
    TIMEREVENT = pygame.USEREVENT + 1

    def __init__(self, game, game_mode:str, window_width=1280, window_height=720, repetitionNum = 6, font_size = 144, timer = 30):
        super().__init__(game)
        pygame.init()

        '''pygame.display.set_caption("typing game")
        # pygame.display.set_icon()
        self.window_width = window_width
        self.window_height = window_height
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))

        self.clock = pygame.time.Clock()'''

        self.game_mode = game_mode
        self.W_INCREMENT_FAC = 1.05

        self.font = pygame.font.SysFont('consolas', font_size, bold=False, italic=False)
        '''self.game.keys = []
        with open('user_data/' + self.game_mode + '.csv') as file:
            for line in csv.DictReader(file):
                self.game.keys.append(Key(line['value'], line['finger'], line['shift'], line['weight']))
        self._weight_flatten()'''

        self.PRACTICE_PATTERN = self._generate_practice_pattern(repetitionNum=repetitionNum)
        self.practice_patterns = {}
        self.key_pair_pending = False
        self.pending_key_id = -1

        self.current_char_pos = None
        self.rendered_char = None
        self.char_rect = None
        self.current_key_pair = None
        self.wait_for_user_key = False

        self.reflex_time = 0

        self.running = True
        self.timer = timer
        pygame.time.set_timer(GamePlay.TIMEREVENT, 1000)

    '''def run(self):
        #background = pygame.image.load("")
        while self.running:
            
            # fill the screen with a color to wipe away anything from last frame
            self.screen.fill((50,50,55))
            
            if not self.wait_for_user_key:
                self.current_char_pos = self.pick_next_key()
                self.rendered_char = self.font.render(self.game.keys[self.current_char_pos].value,True,(127,127,127))
                self.char_rect = self.rendered_char.get_rect(center=(self.window_width/2, self.window_height/2))

                self.wait_for_user_key = True

            self.screen.blit(self.rendered_char, (self.char_rect.x, self.char_rect.y))

            # print(self.practice_patterns)

            reflex_start = int(time.time() * 1000)

            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if (input := pygame.key.name(event.key)) == self.game.keys[self.current_char_pos].value:
                        reflex_end = int(time.time() * 1000)
                        self.update_key(self.current_char_pos, True, reflex_end - reflex_start)

                        self.rendered_char = self.font.render(self.game.keys[self.current_char_pos].value,True,(255,255,255))
                        self.screen.blit(self.rendered_char, (self.char_rect.x, self.char_rect.y))

                        self.wait_for_user_key = False
                    else:
                        self.add_practice_keys(tuple(sorted((self.current_char_pos, input_to_pos(self, input)))))

                        self.rendered_char = self.font.render(self.game.keys[self.current_char_pos].value,True,(200,127,127))
                        self.screen.blit(self.rendered_char, (self.char_rect.x, self.char_rect.y))
                if event.type == Game.TIMEREVENT:
                    self.timer -= 1
                    if self.timer < 0:
                        self.running = False

            # flip() the display to put your work on screen
            pygame.display.flip()

            self.clock.tick(60)  # limits FPS to 60'''

    def update(self, actions):
        '''
        actions[0] -> target (str)

        actions[1] -> response (str)
        '''
        
        if not self.wait_for_user_key:
            self.current_char_pos = self.pick_next_key()
            self.rendered_char = self.font.render(self.game.keys[self.current_char_pos].value,True,(127,127,127))
            self.char_rect = self.rendered_char.get_rect(center=(self.game.window_width/2, self.game.window_height/2))

            self.wait_for_user_key = True
            self.reflex_time = - int(time.time() * 1000)

        if actions['target-response'] is not None:
            self.current_key_pair = actions['target-response']
            if self.current_key_pair[1] == self.current_key_pair[0]:
                self.game.keys[self.current_char_pos].update(True, self.reflex_time + int(time.time() * 1000))
                print(self.game.keys[self.current_char_pos].weight)
                self.wait_for_user_key = False
                self.rendered_char = self.font.render(self.current_key_pair[0],True,(255,255,255))
            else:
                self.add_practice_keys(tuple(sorted((self.current_char_pos, utils.input_to_pos(self.game, self.current_key_pair[1])))))
                self.rendered_char = self.font.render(self.current_key_pair[0],True,(200,127,127))
            
        if self.game.actions['results']:
            self.game.save_progress()
            self.exit_state()
            Results(self.game).enter_state()

        if self.game.actions['restart']:
            self.game.save_progress()
            self.exit_state()
            GamePlay(self.game, 'alpha').enter_state()
            self.game.states[-1].update(actions)

    def render(self):
        self.game.screen.blit(self.rendered_char, (self.char_rect.x, self.char_rect.y))
    
    def pick_next_key(self) -> int:
        '''
        return a keyID based on the set of weights of every key

        practice mechanism 1: when response != target, add (response, target) to practice set and practice with spaced repetition \
        until user correctly type the pair a certain number of times in succession (even when timer reaches 0)
        --> difficulty #1: increase number of the successive correct practice keys to pass
        '''

        if self.key_pair_pending:
            self.key_pair_pending = False
            return self.pending_key_id

        if len(self.practice_patterns) == 0:     # when timer reaches 0, deactivate this process
            return(self.pick_random_key())

        priority_pt = 0
        for practice_pair_ids in self.practice_patterns:
            if self.practice_patterns[practice_pair_ids].pop(0) == '1':
                if (new_priority_pt := len(self.practice_patterns[practice_pair_ids]) > priority_pt):
                    priority_pt = new_priority_pt
                    pair_this_turn = practice_pair_ids

        self._delete_practice_keys()

        if priority_pt == 0:        # meaning no '1' appeared
            return(self.pick_random_key())
        else:
            self.pending_key_id = pair_this_turn[(choice := random.choice((0,1)))]
            self.key_pair_pending = True
            return pair_this_turn[1-choice]
    
    def pick_random_key(self):
            weights = []
            sum = 0
            for key in self.game.keys:
                weights.append(key.weight)

            # return randomized key pos in self.game.keys; 
            return(random.choices(range(len(self.game.keys)), weights, k=1)[0])       # messy

    def add_practice_keys(self, key_pair:tuple):
        self.practice_patterns[key_pair] = copy.deepcopy(self.PRACTICE_PATTERN)

    def _delete_practice_keys(self):
        delete_list = []

        for pair in self.practice_patterns:
            if len(self.practice_patterns[pair]) == 0:
                delete_list.append(pair)
        
        for pair in delete_list:
            del self.practice_patterns[pair]

    def _generate_practice_pattern(self, repetitionNum:int=6):
        pattern = '1'
        for i in range(repetitionNum - 1):
            for _ in range(2**i - 1):
                pattern += '0'
            pattern += '1'
        return list(pattern)        # turn pattern into a list to use pop()
'''    
    def _weight_flatten(self):
        with open('user_data/time_record.txt') as file:
           last_session_end = int(file.read())
        current_session_start = int(time.time())
        off_time = current_session_start - last_session_end

        flatten_fac = GamePlay.RETAINING_FAC/(GamePlay.RETAINING_FAC + days(off_time))

        weight_logs = [int(math.log(int(key.weight)/Key.INITIAL_WEIGHT, self.W_INCREMENT_FAC)) for key in self.game.keys]
        for i in range(len(self.game.keys)):
            self.game.keys[i].weight = \
                int(Key.INITIAL_WEIGHT * (self.W_INCREMENT_FAC ** int(weight_logs[i] * flatten_fac)))
    
    def _regularize_weight(self):
        weight_logs = [int(math.log(int(key.weight)/Key.INITIAL_WEIGHT, self.W_INCREMENT_FAC)) for key in self.game.keys]
        min_log = min(weight_logs.values())
        for i in range(len(self.game.keys)):
            self.game.keys[i].weight = \
                int(Key.INITIAL_WEIGHT * (self.W_INCREMENT_FAC ** (weight_logs[i] - min_log)))
    
    def save_progress(self):
        self._regularize_weight()

        with open('../user_data' + self.game_mode + '.csv', 'w', newline="") as file:
            fieldnames = ['value', 'finger', 'shift', 'weight']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for key in self.game.keys:
                writer.writerow(key)

        with open('user_data/time_record.txt','w') as file:
            file.write(str(int(time.time())))
'''