import hashlib


class AnalysisBase(object):
    is_active = True

    def name(self):
        if self.__class__.__name__.startswith("Analysis"):
            return self.__class__.__name__[8:].lower()
        else:
            return self.__class__.__name__.lower()

    def reset(self, bc_size):
        raise NotImplemented

    def update(self, chuck):
        raise NotImplemented

    def done(self):
        raise NotImplemented


class FileStreamAnalysis(object):
    def __init__(self):
        self.factors = []

    def register(self, factor: AnalysisBase):
        self.factors.append(factor)

    def executor(self, fp):
        base_chuck_size = 9500 * 1024
        for factor in self.factors:
            factor.reset(bc_size=base_chuck_size)
        base_chuck = fp.read(base_chuck_size)
        for factor in self.factors:
            factor.update(base_chuck)
        while len(base_chuck) == base_chuck_size:
            base_chuck = fp.read(base_chuck_size)
            for factor in self.factors:
                if factor.is_active:
                    factor.update(base_chuck)
        res = {}
        for factor in self.factors:
            res[factor.name()] = factor.done()
        return res


class AnalysisMd5(AnalysisBase):
    def reset(self, bc_size):
        self.hashlib = hashlib.md5()

    def update(self, chuck):
        self.hashlib.update(chuck)

    def done(self):
        return self.hashlib.digest()


class AnalysisSha1(AnalysisMd5):
    def reset(self, bc_size):
        self.hashlib = hashlib.sha1()


class AnalysisEd2k(AnalysisMd5):
    def reset(self, bc_size):
        self.hashlib = hashlib.new('md4')

    def update(self, chuck):
        self.hashlib.update(hashlib.new('md4', chuck).digest())


class AnalysisSize(AnalysisBase):
    size = 0
    def reset(self, bc_size):
        self.size = 0

    def update(self, chuck):
        self.size += len(chuck)

    def done(self):
        return self.size