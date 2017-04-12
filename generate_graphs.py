import matplotlib.pyplot as plt
import numpy as np
import collections
import csv
import os

from matplotlib.legend_handler import HandlerLine2D

generated_graph_dir_name = 'generated_graphs'

def get_data_from_csv(csvfile):
    data = collections.defaultdict(list)
    with open(csvfile) as f:
        reader = csv.reader(f, delimiter='|')
        header = reader.next()
        for row in reader:
            value = {}
            for i in xrange(2, len(header)):
                string_data = row[i]
                try:
                    float_data = float(string_data)
                except:
                    float_data = np.nan
                value[header[i]] = float_data
            url = row[0]
            data[url].append(value)
    return data


def clean_and_sort_data_items(data):
    items = data.items()
    # get_tti = lambda x: x['TTI']
    get_tti = lambda x: x['PropAndLonely']

    # Filter out 0 TTI values. They skew mean and std
    items = map(lambda (k, v): (k, filter(lambda x: get_tti(x) > 0, v)), items)
    # Sort by mean TTI
    items.sort(key=lambda (k, v): np.mean(map(get_tti, v)))
    # Also, sort the list of values of each site by TTI
    items = map(lambda (k, v): (k, sorted(v, key=get_tti)), items)

    return items


def main():
    data = get_data_from_csv('results.csv')
    items = clean_and_sort_data_items(data);

    counter = 0;
    for site_url, values in items:
        tti_values = [v['PropAndLonely'] for v in values]
        prop_line, = plt.plot([v['Prop'] for v in values],  range(len(values)), 'b-o', label='TTI-Prop')
        lonely_line, = plt.plot([v['Lonely'] for v in values],  range(len(values)), 'r-s', label='TTI-Lonely')
        prop_and_lonely_line, = plt.plot([v['PropAndLonely'] for v in values],  range(len(values)), 'g-p', label='TTI-PropAndLonely')
        lonely_line, = plt.plot([v['Prop'] for v in values],  range(len(values)), 'g-.', label='TTI-Prop')
        fcp_line, = plt.plot([v['TTFCP'] for v in values], range(len(values)), 'g-.', label='TTFCP')
        fmp_line, = plt.plot([v['TTFMP'] for v in values], range(len(values)), 'r--', label='TTFMP')
        # tti_line, = plt.plot(tti_values, range(len(values)), 'b-o', label='TTI')
        onload_line, = plt.plot([v['TTOnload'] for v in values], range(len(values)), 'k-', label='TTOnload')
        plt.xlabel('NetworkReverseSearch FirstInteractive (ms)')
        plt.ylabel('Run index')
        plt.axis([0, 150000, 0, 25])

        mean = np.mean(tti_values)
        std = np.std(tti_values)
        rel_std = std / mean
        plt.title(site_url)
        stats = """mean: {0:.2f}
        std: {1:.2f}
        rel_std: {2:.4f}""".format(mean, std, rel_std)
        plt.text(0.95, 0.05, stats, horizontalalignment='right', verticalalignment='bottom', transform=plt.gca().transAxes);

        handler_map = {
            fcp_line : HandlerLine2D(numpoints=5),
            fmp_line : HandlerLine2D(numpoints=5),
            prop_line : HandlerLine2D(numpoints=5),
            lonely_line : HandlerLine2D(numpoints=5),
            prop_and_lonely_line : HandlerLine2D(numpoints=5),
            # tti_line : HandlerLine2D(numpoints=5)
        }
        plt.legend(handler_map=handler_map, loc='best')


        print '<p id="{0}">{0}: {1}</p>'.format(counter, site_url)
        print '<img src="{0}.png">'.format(counter)
        if not os.path.exists(generated_graph_dir_name):
            os.mkdir(generated_graph_dir_name);
        # plt.show()
        plt.savefig(os.path.join(generated_graph_dir_name, str(counter) + '.png'))
        plt.gcf().clear()
        counter += 1
        # break
    print "Generated " + str(counter) + " graphs"


if __name__ == '__main__':
    main()
