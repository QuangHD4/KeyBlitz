import pygame, os, copy

BASE_IMG_PATH = 'components/'

def days(time:int):
    return time/86400

def input_to_pos(game, in_value:str):
    for i in range(len(game.keys)):
        if game.keys[i].value == in_value:
            return i
    raise Exception('Key not found')

def load_img(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    return img

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_img(BASE_IMG_PATH + path + '/' + img_name))
    return images

# apply in Key class
# def jitter(char:pygame.Surface, duration = ):


class Animation:
    def __init__(self, images, img_dur:int = 5) -> None:
        self.images = images
        self.img_dur = img_dur
        self.frame = 0
        self.done = False

    def update(self):
        self.frame = min(self.frame + 1, self.img_dur * len(self.images) - 1)
        if self.frame >= self.img_dur * len(self.images):
            self.done = True

    def image(self):
        return self.images[self.frame//self.img_dur]
    

'''def run_once(f):
    def 

@run_once
def start_timer'''