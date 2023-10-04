import sys
import time
from pathlib import Path

VALID_SECTIONS = [
    "kepala_putusan",
    "identitas",
    "riwayat_penahanan",
    "riwayat_perkara",
    "riwayat_tuntutan",
    "riwayat_dakwaan",
    "fakta",
    "fakta_hukum",
    "pertimbangan_hukum",
    "amar_putusan",
    "penutup",
]


def get_section_content(doc, section):
    start_section = f"<{section}>"
    end_section = f"</{section}>"

    start_index = doc.find(start_section)
    end_index = doc.find(end_section)

    content = ""

    if start_index != -1 and end_index != -1:
        content = doc[start_index + len(start_section) : end_index]
        content = content.replace("\n", " ")

    return content


def find_keyword_all_one(doc, keyword1):
    for section in VALID_SECTIONS:
        content = get_section_content(doc, section)

        if keyword1 in content:
            return True

    return False


def find_keyword_all(doc, keyword1, logic_op, keyword2):
    is_keyword1_found = False
    is_keyword2_found = False

    for section in VALID_SECTIONS:
        content = get_section_content(doc, section)

        if keyword1 in content:
            is_keyword1_found = True
        if keyword2 in content:
            is_keyword2_found = True

        if is_keyword1_found and is_keyword2_found:
            break

    if logic_op == "and":
        return is_keyword1_found and is_keyword2_found
    if logic_op == "or":
        return is_keyword1_found or is_keyword2_found

    return is_keyword1_found and not is_keyword2_found  # ANDNOT


def find_keyword_section(doc, section, keyword1, logic_op=None, keyword2=None):
    content = get_section_content(doc, section)

    if logic_op == "and":
        return keyword1 in content and keyword2 in content
    if logic_op == "or":
        return keyword1 in content or keyword2 in content
    if logic_op == "andnot":
        return keyword1 in content and keyword2 not in content

    return keyword1 in content


def get_attributes(doc):
    attribute_keys = {
        "province": 'provinsi="',
        "class": 'klasifikasi="',
        "subclass": 'sub_klasifikasi="',
        "institution": 'lembaga_peradilan="',
    }

    attributes = {}

    for attr_type, attr_key in attribute_keys.items():
        start = doc.find(attr_key)
        if start != -1:
            end = doc.find('"', start + len(attr_key))
            attr_value = doc[start + len(attr_key) : end]
            attributes[attr_type] = attr_value
        else:
            attributes[attr_type] = ""

    return attributes


def progress_bar(iterable, total=None, length=40):
    total = total or len(iterable)

    def show_progress(iteration):
        progress = iteration / total
        arrow = "=" * int(round(length * progress))
        spaces = " " * (length - len(arrow))
        sys.stdout.write(f"\r[{arrow}{spaces}] {int(progress * 100)}% ")
        sys.stdout.flush()

    for i, item in enumerate(iterable, 1):
        yield item
        show_progress(i)


def main():
    parent_dir = Path(__file__).resolve().parent
    dataset_dir = parent_dir / "indo-law" / "dataset"
    found_docs = 0

    if len(sys.argv) == 3:
        section = sys.argv[1].lower()
        keyword1 = sys.argv[2].lower()

        if section not in VALID_SECTIONS and section != "all":
            print("Section dokumen tidak benar.")
            return

        start = time.time()

        for doc_path in dataset_dir.iterdir():
            with open(doc_path, "r") as file:
                data = file.read()

                if section == "all":
                    is_found = find_keyword_all_one(data, keyword1)
                else:
                    is_found = find_keyword_section(data, section, keyword1)

                if is_found:
                    attributes = get_attributes(data)
                    province, clss, subclss, institution = attributes.values()
                    print(
                        f"{doc_path.name} {province:>15.15} {clss:>15.15} {subclss:>30.30} {institution:>20.20}"
                    )
                    found_docs += 1

        end = time.time()

        print(f"Banyaknya dokumen yang ditemukan = {found_docs}")
        print(f"{'Total waktu pencarian':32} = {end - start:.3f} detik")
    elif len(sys.argv) == 5:
        section = sys.argv[1].lower()
        keyword1 = sys.argv[2].lower()
        logic_op = sys.argv[3].lower()
        keyword2 = sys.argv[4].lower()

        if section not in VALID_SECTIONS and section != "all":
            print("Section dokumen tidak benar.")
            return

        valid_logic_ops = ["and", "or", "andnot"]

        if logic_op not in valid_logic_ops:
            print("Mode harus berupa AND, OR atau ANDNOT.")
            return

        start = time.time()

        for doc_path in dataset_dir.iterdir():
            with open(doc_path, "r") as file:
                data = file.read()

                if section == "all":
                    is_found = find_keyword_all(data, keyword1, logic_op, keyword2)
                else:
                    is_found = find_keyword_section(
                        data, section, keyword1, logic_op, keyword2
                    )

                if is_found:
                    attributes = get_attributes(data)
                    province, clss, subclss, institution = attributes.values()
                    print(
                        f"{doc_path.name} {province:>15.15} {clss:>15.15} {subclss:>30.30} {institution:>20.20}"
                    )
                    found_docs += 1

        end = time.time()

        print(f"Banyaknya dokumen yang ditemukan = {found_docs}")
        print(f"{'Total waktu pencarian':32} = {end - start:.3f} detik")
    else:
        print("Argumen program tidak benar.")


if __name__ == "__main__":
    main()
