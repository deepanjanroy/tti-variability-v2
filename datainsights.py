import csv
import numpy as np
from generate_graphs import get_data_from_csv, clean_and_sort_data_items


def main():
    data = get_data_from_csv('results.csv')
    items = clean_and_sort_data_items(data)

    with open('data_stats.csv', 'w') as f:
        writer = csv.writer(f)
        # Headers
        writer.writerow(["Index", "Site", "Mean TTI", "STDEV", "REL-STDEV", "Count"])
        for i, (site_url, values) in enumerate(items):
            tti_values  = [v['PropAndLonely'] for v in values]
            mean = np.mean(tti_values)
            stdev = np.std(tti_values)
            rel_stdev = stdev / mean
            count = len(tti_values)
            writer.writerow([i, site_url, mean, stdev, rel_stdev, count])

if __name__ == '__main__':
    main()
