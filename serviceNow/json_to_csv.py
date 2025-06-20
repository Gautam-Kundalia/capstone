import json
import csv
import os
from collections import defaultdict

def analyze_json_file(json_file):
    """Analyze the JSON file to see what streams and records we have."""
    stream_counts = defaultdict(int)
    total_records = 0
    
    print(f"Analyzing {json_file}...")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    data = json.loads(line)
                    if data.get('type') == 'RECORD':
                        stream_name = data.get('stream', 'unknown')
                        stream_counts[stream_name] += 1
                        total_records += 1
                        
                        if line_num % 1000 == 0:
                            print(f"Processed {line_num} lines, found {total_records} records...")
                            
                except json.JSONDecodeError:
                    continue
                    
    except FileNotFoundError:
        print(f"File {json_file} not found")
        return {}, 0
    
    print(f"\nAnalysis complete!")
    print(f"Total records: {total_records}")
    print("\nRecords by stream:")
    for stream, count in sorted(stream_counts.items()):
        print(f"  {stream}: {count} records")
    
    return stream_counts, total_records

def extract_stream_to_csv(json_file, stream_name, output_dir):
    """Extract specific stream data to CSV."""
    records = []
    
    print(f"Extracting {stream_name} stream...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            try:
                data = json.loads(line)
                if data.get('type') == 'RECORD' and data.get('stream') == stream_name:
                    record = data.get('record', {})
                    # Clean empty dates
                    clean_record = {}
                    for key, value in record.items():
                        if value == '' and ('_at' in key or '_date' in key or '_time' in key):
                            clean_record[key] = None
                        else:
                            clean_record[key] = value
                    records.append(clean_record)
                    
            except json.JSONDecodeError:
                continue
    
    if not records:
        print(f"No records found for stream {stream_name}")
        return
    
    # Get all field names
    fieldnames = set()
    for record in records:
        fieldnames.update(record.keys())
    fieldnames = sorted(list(fieldnames))
    
    # Write to CSV
    csv_file = os.path.join(output_dir, f"{stream_name}.csv")
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"Created {csv_file} with {len(records)} records")

def main():
    json_file = "all_servicenow_data.json"
    output_dir = "output"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Analyze the file first
    stream_counts, total_records = analyze_json_file(json_file)
    
    if total_records == 0:
        print("No records found in the JSON file")
        return
    
    print(f"\nConverting {total_records} records to CSV files...")
    
    # Extract each stream to separate CSV
    for stream_name in stream_counts.keys():
        extract_stream_to_csv(json_file, stream_name, output_dir)
    
    print(f"\nConversion complete! Check the '{output_dir}' directory for CSV files.")

if __name__ == "__main__":
    main()