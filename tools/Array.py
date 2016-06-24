import math
import Statistics

def itemgetter(*items):
    if len(items) == 1:
        item = items[0]
        def g(obj):
            return obj[item]
    else:
        def g(obj):
            return tuple(obj[item] for item in items)
    return g

def MeanArray(X, Y, NumberOfSteps=10):
    Domain = [min(X), max(X)]
    StepSize = (Domain[1] - Domain[0]) / float(NumberOfSteps)

    NewXRange = [i * StepSize for i in range(0, NumberOfSteps + 1)]

    Y2D = []

    for CurrentMin in NewXRange:
        CurrentMax = CurrentMin + StepSize
        Y2D.append([])

        # cycle through all values
        for i in range(0, len(X)):
            # if the x value is within the range
            if X[i] >= CurrentMin and X[i] <= CurrentMax:
                # append
                Y2D[len(Y2D) - 1].append(Y[i])


    MeanY = [sum(i) / float(len(i)) if len(i) != 0 else 0 for i in Y2D]
    MaxNumber = max([sum(i) for i in Y2D])
    Number = [len(i) / float(MaxNumber) * 500.0 for i in Y2D]

    return [NewXRange, MeanY, Number]

def float_range(Start, End, Step):
    List = []
    i = Start

    while i <= End:
        i = round(i, 2)
        List.append(i)
        i += Step
    return List