from sympy import *
import time
from sympy.abc import b

def symbolic_to_numeric(wf, bounds):
    result = wf
    for arg, bound in bounds.items():
        result = result.subs(arg, bound[1])-result.subs(arg, bound[0])
    return result

def integrate_from_dict(wf, bounds):
    result = wf
    for key, value in bounds.items():
        result = wf.integrate([key, value[0], value[1]])
    return result

class Term(object):
    def __init__(self, wfs=None, bounds=None):
        # wf = weight function
        if wfs is None:
            self.wfs = [1]
        else:
            self.wfs = wfs
        # bounds are integral bounds
        if bounds is None:
            self.bounds = [{}]
        else:
            self.bounds = bounds
        # cst is the constant value, carried separately for speed improvement.
        # Default is 1 in which case the weight function is not altered by the cst.

    def __add__(self, other):
        wfs = self.wfs + other.wfs
        bounds = self.bounds + other.bounds
        return Term(wfs, bounds)

    def __mul__(self, other):
        wfs = flatten(Matrix(self.wfs) * Matrix(other.wfs).T)
        bounds = []
        for bounds1 in self.bounds:
            for bounds2 in other.bounds:
                new_bound = bounds1.copy()
                bounds1_set = set(bounds1)
                bounds2_set = set(bounds2)
                for variable in bounds1_set & bounds2_set:
                    new_bound[variable] = [max(bounds1.get(variable)[0], bounds2.get(variable)[0]), min(bounds1.get(variable)[1], bounds2.get(variable)[1])]
                for variable in bounds2_set-bounds1_set:
                    new_bound[variable] = bounds2.get(variable)
                bounds.append(new_bound)
        return Term(wfs, bounds)

    def __str__(self):
        return "wfs: " + str(self.wfs) + " bounds: " + str(self.bounds)

    def integrate(self):
        # startTime = time.time()
        # integral = [self.wfs[i].integrate((sympify('b'),  sympify(self.bounds[i]['b'][0]), sympify(self.bounds[i]['b'][1]))) if hasattr(self.wfs[i], 'free_symbols') else self.wfs[i] for i in range(len(self.wfs))]

        integrated = [wf.integrate(*wf.free_symbols) if hasattr(wf, 'free_symbols') and (len(wf.free_symbols) != 0) else wf for wf in self.wfs]
        integral = [symbolic_to_numeric(integrated[i], self.bounds[i]) if hasattr(self.wfs[i], 'free_symbols') else self.wfs[i] for i in range(len(self.wfs))]
        # endTime = time.time()
        # print(endTime - startTime)
        return Term([sum(integral)], [{}])
