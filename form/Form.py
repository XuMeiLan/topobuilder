# -*- coding: utf-8 -*-
# @Author: bonet
# @Date:   2016-05-01 12:30:36
# @Last Modified by:   bonet
# @Last Modified time: 2016-05-02 22:02:02
import scipy
import math
import os

from ..RosettaIO.constraints.ConstraintSet import ConstraintSet
from ..RosettaIO.loops.Loops import Loops


class Form(object):
    """docstring for Form"""
    def __init__(self, identifier, sslist):
        self.sslist  = sslist
        self.id      = identifier
        self.seq_str = []
        self.inits   = []
        self.const   = ConstraintSet()
        self.loops   = Loops()
        self.order   = []

    def set_order(self, data):
        order = {}
        for x in range(len(data)):
            order[data[x]] = x + 1
        refs  = filter(None, [x.ref for x in self.sslist])
        self.order = [order[x] for x in refs]

    def make_loops(self):
        for x in range(len(self.sslist)):
            if self.sslist[x].ref is not None:
                self.loops.add_loop(self.inits[x], self.inits[x] + len(self.sslist[x].atoms) - 1)

    def make_constraints(self):
        for x in range(len(self.sslist)):
            y = self.sslist[x]
            p = self.inits[x]
            for r1 in range(len(y.atoms)):
                for r2 in range(r1 + 5, len(y.atoms)):
                    d = scipy.spatial.distance.euclidean(y.atoms[r1], y.atoms[r2])
                    self.const.add_constraint(num1 = p + r1, num2 = p + r2, value = d, dev=1.5, tag="INNER")

        for x in range(len(self.sslist)):
            px = self.inits[x]
            sx = self.sslist[x]
            for y in range(x + 1, len(self.sslist)):
                py = self.inits[y]
                sy = self.sslist[y]
                for r1 in range(len(sx.atoms)):
                    for r2 in range(len(sy.atoms)):
                        d = scipy.spatial.distance.euclidean(sx.atoms[r1], sy.atoms[r2])
                        self.const.add_constraint(num1 = px + r1, num2 = py + r2, value = d, dev=3.0, tag="OUTER")

    # def _check_invert(self):  # TODO: wrong
    #     count1 = 0
    #     for x in range(len(self.sslist)):
    #         if self.sslist[x].ref is not None:
    #             count1 = x
    #     return 0 if count1 % 2 == 1 else 1

    def prepare_coords(self):
        # inv = self._check_invert()
        # for x in range(len(self.sslist)):
        #     if x % 2 == inv:
        #         self.sslist[x].struc.invert_direction()

        i = 2
        self.seq_str.append(("G", "C", "X"))
        self.inits.append(i)
        for x in range(len(self.sslist) - 1):
            for xx in self.sslist[x].sequence:
                self.seq_str.append((xx, self.sslist[x].get_type(), "S"))
            i += len(self.sslist[x].sequence)
            d = scipy.spatial.distance.euclidean(self.sslist[x].atoms[-1], self.sslist[x + 1].atoms[0])
            d = int(math.ceil(d / 3.))
            i += d
            for yy in range(d):
                self.seq_str.append(("G", "C", "X"))
            self.inits.append(i)
        for xx in self.sslist[-1].sequence:
            self.seq_str.append((xx, self.sslist[-1].get_type(), "S"))
        self.seq_str.append(("G", "C", "X"))

    def to_sequence(self):
        return ">" + self.id + "\n" + "".join([x[0] for x in self.seq_str])

    def to_psipred_ss(self):
        text = []
        text.append("# PSIPRED VFORMAT (PSIPRED V2.6 by David Jones)\n")
        sse = [x[1] for x in self.seq_str]
        for i in range(len(sse)):
            pH, pE, pC = 0, 0, 0
            if sse[i] == 'C': pC = 1
            else:
                edge = False
                if sse[i] != sse[i - 1] or sse[i] != sse[i - 2]: edge = True
                if sse[i] != sse[i + 1] or sse[i] != sse[i + 2]: edge = True
                if edge:
                    pC = 0.3
                    if sse[i] == 'E': pE = 0.7
                    else:             pH = 0.7
                else:
                    if sse[i] == 'E': pE = 1
                    else:             pH = 1

            line = "{0:>4} {1} {2}   {3:0.3f}  {4:0.3f}  {5:0.3f}".format(i + 1, 'A', sse[i], pC, pH, pE)
            text.append(line)
        return '\n'.join(text)

    def to_pdb(self):
        data = []
        for x in range(len(self.sslist)):
            data.append(self.sslist[x].atom_points(atom = self.inits[x]))
        return "\n".join(data)

    # def to_command(self, ori, chain, targetl, templtl, fastaf, ssefil, constrfl, commfl):

    #     text = []
    #     text.append("-fold_from_loops:target:pose {0}".format(os.path.relpath(ori, os.path.dirname(commfl))))
    #     text.append("-fold_from_loops:target:chain {0}".format(chain))
    #     text.append("-fold_from_loops:target:pdb_count")
    #     text.append("-fold_from_loops:target:loops {0}".format(os.path.relpath(targetl, os.path.dirname(commfl))))
    #     text.append("-fold_from_loops:target:order {0}".format(" ".join([str(x) for x in self.order])))

    #     text.append("-in:file:s {0}".format(os.path.relpath(ori, os.path.dirname(commfl))))
    #     text.append("-in:file:fasta {0}".format(os.path.relpath(fastaf, os.path.dirname(commfl))))
    #     text.append("-in:file:psipred_ss2 {0}".format(os.path.relpath(ssefil, os.path.dirname(commfl))))
    #     text.append("-loops:loop_file {0}".format(os.path.relpath(templtl, os.path.dirname(commfl))))
    #     text.append("-fold_from_loops:scaffold:nopose")
    #     text.append("-fold_from_loops:scaffold:cst_file {0}".format(os.path.relpath(constrfl, os.path.dirname(commfl))))

    #     # text.append("-fold_from_loops:loop_mov_nterm 2")
    #     # text.append("-fold_from_loops:loop_mov_cterm 2")

    #     text.append("-fold_from_loops:hb_srbb 2")

    #     text.append("-fold_from_loops:native_ca_cst")

    #     text.append("-in:ignore_unrecognized_res")
    #     text.append("-run:intermediate_structures")
    #     text.append("-out:nstruct 100")
    #     text.append("-out:file:silent_struct_type binary")
    #     # text.append("-out:prefix {0}".format(ident))
    #     # text.append("-out:file:silent {0}".format(ident))

    #     text.append("-out:overwrite")

    #     return "\n".join(text)