import csv

f = open('chosen_results.csv')
reader = csv.DictReader(f)

flat_traces = []

for row in reader:
    traces = row['trace'].split(',')
    flat_traces.extend(traces)

wf = open('trace_list.txt', 'w')
wf.writelines('\n'.join(flat_traces))
