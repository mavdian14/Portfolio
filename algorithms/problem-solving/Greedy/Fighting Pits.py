#!/bin/python3

import math
import os
import random
import re
import sys

from collections import defaultdict

def readints():
    return [int(x) for x in input().strip().split()]


class Team():
    def __init__(self, id, strengths):
        self.id = id
        self.strengths = sorted(strengths)
        self._beatable_sizes = defaultdict(lambda: [self.strengths[0]])
        self._least_winning_index = defaultdict(int)
        self.N = len(self.strengths)
        self.sum = sum(self.strengths)

    def __len__(self):
        return len(self.strengths)

    def __getitem__(self, idx):
        return self.strengths[idx]

    def add(self, strength):
        assert not self.strengths or strength >= self.strengths[-1]
        self.N += 1
        self.sum += strength
        self.strengths.append(strength)

    def simulate_fight(self, opponent, memoize=False):
        return self.id if self.can_beat(opponent, memoize) else opponent.id

    def can_beat(self, opponent, memoize):
        if memoize:
            return self.beatable_size(opponent) >= opponent.N
        else:
            i_self = self.N - 1
            i_opponent = opponent.N - 1
            while i_self >= 0:
                i_opponent -= self[i_self]
                if i_opponent < 0:
                    return True
                i_self -= opponent[i_opponent]
            return False

    def beatable_size(self, opponent):
        bs = self._beatable_sizes[opponent]
        lwi = self._least_winning_index
        for i in range(len(bs), self.N):
            for lwi[opponent] in range(lwi[opponent], opponent.N):
                idx = i - opponent[lwi[opponent]]
                if idx < 0 or lwi[opponent] >= bs[idx]:
                    break
            else:
                return opponent.N
            bs.append(lwi[opponent] + self[i])
        return bs[-1]


def main():
    team = {}

    N, K, Q = readints()
    for n in range(N):
        s, t = readints()
        team.setdefault(t, []).append(s)

    for k, v in team.items():
        t = Team(k, team[k])
        team[k] = t

    
    num_matches = defaultdict(int)
    queries = []
    for q in range(Q):
        qt, *args = readints()
        if qt == 2:
            key = frozenset(args)
            num_matches[key] += 1
            args += [key] 
        queries.append((qt, args))

    memoize_set = set(k for k, v in num_matches.items() if v >= 1000)
    for qt, args in queries:
        if qt == 1:
            p, x = args
            team.setdefault(x, Team(x, [])).add(p)
        else:
            x, y, key = args
            print(team[x].simulate_fight(team[y], key in memoize_set))


if __name__ == '__main__':
    main()
