data = {}
data['format'] = '1456 the streets, devner, co, use, usa'
commacount = 0
shortaddy = ''
for char in data['format']:
  if char == ',':
    commacount = commacount + 1
    continue
  if commacount == 1:
    shortaddy = shortaddy + char
  if commacount ==2:
    shortaddy = shortaddy + char
print shortaddy
