"""
Documentation: Pin mapping
    cyton board is mapped to the first 8 positions in the list amd the daisy board to the further 8 positions

        Node | Pin | Position
             |     | in list
-------------|-----|----------
Cyton:   C3  |  1  |    0
         C4  |  3  |    2
Daisy:  FC1  |  2  |   10
        FC2  |  3  |   11
        CP1  |  6  |   14
        CP2  |  7  |   15
"""

'''
Calculate average signal of the four electrodes surrounding the hand knob of 
the motor area (small laplacian)
'''
def calculate_small_laplacian(signal1, signal2, signal3, signal4):
    counter = 0
    length = len(signal1)
    result = list()

    while counter < length:
        average = (signal1[counter]+signal2[counter]+signal3[counter]+signal4[counter])/4
        result.append(average)
        counter += 1

    return result


'''
Subtract the calculated average signal from C3 and C4 to perform the spatial filtering
'''
def calculate_spatial_filtering(signal_list):
    signal_C3a = list()
    signal_C4a = list()
    result = list()
    #TODO: ((maybe)) adjust structure of the lists
    signal_average = calculate_small_laplacian(signal_list[0], signal_list[1], signal_list[2], signal_list[5])

    length = len(signal_list[0])
    counter = 0
    while counter < length:
        signal_C3a.append(signal_list[3][counter]-signal_average[counter])
        signal_C4a.append(signal_list[4][counter]-signal_average[counter])
        counter += 1

    result.append(signal_C3a)
    result.append(signal_C4a)
    return result




