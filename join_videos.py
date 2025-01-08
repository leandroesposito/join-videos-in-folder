import os
import argparse
from units import convert_bytes

def listFiles(dirpath:str) -> list:
    """
    List all files inside folder and sort
    """
    filespath = []
    for dir, _, filenames in os.walk(dirpath):
        files = filenames.copy()
        # extract filename without extention and check if is a number
        if os.path.splitext(os.path.basename(filenames[0]))[0].isdigit():
            # sort filenames as numbers
            sorted_files = sorted(files, key=lambda f: int(os.path.splitext(os.path.basename(f))[0]))
        else:
            # sort files by names
            sorted_files = sorted(files)

        filespath += [os.path.join(dir,file) for file in sorted_files]

    return filespath

def main(argv):
    dirpaths:list = argv.path
    drive:str = argv.drive + ":" if argv.drive is not None else None
    audio_only = argv.audio_only
    overwrite = argv.overwrite

    processed:list = []
    while len(dirpaths) > 0:
        dirpath = dirpaths.pop(0)
        try:
            target_folder, target_filename = os.path.split(dirpath)
            if drive is not None:
                target_folder = os.path.join(drive, os.path.splitdrive(target_folder)[1])

            txt_file_path = os.path.join(dirpath, "fileslist.txt")
            if os.path.isfile(txt_file_path):
                os.remove(txt_file_path)
            files = listFiles(dirpath)
            # generate text file formatted for ffmpeg listing all videos to join
            with open(txt_file_path, "w", encoding="utf-8") as f:
                f.writelines([f"file '{f}'\n" for f  in files])

            # generate ffmpeg command string
            command = "ffmpeg"

            if overwrite:
                command += " -y"
            else:
                command += " -n"

            command += f' -f concat -safe 0 -i "{txt_file_path}"'

            if audio_only:
                command += " -vn -acodec copy"
                output_path = os.path.join(target_folder, target_filename) + ".aac"
            else:
                command += " -c copy"
                output_path = os.path.join(target_folder, target_filename) + ".mp4"

            command += f' "{output_path}"'

            print(command)

            # run command
            os.system(command)
            print()
        except Exception as e:
            print(e.with_traceback())
            os.remove(txt_file_path)
            break
        processed.append(dirpath)
        os.remove(txt_file_path)

    # show orignal files size, original folder name and generated file name with final file size
    # and percentage of file size in relstion with original files
    for dirpath in processed:
        folder_size = sum((os.path.getsize(os.path.join(dirpath, f)) for f in os.listdir(dirpath)))

        target_folder, target_filename = os.path.split(dirpath)
        if drive is not None:
                target_folder = os.path.join(drive, os.path.splitdrive(target_folder)[1])

        if audio_only:
            file_name = os.path.join(target_folder, target_filename + ".aac")
        else:
            file_name = os.path.join(target_folder, target_filename + ".mp4")

        file_size = os.path.getsize(file_name)

        print(f"Folder: {dirpath}")
        print(f"File: {file_name}")
        print(f"Folder size: {convert_bytes(folder_size)}")
        print(f"File size: {convert_bytes(file_size)}")

        print(f"{int(file_size / folder_size * 100)}% of original files size")
        if int(file_size / folder_size * 100) < 90:
            print ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Join video files inside a folder using ffmpeg without reencoding so make sure they are compatible")

    parser.add_argument("path", nargs="+", help="Directory with videos to join")
    parser.add_argument("--drive", "-d", help="Drive to output videos")
    parser.add_argument("--audio-only", "-a", action="store_true", help="Create only audio file")
    parser.add_argument("--overwrite", "-ov", action="store_true", help="Overwrite file if exist, skip by default")

    argv = parser.parse_args()
    print(argv)

    main(argv)