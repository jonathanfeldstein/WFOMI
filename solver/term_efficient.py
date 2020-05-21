from sympy import *
import time

def symbolic_to_numeric(wf, bounds):
    result = wf
    for symbol in wf.free_symbols:
        result = result.subs(symbol, bounds[symbol][1])-result.subs(symbol, bounds[symbol][0])
    return result

class Term(object):
    def __init__(self, wfs=None, bounds=None, cst=None):
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
        if cst is None:
            self.cst = [1]
        else:
            self.cst = cst

    def __add__(self, other):
        wfs = self.wfs + other.wfs
        bounds = self.bounds + other.bounds
        cst = self.cst + other.cst
        return Term(wfs, bounds, cst)

    def __mul__(self, other):
        wfs = flatten(Matrix(self.wfs) * Matrix(other.wfs).T)
        cst = flatten(Matrix(self.cst) * Matrix(other.cst).T)
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
        return Term(wfs, bounds, cst)

    def __str__(self):
        return "wfs: " + str(self.wfs) + " bounds: " + str(self.bounds) + "cst: " + str(self.cst)

    def integrate(self):
        integrated = {wf: wf.integrate(*wf.free_symbols) if hasattr(wf, 'free_symbols') else wf for wf in set(self.wfs)}
        integral = [symbolic_to_numeric(integrated[self.wfs[i]], self.bounds[i])*self.cst[i] if hasattr(self.wfs[i], 'free_symbols') else self.wfs[i]*self.cst[i] for i in range(len(self.wfs))]
        return Term([1], [{}], [sum(integral)])
