class ProcessedData:
    def __init__(self, id, stress, strain, mstress, mstrain, modulus, maxStress, percentYeild, breakStress, percentatBreak, fullStrain, fullStress, number, orrient):
        self.id = id
        self.stress = stress
        self.strain = strain
        self.mstrain = mstrain
        self.mstress = mstress
        self.modulus = modulus
        self.maxStress = maxStress
        self.percentYeild = percentYeild
        self.breakStress = breakStress
        self.percentatBreak = percentatBreak
        self.fullStrain = fullStrain
        self.fullStress = fullStress
        self.number = number
        self.orrient = orrient