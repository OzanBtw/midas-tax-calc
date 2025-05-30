# Midas Tax Calculator

![GitHub release (latest by date)](https://img.shields.io/github/v/release/OzanBtw/midas-tax-calc)
![GitHub issues](https://img.shields.io/github/issues/OzanBtw/midas-tax-calc)
![GitHub license](https://img.shields.io/github/license/OzanBtw/midas-tax-calc?style=flat)

A Python-based utility that helps users calculate their capital gains tax based on transaction data exported from the **Midas** investment app.

## Screenshots

![Screenshot 1](./source/screenshots/screen_1.png)
![Screenshot 2](./source/screenshots/screen_2.png)


## Features

- View income and tax summaries for a selected year
- Display monthly graph of annual income and individual ticker performance
- Monitor income from open (alive) orders
- Fast and efficient performance

## Compatibility
Tested on macOS Ventura and tested with limited coverage on Windows 11.

## Install & Setup
To install the project, run the following command in a terminal in your desired directory:

```bash
git clone https://github.com/OzanBtw/midas-tax-calc.git
cd midas-tax-calc
pip install -r requirements.txt
```

To run the project, run the following command in the same directory:
```bash
python main.py
```

> [!IMPORTANT]
> This project requires Java (OpenJDK 17 or later). Make sure `java` and `javac` are available in your system PATH. If you're using OpenJDK, you may need to manually set the `JAVA_HOME` environment variable.
> On macOS, this often works; on Windows or Linux, you may need to configure it manually.


To setup the project, you will need:

- An **EVDS API key**.[^1]
- Monthly account extracts (in PDF) from **Midas**.[^2]

After running the app for the first time, you will be prompted to enter and provide these.

> [!WARNING]
> All extracts must be included. Missing files may cause incorrect tax calculations or app crashes.

## License

Midas Tax Calculator is licensed under the Apache License, Version 2.0, as found in the [LICENSE](https://github.com/OzanBtw/midas-tax-calc/blob/main/LICENSE) file.



## FAQ

<details>
<summary><strong>How does the app calculate tax?</strong></summary>

The app uses the **FIFO (First-In, First-Out)** method to match buy and sell orders and calculate capital gains. Fees from the transactions are included in the calculation. It also adjusts gains based on the inflation rate. For more details, please see Article 30 of the [GENERAL MANAGEMENT ACCOUNTING REGULATION](https://mevzuat.gov.tr/mevzuat?MevzuatNo=20147052&MevzuatTur=21&MevzuatTertip=5).

</details>

<details>
<summary><strong>Does it include dividends or foreign income?</strong></summary> 

No — the current version only calculates taxes based on capital gains from **stock transactions**.

</details>

<details>
<summary> <strong>Is this tool affiliated with Midas?</strong></summary>

No. This is an **independent** open-source project. It is not affiliated with or endorsed by Midas.

</details>

<details>
<summary><strong>What happens if I forget to add an extract?</strong></summary>

Missing extracts can lead to:

- Incomplete income calculations  
- Crashes when resolving trades.

</details>


---

[^1]: To get the API key, visit the [EVDS website](https://evds2.tcmb.gov.tr/) and log in to generate your API key.

[^2]: Download all monthly extracts from **Midas** and place them in `source/extracts/pdf/` relative to the project root. 


> [!IMPORTANT]
> The tax calculations provided by this tool are <mark>**for informational purposes only**</mark>. Users are solely responsible for any decisions or consequences that result from using this data for official tax filings.
