import os
import re
import sys
import zipfile
from typing import List, Tuple, Dict


def scan_directory_for_mdx_files(directory_path: str) -> List[str]:
    return [
        file for file in sorted(os.listdir(directory_path)) if file.endswith(".mdx")
    ]


def extract_frontmatter_and_title(file_path: str) -> Tuple[str, str]:
    with open(file_path, encoding="utf-8") as file:
        content = file.read()

    frontmatter_pattern = r"^---\s*(.*?)\s*---"
    frontmatter_match = re.search(frontmatter_pattern, content, re.DOTALL)

    title_pattern = r"^title:\s*(.*)$"
    title = ""
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        title_match = re.search(title_pattern, frontmatter, re.MULTILINE)
        if title_match:
            title = title_match.group(1)

    return frontmatter_match.group(0), title.strip('"')


def sort_files_by_title(file_titles: Dict[str, str]) -> List[str]:
    return [file for file, _ in sorted(file_titles.items(), key=lambda x: x[1])]


def generate_table_of_contents(file_titles: Dict[str, str]) -> str:
    toc_lines = ["# Table of Contents\n"]
    for _, title in file_titles.items():
        link = title.lower().replace(" ", "-")
        toc_lines.append(f"- [{title}](#{link})")

    return "\n".join(toc_lines)


def concatenate_files(directory_path: str, sorted_files: List[str]) -> str:
    concatenated_content = []
    for file in sorted_files:
        file_path = os.path.join(directory_path, file)
        with open(file_path, encoding="utf-8") as mdx_file:
            content = mdx_file.read().split("---\n", 2)[-1]
            concatenated_content.append(content)

    return "\n".join(concatenated_content)


def process_mdx_files(directory_path: str, output_file_path: str) -> None:
    try:
        mdx_files = scan_directory_for_mdx_files(directory_path)
        if not mdx_files:
            print("No .mdx files found in the directory.")
            return

        file_titles = {}
        for mdx_file in mdx_files:
            file_path = os.path.join(directory_path, mdx_file)
            try:
                frontmatter, title = extract_frontmatter_and_title(file_path)
                file_titles[mdx_file] = title
            except Exception as e:
                print(f"Error processing file {mdx_file}: {e}")

        sorted_files = sort_files_by_title(file_titles)
        toc = generate_table_of_contents(file_titles)
        concatenated_content = concatenate_files(directory_path, sorted_files)

        final_content = toc + "\n\n" + concatenated_content
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(final_content)
        print(
            f"Processed {len(sorted_files)} files. Output saved to {output_file_path}."
        )

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python mdx_concatenator.py [directory_path] [output_file_path]")
        sys.exit(1)

    directory_path = sys.argv[1]
    output_file_path = sys.argv[2]

    process_mdx_files(directory_path, output_file_path)


if __name__ == "__main__":
    main()
