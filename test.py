import random

lst = ['GreenGrass', 'Sand']
result = random.choices(lst, weights=[2, 1], k=1)
print(result)

import pygame
# from glob import glob
#
# files = glob('graphics/grass/*.png')
# print(files)
# # result = pygame.image.load(glob('graphics/grass/*.png'))
# # print(result)