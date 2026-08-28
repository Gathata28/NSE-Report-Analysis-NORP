# Market-Data Licensing and Attribution Register

## Scope

This register covers the 32 CSV datasets integrated from the user-supplied NSE market-data archive. The public NORP repository contains the permitted market-data extracts and their provenance metadata only. Only the permitted source datasets and attribution metadata are included in the public repository.

## Dataset license

The attached source records identify the historical NSE releases as **CC BY 4.0** and provide the following release-level attribution. The same attribution is stored in the `market_dataset` table and in `data/market_data/market_data_manifest.json`.

| Coverage | Source | Attribution | License |
| --- | --- | --- | --- |
| 2007–2012 | [Mendeley Data 5hk4zw32f5](https://data.mendeley.com/datasets/5hk4zw32f5/1) | Wanjawa, Barack. *Nairobi Securities Exchange All Stocks Prices 2007–2012*. Version 1. | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| 2013–2020 | [Mendeley Data 73rb78pmzw](https://data.mendeley.com/datasets/73rb78pmzw/2) | Wanjawa, Barack. *Kenya Nairobi Securities Exchange (NSE) All Stocks Prices 2013–2020*. Version 2. | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| 2021 | [Mendeley Data 97hkwn5y3x](https://data.mendeley.com/datasets/97hkwn5y3x/4) | Wanjawa, Barack. *Kenya Nairobi Securities Exchange (NSE) — All Stocks Prices 2021*. Version 4. | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| 2022 | [Mendeley Data jmcdmnyh2s](https://data.mendeley.com/datasets/jmcdmnyh2s/2) | Wanjawa, Barack. *Kenya Nairobi Securities Exchange (NSE) All Stocks Prices 2022*. Version 2. | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| 2023–2024 | [Mendeley Data ss5pfw8xnk](https://data.mendeley.com/datasets/ss5pfw8xnk/3) | Wanjawa, Barack. *Kenya Nairobi Securities Exchange (NSE) All Stocks Prices 2023–2024*. Version 3. | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| 2025 | [Mendeley Data 2b63rx67xt](https://data.mendeley.com/datasets/2b63rx67xt/2) | Wanjawa, Barack. *Kenya Nairobi Securities Exchange (NSE) All Stocks Prices 2025*. Version 2. | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| 2026 January–June | [Mendeley Data hvmhnp7f9r](https://data.mendeley.com/datasets/hvmhnp7f9r/1) | Wanjawa, Barack. *Kenya Nairobi Securities Exchange (NSE) All Stocks Prices 2026*. Version 1. | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

## Compliance notes

The repository retains attribution, source URL, release period, original filename, archive origin, SHA-256 checksum, and source-row fidelity for every dataset. Duplicate files from separate packages are kept as separate source datasets rather than silently deduplicated. The MIT license at the repository root applies to project code and documentation; it does not replace or override the CC BY 4.0 terms for the market-data files.

The market data should be redistributed with this attribution register and the applicable CC BY 4.0 notice. Users must comply with the license’s attribution and indication-of-changes requirements. The database stores parsed and normalized columns alongside each original row as JSON; the original values remain available for verification.
