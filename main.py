#!/usr/bin/env python3

import sys

from pdf2image import convert_from_path, convert_from_bytes

# Minimum fraction of the full page width that each staff takes up. Setting this
# too low will cause stuff other than staff lines (e.g. big legato lines) to be
# misdetected as staff lines, while setting it too high will cause actual staff
# lines to go undetected.
MIN_STAFF_WIDTH = 0.6

# Maximum value in the range [0, 255] to consider black (as opposed to white)
MAX_BLACK = 64

# Whether to convert staves from treble to bass (as opposed to the opposite
# direction)
TREBLE_TO_BASS = True


def avg(iterable):
    result = 0
    num_items = 0
    for item in iterable:
        result += item
        num_items += 1
    return result / num_items


def main():
    for pdf in sys.argv[1:]:
        pages = []
        for page in convert_from_path(pdf):
            # Convert to grayscale
            page = page.convert("L")
            original = page.copy()
            pages.append(page)

            # Get image dimensions
            width, height = page.size

            # Find long horizontal black rows
            black_rows = []
            bookends = []
            was_originally_black = lambda x, y: original.getpixel((x, y)) < MAX_BLACK
            for y in range(height):
                first_black_of_run = None
                for x in range(width):
                    if not was_originally_black(x, y):
                        first_black_of_run = None
                        continue
                    if first_black_of_run is None:
                        first_black_of_run = x
                    if x - first_black_of_run > MIN_STAFF_WIDTH * width:
                        black_rows.append(y)
                        if bookends:
                            continue
                        last_black_of_run = first_black_of_run
                        for i in range(x, width):
                            if was_originally_black(i, y):
                                last_black_of_run = i
                        bookends = [first_black_of_run, last_black_of_run]
                        break
            assert black_rows, "No lines found!"
            assert bookends, "Unable to determine staff bookends!"

            # Bundle black rows into staff lines
            last_seen = -2
            lines = []
            for black_row in black_rows:
                if black_row - last_seen == 1:
                    lines[-1].append(black_row)
                elif black_row - last_seen > 1:
                    lines.append([black_row])
                last_seen = black_row
            assert len(lines) % 5 == 0, "Number of lines not divisible by 5!"

            # Determine average line height
            line_height = int(round(sum(len(line) for line in lines) / len(lines)))

            # Chunk lines into staves
            staves = [lines[i * 5 : (i + 1) * 5] for i in range(int(len(lines) / 5))]

            # Determine average space height
            space_height = int(
                round(avg((avg(staff[-1]) - avg(staff[0])) / 4 for staff in staves))
            )

            # Transform staves
            for staff in staves:
                # Erase line
                line = staff[-1 if TREBLE_TO_BASS else 0]
                for black_row in line:
                    for x in range(width):
                        num_black_neighbors = 0
                        if black_row - 1 not in line and was_originally_black(
                            x, black_row - 1
                        ):
                            num_black_neighbors += 1
                        if black_row + 1 not in line and was_originally_black(
                            x, black_row + 1
                        ):
                            num_black_neighbors += 1
                        if num_black_neighbors < 2:
                            page.putpixel(
                                (x, black_row), 255 - num_black_neighbors * 128
                            )

                # Add line
                black_row = staff[0][0] if TREBLE_TO_BASS else staff[-1][-1]
                direction = -1 if TREBLE_TO_BASS else 1
                for y in range(
                    black_row + direction * space_height,
                    black_row + direction * (space_height + line_height),
                    direction,
                ):
                    for x in range(*bookends):
                        page.putpixel((x, y), 0)

        # Save PDF
        pages[0].save(
            pdf.replace(".pdf", ".bass.pdf"),
            "PDF",
            append_images=pages[1:],
            resolution=100.0,
            save_all=True,
        )


if __name__ == "__main__":
    main()
