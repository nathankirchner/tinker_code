import os
import csv
import matplotlib.pyplot as plt
from PIL import Image
from ultralytics import YOLO
import tkinter as tk
from tkinter import filedialog, messagebox


def select_directory(prompt):
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title=prompt)
    return directory

def select_file(prompt):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=prompt)
    return file_path

# Initialize YOLO model
model = YOLO('yolov8n.pt')  # Load YOLOv8 nano model

# Try to find specific image directory first, fall back to user selection if not found
default_image_dir = "/Users/nathankirchner/Workstuff/Projects/GWA_Reviewer/20250214 Raw Data IMS"
if os.path.exists(default_image_dir):
    image_dir = default_image_dir
else:
    image_dir = select_directory("Folder '20250214 Raw Data IMS' not found. Please select directory containing images to analyze")
if not image_dir:
    raise ValueError("No directory selected")

# Try to find specific categories file first, fall back to user selection if not found
default_categories_file = "/Users/nathankirchner/Workstuff/Projects/GWA_Reviewer/20250214 summary_statistics_categories.txt"
if os.path.exists(default_categories_file):
    categories_file = default_categories_file
else:
    categories_file = select_file("Categories file not found. Please select categories.txt file")
if not categories_file:
    raise ValueError("No categories file selected")

# Read categories
with open(categories_file, 'r') as f:
    categories = [line.strip() for line in f.readlines()]

# Initialize counters
category_counts = {category: 0 for category in categories}
total_images = 0
person_count_distribution = {0: 0}  # Initialize with 0 people count

# Initialize before the image processing loop
image_data_list = []

# Analyze images
for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(image_dir, filename)
        try:
            # Analyze image
            print(f"Analysing {filename}")
            results = model(image_path)[0]  # Get results for first image
            detected_classes = results.boxes.cls  # Get class indices
            class_names = [results.names[int(cls)] for cls in detected_classes]  # Convert to class names
            
            # Count people in this image
            people_count = class_names.count('person')
            print(f"FOUND: {class_names} (People count: {people_count})")
            
            # Update person count distribution
            if people_count in person_count_distribution:
                person_count_distribution[people_count] += 1
            else:
                person_count_distribution[people_count] = 1

            # Count matching categories (check all detected objects)
            for detected_class in class_names:
                for category in categories:
                    if category.lower() in detected_class.lower():
                        category_counts[category] += 1
                        break

            # Add image data to list
            image_data = {
                'elements': class_names,
                'size': os.path.getsize(image_path),
                'anomalies': []  # Add anomalies if you detect any
            }
            image_data_list.append(image_data)
            
            total_images += 1
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

# Create first pie chart (original categories)
plt.figure(figsize=(10, 8))
labels = [f"{cat} ({count})" for cat, count in category_counts.items() if count > 0]
values = [count for count in category_counts.values() if count > 0]
plt.pie(values, labels=labels, autopct='%1.1f%%')
plt.title('Image Category Distribution')

# Try to find specific output directory first, fall back to user selection if not found
default_save_dir = "/Users/nathankirchner/Workstuff/Projects/GWA_Reviewer/OUTPUT"
if os.path.exists(default_save_dir):
    save_dir = default_save_dir
else:
    save_dir = select_directory("Folder 'OUTPUT' not found. Please select directory to save results")
if not save_dir:
    raise ValueError("No save directory selected")

# Save first pie chart
chart_path = os.path.join(save_dir, 'category_distribution_pie_chart.png')
plt.savefig(chart_path)
plt.close()

# Create second pie chart (person count distribution)
plt.figure(figsize=(10, 8))
person_labels = [f"{count} people ({freq})" for count, freq in person_count_distribution.items()]
person_values = list(person_count_distribution.values())
plt.pie(person_values, labels=person_labels, autopct='%1.1f%%')
plt.title('People Count Distribution')

# Save second pie chart
person_chart_path = os.path.join(save_dir, 'person_count_distribution_pie_chart.png')
plt.savefig(person_chart_path)
plt.close()

# Save CSV with both distributions
csv_path = os.path.join(save_dir, 'summary_statistics.csv')
with open(csv_path, 'w', newline='') as f:
    writer = csv.writer(f)
    # First section: Category distribution
    writer.writerow(['Category Distribution'])
    writer.writerow(['Category', 'Count', 'Percentage'])
    for category, count in category_counts.items():
        percentage = (count / total_images * 100) if total_images > 0 else 0
        writer.writerow([category, count, f"{percentage:.1f}%"])
    
    # Add spacing between sections
    writer.writerow([])
    writer.writerow([])
    
    # Second section: Person count distribution
    writer.writerow(['Person Count Distribution'])
    writer.writerow(['Number of People', 'Number of Images', 'Percentage'])
    for person_count, frequency in person_count_distribution.items():
        percentage = (frequency / total_images * 100) if total_images > 0 else 0
        writer.writerow([person_count, frequency, f"{percentage:.1f}%"])

# Open both pie charts with default viewer
if os.name == 'nt':  # Windows
    os.startfile(chart_path)
    os.startfile(person_chart_path)
else:  # macOS and Linux
    import subprocess
    opener = 'open' if os.name == 'posix' else 'xdg-open'
    subprocess.call([opener, chart_path])
    subprocess.call([opener, person_chart_path])

# messagebox.showinfo("Complete", "Analysis complete! Check the selected directory for results.")

# # Generate summary of findings across all images
# print("\n=== ANALYSIS SUMMARY ACROSS ALL IMAGES ===")

# # Common elements
# print("\nCommon Elements:")
# common_elements = set.intersection(*[set(img_data['elements']) for img_data in image_data_list])
# for element in common_elements:
#     print(f"- {element}")

# # Differences
# print("\nDifferences:")
# all_elements = set.union(*[set(img_data['elements']) for img_data in image_data_list])
# varying_elements = all_elements - common_elements
# for element in varying_elements:
#     count = sum(1 for img_data in image_data_list if element in img_data['elements'])
#     print(f"- {element} (present in {count}/{len(image_data_list)} images)")

# # Anomalies
# print("\nAnomalies:")
# anomalies_found = False
# for i, img_data in enumerate(image_data_list):
#     if img_data['anomalies']:
#         anomalies_found = True
#         print(f"Image {i+1}:")
#         for anomaly in img_data['anomalies']:
#             print(f"- {anomaly}")
# if not anomalies_found:
#     print("No anomalies detected")

# # Trends
# print("\nTrends:")
# # Analyze size trends
# sizes = [img_data['size'] for img_data in image_data_list]
# avg_size = sum(sizes) / len(sizes)
# print(f"- Average image size: {avg_size:.2f} bytes")

# # Analyze element count trends
# element_counts = [len(img_data['elements']) for img_data in image_data_list]
# avg_elements = sum(element_counts) / len(element_counts)
# print(f"- Average number of elements per image: {avg_elements:.1f}")

# # Check for consistent patterns
# if len(common_elements) > len(varying_elements):
#     print("- Images show high consistency in elements")
# elif len(varying_elements) > len(common_elements):
#     print("- Images show significant variation in elements")

# print("\n" + "="*40)
