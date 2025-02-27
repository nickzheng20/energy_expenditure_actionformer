import os
import json
import cv2
import argparse as parser

def get_video_fps_and_duration(video_path):
    """
    get the fps and duration of a video
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Cannot open video: {video_path}")
        return None, None
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frame_count / fps if fps else 0
    cap.release()
    return fps, duration

def parse_annotation_file(json_file):
    """
    read json file and parse the annotations
    return a list of tuples (video_name, annotation_dict)
    annotation_dict is in the format
        {
            "label": collection_label,       
            "segment": [start_time, end_time],   
            "segment(frames)": None,         
            "label_id": None                
        }
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    annotations = []
    # iterate over all actions
    for collection in data.get("contains", []):
        # get action label
        collection_label = collection.get("label", "Unknown")
        # iterate over all items in the collection
        items = collection.get("first", {}).get("items", [])
        for ann in items:
            target_info = ann.get("target", {})
            target_id = target_info.get("id", "")
            # file:///C:/.../video.mp4#t=start,end
            if "#t=" in target_id:
                video_path, time_part = target_id.split("#t=")
                video_name = video_path.split("/")[-1].split(".")[0]
                # split the start and end time
                times = time_part.split(",")
                if len(times) == 2:
                    try:
                        start_time = float(times[0])
                        end_time = float(times[1])
                    except ValueError:
                        print(f"Value Error {ValueError} at：{time_part}")
                        continue
                else:
                    continue
                # create annotation dict
                annotation_dict = {
                    "label": collection_label,
                    "segment": [start_time, end_time],
                    "segment(frames)": None,
                    "label_id": None,
                }
                annotations.append((video_name, annotation_dict))
    return annotations

def main(args):
    annotations_folder = args.annotations_folder 

    video_annotations = {}

    label_to_id = {"Lifting": 0, "Carrying": 1, "Walking": 2, "Pushing": 3}
    next_label_id = 4

    # scan all json files in the folder
    for file in os.listdir(annotations_folder):
        if file.lower().endswith(".json"):
            json_file = os.path.join(annotations_folder, file)
            ann_list = parse_annotation_file(json_file)
            for video_name, ann in ann_list:
                if video_name not in video_annotations:
                    video_annotations[video_name] = []
                # assign label id
                label = ann["label"]
                if label not in label_to_id:
                    print(f"new label: {label}, assigning id: {next_label_id}")
                    label_to_id[label] = next_label_id
                    next_label_id += 1
                ann["label_id"] = label_to_id[label]
                video_annotations[video_name].append(ann)

    # "version": "Thumos14-30fps",
    # "database": {
    #     "video_test_0000004": {
    #         "subset": "Test",
    #         "duration": 33.83,
    #         "fps": 30.0,
    #         "annotations": [
    #             {
    #                 "label": "CricketBowling",
    #                 "segment": [
    #                     0.2,
    #                     1.1
    #                 ],
    #                 "segment(frames)": [
    #                     6.0,
    #                     33.0
    #                 ],
    #                 "label_id": 5
    #             },
    #             {
    #                 "label": "CricketBowling",
    output = {
        "version": f"EnergyExpenditure-30fps",
        "database": {}
    }
    # video_key_counter = 1
    for video_name, ann_list in video_annotations.items():
        # get video fps and duration
        video_path = os.path.join(annotations_folder, f"{video_name}.mp4")
        fps, duration = get_video_fps_and_duration(video_path)
        if fps is None:
            print(f"Cannot retrieve fps for {video_path}")
            continue

        # convert time to frames
        for ann in ann_list:
            start_time, end_time = ann["segment"]
            start_frame = round(start_time * fps)
            end_frame = round(end_time * fps)
            ann["segment(frames)"] = [float(start_frame), float(end_frame)]

        video_key = video_name  # change to video_key_counter mode?

        video_info = {
            "subset": args.subset,
            "duration": duration,
            "fps": fps,
            "annotations": ann_list
        }
        output["database"][video_key] = video_info

    # write the json file
    output_file = os.path.join(args.annotations_folder, args.output_file)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print(f"Converted json file saved at {output_file}")

if __name__ == '__main__':
    parser = parser.ArgumentParser()
    parser.add_argument('-s', '--subset', type=str, required=True, help='Subset name (e.g., Train, Test, Validation)')
    parser.add_argument('-f', '--annotations_folder', type=str, default='data/video_test')
    parser.add_argument('-o', '--output_file', type=str, default='videos_data.json')
    args = parser.parse_args()
    main(args)
