# Stern OFX Converter

<!--toc:start-->
- [Stern OFX Converter](#stern-ofx-converter)
  - [The project](#the-project)
  - [What it does](#what-it-does)
  - [What it does NOT do](#what-it-does-not-do)
  - [TODOS](#todos)
  - [License](#license)
<!--toc:end-->

## The project

OFX Conversion from other text data formats.

This application is a side-project that helps to perform an accurate accounting of assets, made necessary by those financial institutions that don't like to follow the standards of their own industry.

The naming was chosen because I've just re-watched Schindler's List and Stern is the name of the accountant.

## What it does

- Convert text files to OFX. Supported formats:
  - `csv`

## What it does NOT do

- Accounting processes for you
- Validate the information provided (for now)
- Any file formats other than `csv` (for now)

## TODOS

- Support additional file formats: [ADR001](/docs/001-support-additional-filetypes.md)
- Support base validations (issue TBD): DONE

## License

This project is distributed under a GNUGPLv3 [license](./LICENSE)
