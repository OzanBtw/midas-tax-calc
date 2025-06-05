import os

def _get_number(text):
    if "Ocak" in text:
        return text.replace("Ocak", "01")
    if "Şubat" in text:
        return text.replace("Şubat", "02")
    if "Mart" in text:
        return text.replace("Mart", "03")
    if "Nisan" in text:
        return text.replace("Nisan", "04")
    if "Mayıs" in text:
        return text.replace("Mayıs", "05")
    if "Haziran" in text:
        return text.replace("Haziran", "06")
    if "Temmuz" in text:
        return text.replace("Temmuz", "07")
    if "Ağustos" in text:
        return text.replace("Ağustos", "08")
    if "Eylül" in text:
        return text.replace("Eylül", "09")
    if "Ekim" in text:
        return text.replace("Ekim", "10")
    if "Kasım" in text:
        return text.replace("Kasım", "11")
    if "Aralık" in text:
        return text.replace("Aralık", "12")
    else:
        return "?"+text

def _get_month(text):
    if "01_" in text:
        return text.replace("01_", "Ocak_")
    if "02_" in text:
        return text.replace("02_", "Şubat_")
    if "03_" in text:
        return text.replace("03_", "Mart_")
    if "04_" in text:
        return text.replace("04_", "Nisan_")
    if "05_" in text:
        return text.replace("05_", "Mayıs_")
    if "06_" in text:
        return text.replace("06_", "Haziran_")
    if "07_" in text:
        return text.replace("07_", "Temmuz_")
    if "08_" in text:
        return text.replace("08_", "Ağustos_")
    if "09_" in text:
        return text.replace("09_", "Eylül_")
    if "10_" in text:
        return text.replace("10_", "Ekim_")
    if "11_" in text:
        return text.replace("11_", "Kasım_")
    if "12_" in text:
        return text.replace("12_", "Aralık_")

def _sortDates(text):

    split_up = text.split('_')

    return split_up[1], split_up[0]


def get_paths():
    if not os.path.isdir('source/extracts/pdf'):
        os.mkdir('source/extracts/pdf')

    lis = os.listdir('source/extracts/pdf')

    master = []
    for l in lis:
        l = l.replace("Midas_Ekstre_", "")
        l = l.replace(".pdf", "")
        master.append(l)


    for m in master:
        if "." == m[0]:
            master.remove(m)

    master = list(map(_get_number, master))
    master.sort(key=_sortDates)

    start = master[0]
    end = master[-1]
    master = list(map(_get_month, master))

    master2 = []
    for l in master:
        l = f"Midas_Ekstre_{l}"
        master2.append(l)
    return master2, start, end


if __name__ == "__main__":
    print(get_paths())

