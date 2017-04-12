import csv

f = open('chosen_results.csv')
reader = csv.DictReader(f)
wf = open('url_trace_map.csv', 'w')

row = reader.next()
for row in reader:
    page_name = row['page_name'].split(' ')[0]
    traces = row['trace'].split(',')
    lines = '\n'.join([(page_name + ',' + trace) for trace in traces]) + '\n'
    wf.write(lines)
