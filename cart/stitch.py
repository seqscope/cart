import argparse
from cv2 import cv2
from imutils import paths


def main():
    parser = argparse.ArgumentParser(
        description="Stitch histology images")
    parser.add_argument(
        "-i", "--input", type=str, required=True,
        help="input folder for histology images")
    parser.add_argument(
        "-o", "--output", type=str, required=True,
        help="output tiff path")
    args = parser.parse_args()

    input_dir = args.input 
    output = args.output
    image_paths = sorted(list(paths.list_images(input_dir)))
    print(image_paths, len(image_paths))
    stitch(image_paths, output)


def stitch(image_paths, output):
    images = []
    for image_path in image_paths:
        image = cv2.imread(image_path)
        images.append(image)
    stitcher = cv2.Stitcher.create(cv2.Stitcher_SCANS)
    status, stitched = stitcher.stitch(images)
    print(status)
    if status == 0:
        cv2.imwrite(output, stitched)

if __name__=='__main__':
    main()
