mockdata = [{'snow': 0, 'drive': 1000}, {'snow': 0, 'drive': 2000}, {'snow': 0, 'drive': 3000}, {'snow': 5, 'drive': 5000}, {'snow': 4, 'drive': 5000}]

def reduceBaseline(array):
  basevalue = 0
  basecount = 0
  for i in range(len(array)):
    if array[i]['snow'] == 0:
      basevalue = basevalue + array[i]['drive']
      basecount = basecount + 1
    if array[i - 1]['snow'] == 0 and array[i]['snow'] != 0:
      array[i - 1]['drive'] = basevalue / basecount
  array = array[i-2:len(array)]

reduceBaseline(mockdata)
