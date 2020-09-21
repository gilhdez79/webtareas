def getHours(strhora):
    string= strhora.split(':')
    minutos = int(string[0])
    segundos = int(string[1])

    if minutos > 0 :
        minutos = minutos * 1;

    totalSeg = str(minutos) + '.' + str(segundos);
    return (float(totalSeg))

# print(getHours("10:20"))
