import os
import re


def process_srt_file(idx, file_path, out_dir):
    with open(file_path, "r", encoding="utf8") as file:
        srt_data = file.read()

    fname = file_path.split("/")[-1].split(".")[0]
    # Split the SRT data into individual subtitle blocks
    subtitle_blocks = re.split(r"\n\s*\n", srt_data.strip())
    print(subtitle_blocks[1])

    # Divide subtitle blocks into 5-minute chunks
    chunk_size = 5 * 60  # 5 minutes in seconds
    current_chunk = ""
    current_chunk_time = 0
    chunk_number = 1
    et_ls = []
    et_ls.append(0)
    for block in subtitle_blocks:
        subtitle_lines = block.split("\n")

        # Extract the start and end time of the subtitle
        times = re.findall(r"\d{2}:\d{2}:\d{2}", subtitle_lines[0])

        if len(times) < 2:
            times = re.findall(r"\d{2}:\d{2}:\d{2}", subtitle_lines[1])

        print(times)
        start_time = sum(
            int(x) * 60**i for i, x in enumerate(reversed(times[0].split(":")))
        )
        end_time = sum(
            int(x) * 60**i for i, x in enumerate(reversed(times[1].split(":")))
        )
        et_ls.append(end_time)
        # If the subtitle belongs to the current chunk, append it to the chunk text
        if (et_ls[-1] - et_ls[0]) <= chunk_size:
            current_chunk += " ".join(subtitle_lines[2:]) + " "
            current_chunk_time += end_time - start_time
        else:
            # Write the current chunk to a text file
            output_file_path = (
                f"{out_dir}/{fname}_{idx}_min_{chunk_number}_to_{chunk_number+4}.txt"
            )
            with open(output_file_path, "w", encoding="utf8") as output_file:
                output_file.write(current_chunk.strip())

            # Start a new chunk and append the current subtitle to it
            current_chunk = " ".join(subtitle_lines[2:]) + " "
            current_chunk_time = end_time - start_time
            chunk_number += 5
            et_ls = []

        if chunk_number == 3:
            break

    # Write the last chunk to a text file
    output_file_path = (
        f"{out_dir}/{fname}_{idx}_min_{chunk_number}_to_{chunk_number+4}.txt"
    )
    with open(output_file_path, "w", encoding="utf8") as output_file:
        output_file.write(current_chunk.strip())

    print(f"Chunk {chunk_number} written to: {output_file_path}")


# Usage example
srt_file_path = "/home/oem/Vrushank/Cloud-project/Cloud-project/Succession_S01E01.srt"
process_srt_file(0, srt_file_path, "/home/oem/Vrushank/Cloud-project/Cloud-project/outputs")
