# import random
#
# lst = ['GreenGrass', 'Sand']
# result = random.choices(lst, weights=[2, 1], k=1)
# print(result)

import pygame
# from glob import glob
#
# files = glob('graphics/grass/*.png')
# print(files)
# # result = pygame.image.load(glob('graphics/grass/*.png'))
# # print(result)

# import itertools
# import string
#
# a = string.ascii_lowercase
# print(a)
#
# com = itertools.product(a, a)
# # print(next(com))
#
# str = "".join(next(com))
# print(str)

from vendor.perlin2d import generate_perlin_noise_2d, generate_fractal_noise_2d

# shape = (12, 12)
# res = (4, 4)
# tileable = (True, True)

# result = generate_perlin_noise_2d(shape, res)
# print(result)

# noise = generate_fractal_noise_2d((1280, 960), (8, 6), 5)
# print(noise)

import numpy as np

# Create a sample 2D array
data = np.array([[-0.3, -0.4, 0.69, 0.47],
                 [0.8, 0.2, -0.3, 0.8],
                 [0.45, -0.23, 0.14, -0.28]])

# Define the value you want to find
lower_bound = 0.4
higher_bound = 0.5

combined_condition = np.logical_and(data >= lower_bound, data <= higher_bound)

# Find the indexes where the value equals the target_value
indices = np.where(combined_condition)

# Print the found indexes
print("Indices:", indices)
# print("Column Indices:", col_indices)
