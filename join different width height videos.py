import argparse
import os
import cv2 as cv
import send2trash


def get_width_height(files):
    width_height = []
    for file in files:
        vcap = cv.VideoCapture(file)
        w = vcap.get(cv.CAP_PROP_FRAME_WIDTH)
        h = vcap.get(cv.CAP_PROP_FRAME_HEIGHT)
        width_height.append((w,h))

    return width_height


def find_max_width_height(width_height):
    max_w = max_h = 0
    for w,h in width_height:
        max_w = max(max_w, w)
        max_h = max(max_h, h)

    return (max_w, max_h)

def main(argv):
    width = argv.width
    height = argv.height
    folders = argv.folders

    for folder in folders:

        path, filename = os.path.split(folder)
        output = os.path.join(path, filename + ".mp4")


        files = [os.path.join(folder, file) for file in os.listdir(folder)]

        if width is None and height is None:
            width_height = get_width_height(files)

            max_width_height = find_max_width_height(width_height)

            if max_width_height[0] < max_width_height[1]:
                print("Width used as reference")
                width = int(max_width_height[0])
            else:
                print("Height used as reference")
                height = int(max_width_height[1])

        # temp variables to don't overwrite in loop
        wi = width if width else 0
        he = height if height else 0


        #find min output for widest / tallest video
        for file in files:
            vcap = cv.VideoCapture(file)
            w = vcap.get(cv.CAP_PROP_FRAME_WIDTH)
            h = vcap.get(cv.CAP_PROP_FRAME_HEIGHT)

            # don't overwrite to don't break None check in next iterations
            if width:
                ratio = w / width
                he = max(he, int((h / ratio) + 1))
            else:
                ratio = h / height
                wi = max(wi, int((w / ratio) + 1))

        final_width = wi
        final_height = he

        print(f"{final_width=}")
        print(f"{final_height=}")
        print(f"{output=}")
        # raise Exception()



        cmd = "ffmpeg "
        for file in files:
            cmd += f'-i "{file}" '
        cmd += '-filter_complex "'
        for i in range(len(files)):
            if width:
                cmd += f"[{i}:v]scale={final_width}:-2,pad=iw:{final_height}:0:(oh-ih)/2,setsar=1/1,setpts=PTS-STARTPTS[v{i}] ; "
                # cmd += f"[{i}:v]scale=-2:{height},pad={width}:ih:(ow-iw)/2:0,setsar=1/1,setpts=PTS-STARTPTS[v{i}] ; "
            else:
                cmd += f"[{i}:v]scale=-2:{final_height},pad={final_width}:ih:(ow-iw)/2:0,setsar=1/1,setpts=PTS-STARTPTS[v{i}] ; "
        for i in range(len(files)):
            cmd += f"[v{i}][{i}:a] "
        cmd += f'concat=n={len(files)}:v=1:a=1 [v] [a]" '
        cmd += f'-map "[v]" -map "[a]" -vsync 2 "{output}"'

        cmd_file = f"{output}.bat"
        with open(cmd_file, "w") as f:
            f.write(cmd)
        os.system(f'"{cmd_file}"')
        send2trash.send2trash(cmd_file)

        print(cmd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("folders", help="folders with files to join", nargs="+")
    parser.add_argument("--height", "-he", type=int, help="height of output video")
    parser.add_argument("--width", "-wi", type=int, help="width of output video")

    argv = parser.parse_args()

    # if bool(argv.height) + bool(argv.width) != 1:
        # parser.error("You must set only 1 argument")

    main(argv)