import csv
from scipy.signal import find_peaks
import numpy as np
import Procedure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def val_check(arr, index, threshold): 
    result = []
    right_indeces = []
    left_indeces = []

    for i in range((index-1), 1):
        if arr[i] > threshold:
            left_indeces.append(i)
        else:
            break
    for i in range((index+1), len(arr)):
        if arr[i] > threshold:
            if len(right_indeces) < 10:
                right_indeces.append(i)
            else:
                break
        else:
            break
    if not right_indeces:
        right_indeces.append(index)
    if not left_indeces:
        left_indeces.append(index)
        
    result.append(min(left_indeces))
    result.append(max(right_indeces))
    return result


def get_peaks(results_dict, original_record_dict, fasta_read_counts, fasta_file_name, db_file_name):
    peaks_list = []
    out_file = f"{fasta_file_name}({db_file_name}).csv"
    for key, val in results_dict.items():
        standard_deviation = np.std(val)
        peaks, _ = find_peaks(val, prominence=standard_deviation*0.85, distance=18)
        t = val
        for i in peaks:
            rpm = (val[i]/fasta_read_counts)*1000000
            round_rpm = round(rpm, 4)
            if round_rpm > 5.0:
                peak_slice = val_check(val, i, (val[i]-(standard_deviation*0.1)))
                peak_start = peak_slice[0]
                peak_end = peak_slice[-1] + 18
                peak_string = original_record_dict[key][peak_start:peak_end]
                temp = [key, round_rpm, peak_start, peak_end, peak_string, '', out_file]
                peaks_list.append(temp)
            else:
                continue

    with open(out_file, 'w') as f:
        fields = ['miRNA ID', 'Reads per Million', 'Peak Start', 'Peak End', 'Peak Data', 'Total Reads in NGS File', 'File Name']
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerow(['', '', '', '', '', fasta_read_counts])
        for i in peaks_list:
            writer.writerow(i)

def get_peaks_cli(results_dict, original_record_dict, fasta_read_counts, fasta_file_name, db_file_name):
    peaks_list = []
    out_file = f"Output/Data/{fasta_file_name}({db_file_name}).csv"
    for key, val in results_dict.items():
        standard_deviation = np.std(val)
        peaks, _ = find_peaks(val, prominence=standard_deviation*0.85, distance=18)
        t = val
        for i in peaks:
            rpm = (val[i]/fasta_read_counts)*1000000
            round_rpm = round(rpm, 4)
            if round_rpm > 5.0:
                peak_slice = val_check(val, i, (val[i]-(standard_deviation*0.1)))
                peak_start = peak_slice[0]
                peak_end = peak_slice[-1] + 18
                peak_string = original_record_dict[key][peak_start:peak_end]
                temp = [key, round_rpm, peak_start, peak_end, peak_string, '', out_file]
                peaks_list.append(temp)
            else:
                continue

    with open(out_file, 'w') as f:
        fields = ['miRNA ID', 'Reads per Million', 'Peak Start', 'Peak End', 'Peak Data', 'Total Reads in NGS File', 'File Name']
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerow(['', '', '', '', '', fasta_read_counts])
        for i in peaks_list:
            writer.writerow(i)



