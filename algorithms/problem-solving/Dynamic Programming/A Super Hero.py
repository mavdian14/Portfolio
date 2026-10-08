#!/bin/python3

import math
import os
import random
import re
import sys

def superHero(power, bullets):
    paths_so_far = {0: (0, 0)}
    for power_level, bullets_level in (zip(reversed(power), reversed(bullets))):
        min_bullets = None
        min_enemy = None
        new_paths = {}
        for enemy_pwr, enemy_blts in zip(power_level, bullets_level):
            for total_bullets_next_lvl, carry_bullets_next_lvl in paths_so_far.values():
                extra_bullets_to_carry = 0 
                bullets_required = enemy_pwr + carry_bullets_next_lvl
                if (total_bullets_next_lvl - carry_bullets_next_lvl)  > enemy_blts:
                    extra_bullets_to_carry = (total_bullets_next_lvl - carry_bullets_next_lvl) - enemy_blts
                    bullets_required += extra_bullets_to_carry
                new_carry_bullets = carry_bullets_next_lvl + extra_bullets_to_carry
                new_path = [bullets_required, new_carry_bullets]
                if new_carry_bullets not in new_paths:
                    new_paths[new_carry_bullets] = new_path
                else:
                    if bullets_required < new_paths[new_carry_bullets][0]:
                        new_paths[new_carry_bullets] = new_path
        new_paths2 = {}
        for idx, key in enumerate(sorted(new_paths.keys())):
            if idx == 0:
                new_paths2[key] = new_paths[key]
            else:
                min_total = min(total for total, _ in new_paths2.values())
                if new_paths[key][0] < min_total:
                    new_paths2[key] = new_paths[key]
        paths_so_far = new_paths2
    return min(total_bullets for total_bullets, _ in paths_so_far.values())

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        first_multiple_input = input().rstrip().split()

        n = int(first_multiple_input[0])

        m = int(first_multiple_input[1])

        power = []

        for _ in range(n):
            power.append(list(map(int, input().rstrip().split())))

        bullets = []

        for _ in range(n):
            bullets.append(list(map(int, input().rstrip().split())))

        result = superHero(power, bullets)

        fptr.write(str(result) + '\n')

    fptr.close()
