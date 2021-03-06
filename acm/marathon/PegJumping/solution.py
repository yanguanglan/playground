from collections import Counter
from itertools import cycle, product as prod, permutations as perm, combinations as comb, combinations_with_replacement as combr
from sys import stdin, stdout
from collections import deque
from Queue import Queue
from copy import deepcopy
MAX_REC = 26000
import sys
import heapq
import random
import time
sys.setrecursionlimit(MAX_REC)
read_ints = lambda: map(int, raw_input().split())
read_floats = lambda: map(float, raw_input().split())

MAX_STATE = 10
MAX_REC_START_POS_TRY = 10
DIR = [(-2, 0), (2, 0), (0, -2), (0, 2)]
ADJ_DIR = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIR_NAME = ["U", "D", "L", "R"]
START_TS = time.time()

random.seed(47)


def opposite_dir(d):
    if d == "U":
        return "D"
    elif d == "D":
        return "U"
    elif d == "L":
        return "R"
    else:
        return "L"

def elapse():
    return time.time() - START_TS


def early_stage():
    return elapse() < 3.0

def late_stage():
    return elapse() > 9.0

def end_stage():
    #return elapse() > 14.0
    return False

def middle_stage():
    e = elapse()
    return e < 6.0 and e > 3.0


def cerr(msg, newline=True):
    if newline:
        print >> sys.stderr, msg
    else:
        print >> sys.stderr, msg,
    sys.stderr.flush()


class State(object):

    def __init__(self, game, r, c):
        self.game = game
        self.r = r
        self.c = c
        self.cr = r
        self.cc = c
        self.sum = 0
        self.dirs = []
        self.used_peg_set = set()

    def can_move(self, d, ignore_dest_peg=False):
        pos = DIR_NAME.index(d)
        dr, dc = DIR[pos]
        br, bc = ADJ_DIR[pos]
        cr, cc = self.cr + dr, self.cc + dc
        ar, ac = self.cr + br, self.cc + bc
        if self.game.valid_cell(cr, cc) and (
            (ignore_dest_peg or not self.game.has_peg(cr, cc)) or
            (cr == self.r and cc == self.c)
        ) and self.game.valid_cell(ar, ac) and (self.game.has_peg(ar, ac)) and (
            not (ar, ac) in self.used_peg_set):
            return True

    def run(self, d):
        pos = DIR_NAME.index(d)
        dr, dc = DIR[pos]
        br, bc = ADJ_DIR[pos]
        cr, cc = self.cr + dr, self.cc + dc
        ar, ac = self.cr + br, self.cc + bc
        self.sum += self.game.value(ar, ac)
        self.dirs.append(d)
        self.used_peg_set.add((ar, ac))
        self.cr = cr
        self.cc = cc

    def copy(self):
        state = State(self.game, self.r, self.c)
        state.cr = self.cr
        state.cc = self.cc
        state.sum = self.sum
        state.dirs = self.dirs[:]
        state.used_peg_set = deepcopy(self.used_peg_set)
        return state

    def score(self):
        return self.sum * len(self.dirs)

    def __str__(self):
        return "(r=%s, c = %s, cr=%s, cc=%s, len=%s, score = %s, dirs=%s)" % (
            self.r, self.c, self.cr, self.cc, len(self.dirs), self.score(),
            "".join(self.dirs))

    def show(self):
        for x in xrange(self.game.N):
            for y in xrange(self.game.N):
                if (x, y) in self.used_peg_set:
                    cerr('o', False)
                elif (x, y) == (self.r, self.c):
                    cerr('s', False)
                elif self.game.has_peg(x, y) and abs(x-self.r) % 2 == 0 and abs(y-self.c)%2 == 0:
                    cerr('x', False)
                elif self.game.has_peg(x, y):
                    cerr('+', False)
                else:
                    cerr('.', False)

            cerr("")

    def step(self):
        return "%s %s %s" % (self.r, self.c, "".join(self.dirs))


class Game(object):

    def __init__(self, peg_value, board):
        self.peg_value = peg_value[:]
        self.N = len(board)
        self.bo = deepcopy(board)
        self.score = 0
        self.steps = []
        self.call_cnt_bf_one_largest_step_at = 0

    def valid_cell(self, r, c):
        return r >= 0 and r < self.N and c >= 0 and c < self.N

    def has_peg(self, r, c):
        return self.valid_cell(r, c) and self.bo[r][c] > 0

    def value(self, r, c):
        return self.peg_value[self.bo[r][c]]

    def update(self, steps):
        for step in steps:
            self.run(step)

    def merge(self, groups):
        ret = set()
        for g in groups:
            ret = ret.union(g)
        return ret

    def divide(self, peg_list):
        groups = []
        vis = set()
        for x, y in peg_list:
            if not (self.has_peg(x, y) and not (x, y) in vis):
                continue
            g = set()
            g.add((x, y))
            vis.add((x, y))
            Q = Queue()
            Q.put((x, y))
            while not Q.empty():
                r, c = Q.get()
                for dr in [-2, -1, 0, 1, 2]:
                    for dc in [-2, -1, 0, 1, 2]:
                        nr, nc = r + dr, c + dc
                        if not (self.has_peg(nr, nc) and not (nr, nc) in vis):
                            continue
                        g.add((nr, nc))
                        Q.put((nr, nc))
                        vis.add((nr, nc))
            groups.append(g)

        groups = sorted(groups, key=lambda g: len(g))
        return groups

    def runs(self, steps, group):
        for step in steps:
            self.run(step, group)

    def run(self, step, group):
        r, c, dirs = step.split(' ')
        r = int(r)
        c = int(c)
        assert self.valid_cell(r, c) and self.has_peg(r, c)

        if (r, c) in group:
            group.remove((r, c))


        sum = 0
        for d in dirs:
            pos = DIR_NAME.index(d)
            dr, dc = DIR[pos]
            ar, ac = ADJ_DIR[pos]
            # add new peg being jumped over
            nr, nc = r + ar, c + ac
            assert self.has_peg(nr, nc)
            if (nr, nc) in group:
                group.remove((nr, nc))
            sum += self.value(nr, nc)
            self.bo[nr][nc] = 0
            # move jumping peg
            nr, nc = r + dr, c + dc
            assert not self.has_peg(nr, nc)
            self.bo[nr][nc] = self.bo[r][c]
            self.bo[r][c] = 0
            r, c = nr, nc
        cur_score = sum * len(dirs)
        self.score += cur_score
        self.steps.append(step)
        group.add((r, c))
        return r, c, len(dirs), cur_score

    def h(self):
        pass

    def bf_one_largest_step_at(self, r, c, ignore_dest_peg=False):
        self.call_cnt_bf_one_largest_step_at += 1
        assert self.valid_cell(r, c) and self.has_peg(r, c)
        best = state = State(self, r, c)
        cur_list = [state]
        dep = 0
        while len(cur_list) > 0:
            dep += 1
            #cerr("dep = %s, cur_list size=%s" % (dep, len(cur_list)))
            cur_list = sorted(cur_list, key=lambda s: -s.score())
            next_list = []
            state_limit = MAX_STATE if not late_stage() else 5
            for i in xrange(min(len(cur_list), state_limit)):
                state = cur_list[i]
                for d in DIR_NAME:
                    if state.can_move(d, ignore_dest_peg):
                        new_state = state.copy()
                        new_state.run(d)
                        if best.score() < new_state.score():
                            best = new_state
                        next_list.append(new_state)
            cur_list = next_list
        return best

    def bf_one_step_at(self, r, c, ignore_dest_peg=False):
        assert self.valid_cell(r, c) and self.has_peg(r, c)
        state = State(self, r, c)
        while True:
            found = False
            for d in DIR_NAME:
                if state.can_move(d):
                    state.run(d, ignore_dest_peg)
                    found = True
            if not found:
                break
        return state

    def can_move(self, r, c, d=None):
        if not self.valid_cell(r, c) or self.bo[r][c] == 0:
            return dirs
        for i in xrange(len(DIR)):
            dr, dc = DIR[i]
            ar, ac = ADJ_DIR[i]
            if self.valid_cell(r + dr, c + dc) and  \
                not self.has_peg(r + dr, c + dc) and \
                self.valid_cell(r + ar, c + ac) and \
                self.has_peg(r + ar, c + ac) and \
                (not d or d == DIR_NAME[i]):
                return True

    def guess_start_pegs(self, group):
        candidates = []
        for r, c in group:
            if self.has_peg(r, c):
                candidates.append((r, c))

        sub_group = []
        for i in xrange(4):
            sub_group.append(set())
        for r, c in candidates:
            ty = (r % 2) * 2 + c % 2
            sub_group[ty].add((r, c))

        candidates = []
        for i in xrange(4):
            if sub_group[i]:
                sub_candidates = []
                minr, minc, maxr, maxc = self.border_pos(sub_group[i])
                #cerr("sub_group_sz=%s, val=%s" % (len(sub_group[i]), sub_group[i]))
                #cerr("minr=%s,minc=%s,maxr=%s,maxc=%s" % (minr, minc, maxr, maxc))
                for r, c in sub_group[i]:
                    if r == minr or r == maxr or c == minc or c == maxc:
                        sub_candidates.append((r, c))
                candidates.append(sub_candidates)
        return candidates

    def bf_one_step(self, group):

        candidates = []
        for c in self.guess_start_pegs(group):
            for p in c:
                if self.can_move(p[0], p[1]):
                    candidates.append(p)

        random.shuffle(candidates)
        best = None

        limit = 1
        if early_stage():
            limit = 30
        elif middle_stage():
            limit = 20 

        for i in xrange(min(len(candidates), limit)):
            r, c = candidates[i]
            state = self.bf_one_largest_step_at(r, c)
            #state = self.bf_one_step_at(r, c)
            if not best or best.score() < state.score():
                best = state

        if best:
            #best.show()
            #exit(0)
            return best.step()

    def gen_groups(self):
        peg_list = [(i, j) for i in xrange(self.N) for j in xrange(self.N)
                    if self.has_peg(i, j)]
        groups = self.divide(peg_list)
        return groups

    def border_pos(self, group):
        minr, minc = self.N + 1, self.N + 1
        maxr, maxc = -1, -1
        for r, c in group:
            minr = min(minr, r)
            minc = min(minc, c)
            maxr = max(maxr, r)
            maxc = max(maxc, c)
        return minr, minc, maxr, maxc

    def get_rec_start_pos(self, group):

        candidates = []
        for c in self.guess_start_pegs(group):
            random.shuffle(c)
            candidates.extend(c[:])
        random.shuffle(candidates)

        #self.show(candidates)

        best = None

        for i in xrange(min(len(candidates), MAX_REC_START_POS_TRY)):
            r, c = candidates[i]
            state = self.bf_one_largest_step_at(r, c, True)
            #cerr("elapse time=%s state=%s" % (elapse(), state))
            if not best or best.score() < state.score():
                best = state

        cerr("at get_rec_start_pos, group_size=%s, candidate_size=%s, best=%s"
            % (len(group), len(candidates), best))
        best.show()

        return best.r, best.c

    def remove_peg(self, r, c, blocks=set()):
        assert self.has_peg(r, c)
        for i in xrange(4):
            ax, ay = ADJ_DIR[i]
            nx, ny = r + ax, c + ay
            if (nx, ny) in blocks:
                continue
            if self.has_peg(nx, ny) and self.can_move(nx, ny, opposite_dir(DIR_NAME[i])):
                step = "%s %s %s" % (nx, ny, opposite_dir(DIR_NAME[i]))
                return step

    def remove_rec_blocks(self, r, c, group):
        blocks = set()
        for x, y in group:
            if (x, y) != (r, c) and abs(x - r) % 2 == 0 and abs(y - c) % 2 == 0:
                blocks.add((x, y))

        block_cnt = len(blocks)

        while True:
            found = False
            for x, y in blocks:
                if not self.has_peg(x, y):
                    continue
                step = self.remove_peg(x, y)
                if step:
                    self.run(step, group)
                    found = True
                else:
                    for i in xrange(4):
                        continue
                        ax, ay = ADJ_DIR[i]
                        nx, ny = x + ax, y + ay
                        if not self.has_peg(nx, ny):
                            continue
                        step = self.remove_peg(nx, ny, blocks)
                        if step:
                            self.run(step, group)
                            found = True
                        else:
                            pass
            if not found:
                break

        left_cnt = len(set((x, y) for (x, y) in blocks if self.has_peg(x, y)))

        cerr("block_cnt = %s,removed = %s" % (block_cnt, left_cnt))
        #cerr("elapse=%s" % elapse())

    def show(self, p):
        for x in xrange(self.N):
            for y in xrange(self.N):
                if (x, y) in p:
                    cerr('o', False)
                elif self.has_peg(x, y):
                    cerr('+', False)
                else:
                    cerr('.', False)
            cerr("")

    def bf(self):
        best_cnt = 0
        best_score = 0
        groups = self.gen_groups()
        #for g in groups:
        #    cerr("group size=%s, show:" % len(g))
        #    self.show(g)
        while groups:
            if end_stage():
                break
            g = groups.pop()
            total = len(g)
            while True:
                if end_stage():
                    break
                r, c = self.get_rec_start_pos(g)
                self.remove_rec_blocks(r, c, g)
                step = self.bf_one_step(g)
                if step:
                    r, c, cnt, score = self.run(step, g)
                    if cnt > best_cnt:
                        best_cnt = cnt
                        #cerr("best_cnt update: r=%s, c=%s, cnt=%s, score=%s" % (r, c, cnt, score))
                    if score > best_score:
                        best_score = score
                    cerr("update: r=%s, c=%s, cnt=%s, score=%s, elapse=%s" % (r, c, cnt, score, elapse()))
                    if total > 200 and 1.0 * (total - len(g)) / total < 0.5:
                        ng = self.divide(g)
                        groups.extend(ng)
                        cerr("try to divide group into %s subgroup" % len(ng))
                        break
                else:
                    break
        cerr("N=%s" % self.N)
        cerr("bf_one_largest_step_at cnt=%s" % self.call_cnt_bf_one_largest_step_at)


class PegJumping(object):

    def getMoves(self, peg_value, board_):
        peg_value.insert(0, 0)
        board = []
        N = len(board_)
        for i in xrange(N):
            line = []
            for j in xrange(N):
                line.append(0 if board_[i][j] == '.' else int(board_[i][j]) + 1)
            board.append(line)
        peg = Game(peg_value, board)
        peg.bf()
        return peg.steps


def main():
    M = read_ints()[0]
    peg_value = []
    for i in xrange(M):
        peg_value.append(read_ints()[0])
    N = read_ints()[0]
    board = []
    for i in xrange(N):
        line = raw_input()
        board.append(line)
    peg = PegJumping()
    ret = peg.getMoves(peg_value, board)
    print len(ret)
    for l in ret:
        print l
    stdout.flush()


if __name__ == '__main__':
    main()
