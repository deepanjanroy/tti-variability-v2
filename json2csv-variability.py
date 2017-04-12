import collections
import csv
import json
import sys

prop_and_lonely_metric_name = 'firstInteractive-FMP-Proportional-w15-3000-lonely-ws-250-padding-1000psb-5000'
prop_metric_name = 'firstInteractive-FMP-Proportional-w15-3000'
lonely_metric_name = 'firstInteractiveNetRevLonelyWindow'

metric_names = [
    prop_metric_name,
    lonely_metric_name,
    prop_and_lonely_metric_name
]

time_to_onload_metric_name = 'timeToOnload'

def load_results_from_file(filename):
    results = [];
    with open(filename) as f:
        for line in f:
            try:
                results.append(json.loads(line))
            except:
                print "Could not parse json: "
                print line
                print "######################"
    print "Loaded " + filename
    return results

def get_diagnostic_maps(bin):
    if len(bin) == 2:
        # This means we have a diagnostis map
        return bin[1]
    return []

def get_diagnostic_from_all_bins(histogram):
    all_diagnostics = []
    underflow_bin = histogram.get('underflow_bin', [])
    all_diagnostics.extend(get_diagnostic_maps(underflow_bin))
    for binIndex, bin in histogram.get('centralBins', {}).items():
        all_diagnostics.extend(get_diagnostic_maps(bin))
    overflowBin = histogram.get('overflowBin', [])
    all_diagnostics.extend(get_diagnostic_maps(overflowBin))
    # Sometimes there is an "allBins".
    # Probably from new versions of catapult.
    if 'allBins' in histogram:
        allBins = histogram['allBins']
        for bin in allBins.values():
            all_diagnostics.extend(get_diagnostic_maps(bin))
    return all_diagnostics

def get_metric_histogram(ctp_result, metricName):
    histograms = ctp_result['pairs']['histograms']
    metric_histogram = [h for h in histograms if h.get('name', '') == metricName]
    if len(metric_histogram) == 0:
        return None
    if len(metric_histogram) > 1:
        raise Exception("The world is falling apart")
    return metric_histogram[0]

# The approach in this function looks fragile but I don't know a better way
# def get_url(ctp_result):
#     import IPython; IPython.embed()
#     # The first histogram happens to be the one with some metadata.
#     metadata_histogram = ctp_result['pairs']['histograms'][0]
#     return metadata_histogram['storyUrl']
def get_url(ctp_result):
    fcp_histogram = get_metric_histogram(ctp_result, 'timeToFirstContentfulPaint')
    diagnostics = get_diagnostic_from_all_bins(fcp_histogram)
    if len(diagnostics) > 0:
        url = diagnostics[0]["url"]["value"]
        return url
    return "unable to determine url"

# This function returns a string in the failure cases to make it more obvious in
# the csv what's going on.
def get_value(histogram):
    if 'running' in histogram:
        running_stats = histogram['running']
        running_max = running_stats[1]
        running_min = running_stats[4]
        if running_min == running_max:
            return running_min
        else:
            return "Error: Value not unique. Count: " + str(running_stats[0])
    return "Error: No value found"


# Returns a list of useful breakdown numbers
def get_breakdowns(result):
    histogram = get_metric_histogram(result, reverse_search_metric_name)
    diagnostics = get_diagnostic_from_all_bins(histogram)
    if len(diagnostics) == 0:
        return ["Error: No diagnostic found"]
    if len(diagnostics) != 1:
        print "Warning: Multiple diagnostics found: ", diagnostics
    return [json.dumps(diagnostics[-1]['Long task Breakdown of [forwardSearch, reverseSearch]']['value'])]

def get_url_to_trace_map(map_file):
    with open(map_file) as f:
        r = csv.reader(f)
        r.next()  # Skip over column titles
        url_to_traces = {}
        for row in r:
            url_to_traces[row[0].split(" ")[0].strip()] = row[1]
        return url_to_traces

def get_trace_path(ctp_result):
    return ctp_result["canonicalUrl"]


def main():
    if len(sys.argv) >= 2:
        ctp_result_filename = sys.argv[1]
    else:
        ctp_result_filename = "ctpresults.json"

    if len(sys.argv) >= 3:
        url_trace_map_filename = sys.argv[2]
    else:
        url_trace_map_filename = "url_trace_map.csv"

    results = load_results_from_file(ctp_result_filename)
    # url_to_traces = get_url_to_trace_map(url_trace_map_filename)
    with open("results.csv", 'wb') as f:
        writer = csv.writer(f, delimiter='|')
        related_data_headers = ['TTFCP', 'TTFMP', 'TTOnload', 'Prop', 'Lonely', 'PropAndLonely']
        writer.writerow(['url', 'trace'] + related_data_headers);
        for r in results:
            if len(r['failures']) != 0:
                print "Skipping result because of failures: ", r
                print "XXXXXXXXXXXXXXX"
                continue
            metrics = [0, 0, 0, 0]
            tti_metric_histograms = [get_metric_histogram(r, m) for m in metric_names]
            ttonload_histogram = get_metric_histogram(r, time_to_onload_metric_name)

            # Any one of them is good for diagnostics
            diagnostics = get_diagnostic_from_all_bins(tti_metric_histograms[0])
            # Any unavailable data will just be plotted as 0
            if len(diagnostics) == 1:
                d = diagnostics[0]

                nav_start = float(d['navigationStart']['value'])
                fcp = float(d['fcp']['value'])
                # SearchBegin happens to be FMP at the moment.
                # Please be cautious if reusing this code. ###
                fmp = float(d['fmp']['value'])
                tti_metric_values = [(get_value(h) - nav_start) for h in tti_metric_histograms]

                ttfcp = fcp - nav_start
                ttfmp = fmp - nav_start
                ttonload = get_value(ttonload_histogram)
                metrics = [ttfcp, ttfmp, ttonload] + tti_metric_values

            url = get_url(r)
            rowData = [url, get_trace_path(r)] + metrics
            writer.writerow(rowData)
    print "Total results processed:", len(results)


if __name__ == '__main__':
    main()

