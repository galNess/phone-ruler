import argparse
import csv
import cv2
import os
import numpy as np


def parse_csv(filename):
    data = {}
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            model = row['model']
            data[model] = {
                'name': row['name'],
                'h_px': int(row['h_px']),
                'w_px': int(row['w_px']),
                'd_in': float(row['d_in'])
            }
    return data


def calculate_physical_height(d_in, h_px, w_px):
    aspect_ratio = h_px / w_px
    return d_in * aspect_ratio / np.sqrt(1 + aspect_ratio ** 2)


def get_available_models(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row['model'] for row in reader]


def draw_metric_ruler(img, start_y, direction, text_y, params, white, px_per_mm):
    for i in range(int(params['h_mm']) + 1):
        x = int(i * px_per_mm)
        if i % 10 == 0:  # Major tick (cm)
            cv2.line(img, (x, start_y), (x, start_y + direction * (80 + 200 * int(i == 0))), white, 7)
            cv2.putText(img, f"{i // 10}", (x - 32 * (i // 100 + 1), text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 3, white, 3)
        elif i % 5 == 0:  # Intermediate tick (5mm)
            cv2.line(img, (x, start_y), (x, start_y + direction * 60), white, 3)
        else:  # Minor tick (1mm)
            cv2.line(img, (x, start_y), (x, start_y + direction * 40), white, 2)


def draw_imperial_ruler(img, start_y, direction, text_y, params, white, px_per_inch):
    inches = params['h_mm'] / 25.4
    for i in range(int(inches * 8) + 1):
        x = int(i * px_per_inch / 8)
        if i % 8 == 0:  # Major tick (1 inch)
            cv2.line(img, (x, start_y), (x, start_y + direction * (80 + 200 * int(i == 0))), white, 7)
            cv2.putText(img, f"{i // 8}", (x - 32 * (i // 64 + 1), text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 3, white, 3)
        elif i % 4 == 0:  # 1/2 inch
            cv2.line(img, (x, start_y), (x, start_y + direction * 60), white, 3)
        elif i % 2 == 0:  # 1/4 inch
            cv2.line(img, (x, start_y), (x, start_y + direction * 50), white, 2)
        else:  # 1/8 inch
            cv2.line(img, (x, start_y), (x, start_y + direction * 40), white, 2)


def main():
    parser = argparse.ArgumentParser(description='Generate ruler images for phone models.')
    parser.add_argument('model', help='Phone model to generate ruler for')
    args = parser.parse_args()

    model = args.model
    csv_filename = 'phone_models.csv'
    images_dir = 'generated_images'
    os.makedirs(images_dir, exist_ok=True)

    available_models = get_available_models(csv_filename)
    if model not in available_models:
        print(f"Error: Model '{model}' not found. Available models are:")
        print(", ".join(available_models))
        return

    data = parse_csv(csv_filename)
    params = data[model]
    params['h_mm'] = 25.4 * calculate_physical_height(params['d_in'], params['h_px'],
                                                      params['w_px'])
    px_per_mm = params['h_px'] / params['h_mm']
    px_per_inch = px_per_mm * 25.4
    white = (255, 255, 255)

    for measure in ['metric', 'imperial']:
        img = np.zeros((params['w_px'], params['h_px'], 3), dtype=np.uint8)

        for ruler in ['top', 'bottom']:
            if ruler == 'top':
                start_y, direction, text_y = 0, 1, 170
            else:
                start_y, direction, text_y = params['w_px'] - 1, -1, params['w_px'] - 110

            if measure == 'metric':
                draw_metric_ruler(img, start_y, direction, text_y, params, white, px_per_mm)
            else:
                draw_imperial_ruler(img, start_y, direction, text_y, params, white, px_per_inch)

        if measure == 'metric':
            unit = "cm"
            ruler_type = "Metric"
        else:
            unit = "INCH"
            ruler_type = "Imperial"

        cv2.putText(img, unit, (320, params['w_px'] // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 8, white, 8)
        cv2.putText(img, f"{ruler_type} ruler for {params['name']}",
                    (320, params['w_px'] // 2 + 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 3, white, 3)

        cv2.imwrite(os.path.join(images_dir, f'Ruler_{model}_{measure}.png'), img)


if __name__ == "__main__":
    main()
