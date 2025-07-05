# script for merging marks exported from stream (as csv) into SMS mark export for re-import
import csv, sys

def column_index(column):
    if ord(column) < ord('A') or ord(column) > ord('Z'):
        print("column must be character A-Z (found {})".format(column))
        sys.exit()
    return ord(column) - ord('A')

def parse_marks(marks):
    return 0.0 if marks == '-' else float(marks)

def format_sid(sid):
    while len(sid) < 8:
        sid = '0' + sid
    return sid

if __name__ == "__main__":

    if len(sys.argv) < 4:
        print("Syntax: python mark_merge.py <stream.csv>[:<column>] <sms.csv> <max_marks>")
        sys.exit()

    (stream_file, stream_column) = (sys.argv[1]).split(":") if ':' in sys.argv[1] else (sys.argv[1], 'G')
    (sms_file, max_marks) = (sys.argv[2], float(sys.argv[3]))

    # read input csv files
    with open(stream_file, 'r') as csvfile:
        stream_values = [ row for row in csv.reader(csvfile) ]
    with open(sms_file, 'r') as csvfile:
        sms_values = [ row for row in csv.reader(csvfile) ]

    # match stream_rows to sms_rows
    match_count = 0
    for stream_row in stream_values[1:]:
        # restore leading zeros of student_id if lost during stream export
        student_id = format_sid(stream_row[column_index('C')])
        marks = parse_marks(stream_row[column_index(stream_column)])
        percentage = marks * 100.0 / max_marks
        if marks > max_marks:
            print("Warning: student {} received {}/{} marks (capped at 100%)".format(student_id, marks, max_marks))
            percentage = 100.0
        for sms_row in sms_values[1:]:
            # match by student ID
            if sms_row[column_index('G')].startswith(student_id, 1):
                sms_row[column_index('J')] = "{:.2f}".format(percentage)
                sms_row[column_index('K')] = "" # clear grade or SMS may reject due to mark/grade mismatch
                match_count += 1
                break
    print("merged marks for {}/{} students".format(match_count, len(stream_values) - 1))

    # write result back to sms file
    with open(sms_file, 'w') as csvfile:
        sms_writer = csv.writer(csvfile)
        for sms_row in sms_values:
            sms_writer.writerow(sms_row)

