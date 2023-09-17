import os
import json
import cv2
import argparse

parser = argparse.ArgumentParser(usage="Run with -h for help",
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-i","--images_dir", required=True)
parser.add_argument("-a","--annotations_dir", required=True)

args = parser.parse_args()

images_dir = args.images_dir
annotations_dir = args.annotations_dir

if not os.path.exists(images_dir):
    print("[ERROR] Directory %s does not exist." % images_dir)
    exit(-1)

if not os.path.exists(annotations_dir):
    print("[ERROR] Directory %s does not exist." % annotations_dir)
    exit(-1)

pcb_defect_labels = ["open", "short", "mousebite", "spur", "copper", "pin-hole"]

directory_images = os.fsencode(images_dir)
directory_labels = os.fsencode(annotations_dir)

# append _test after all the annotations.
for file in os.listdir(directory_labels):
    filename = os.fsdecode(file)
    img_path = (os.path.join(directory_labels.decode("utf-8"), filename))
    base=os.path.basename(img_path)
    file_name_without_ext = os.path.splitext(base)[0] # name of the file without the extension
    os.rename(img_path,(os.path.join(directory_labels.decode("utf-8"), file_name_without_ext+"_test"+"."+"txt")))

categories = []
for j,label in enumerate(pcb_defect_labels):
    label = label.strip()
    categories.append({"id":j+1,"name":label})

write_json_context = dict()
write_json_context['info'] = {'description': '', 'url': '', 'version': '', 'year': 2021, 'contributor': '', 'date_created': '2021-02-12 11:00:08.5'}
write_json_context['licenses'] = [{'id': 1, 'name': None, 'url': None}]
write_json_context['categories'] = categories
write_json_context['images'] = []
write_json_context['annotations'] = []

# Read the bounding boxes from (.txt) and store in COCO format
file_number = 1
num_bboxes = 1
for file in os.listdir(directory_images):
    filename = os.fsdecode(file)
    img_path = (os.path.join(directory_images.decode("utf-8"), filename))
    base=os.path.basename(img_path)
    file_name_without_ext = os.path.splitext(base)[0] # name of the file without the extension
    annotation_path  = os.path.join(directory_labels.decode("utf-8"), file_name_without_ext+ "." + 'txt')
    img_name = os.path.basename(img_path) # name of the file without the extension
    img_context = {}
    height,width = cv2.imread(img_path).shape[:2]
    img_context['width'] = width
    img_context['height'] = height
    img_context['id'] = filename # image id #file_number
    img_context['file_name'] = filename
    write_json_context['images'].append(img_context)
    
    with open(annotation_path,'r') as f2:
        lines2 = f2.readlines() 

    for i,line in enumerate(lines2): # for loop runs for number of annotations labelled in an image
        line = line.split(' ')
        bbox_dict = {}
        x_bbox,y_bbox,x2,y2,class_id= line[0:]
        x_bbox,y_bbox,x2,y2,class_id= float(x_bbox),float(y_bbox),float(x2),float(y2),int(class_id)
        width_bbox = x2-x_bbox
        height_bbox = y2-y_bbox
        bbox_dict['id'] = num_bboxes
        bbox_dict['image_id'] = filename
        bbox_dict['category_id'] = class_id
        bbox_dict['iscrowd'] = 0 
        bbox_dict['area']  = height_bbox * width_bbox
        if x_bbox <0: #check if x_coco extends out of the image boundaries
            x_bbox = 1
        if y_bbox <0: #check if y_coco extends out of the image boundaries
            y_bbox = 1
        bbox_dict['bbox'] = [x_bbox,y_bbox,width_bbox,height_bbox]
        bbox_dict['segmentation'] = []
        write_json_context['annotations'].append(bbox_dict)
        num_bboxes+=1
    file_number = file_number+1
   

# Delete existing .txt file
for f in os.listdir(annotations_dir):
    os.remove(os.path.join(annotations_dir, f))

coco_format_save_path = os.path.join(annotations_dir, 'instances.json')
with open(coco_format_save_path,'w') as fw:
    json.dump(write_json_context,fw)

print("JSON file saved at %s" % coco_format_save_path )