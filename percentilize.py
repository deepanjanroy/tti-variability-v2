import csv

f = open('ctresults.csv')
reader = csv.reader(f)

headers = reader.next()
pessimistic_metric_name = 'firstInteractive-FMP-ReverseSearchFromNetworkFirstInteractive_avg (ms)'
tti_index = headers.index(pessimistic_metric_name)

rows = []
for row in reader:
    rows.append(row)

rows_with_values = []
count = 0
for row in rows:
    try:
        float(row[tti_index])
        rows_with_values.append(row)
    except:
        count += 1

print "Ignored: ", count

rows_with_values.sort(key=lambda r: float(r[tti_index]))

chosen_rows = []
for i in xrange(0, len(rows_with_values), 8):
    chosen_rows.append(rows_with_values[i])

wf = open('chosen_results.csv', 'w')
writer = csv.writer(wf)
writer.writerow(headers)
for row in chosen_rows:
    writer.writerow(row)
