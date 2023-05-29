# QGIS Playground

Ref: <https://courses.spatialthoughts.com/pyqgis-in-a-day.html>

## Pre-requisites

```bash
brew install --cask qgis
```

## Usage

```bash
make build
make start <http://localhost:81> # !!! does not work on m1 mac
```

## Notes

### reduce vector resolution (permanent)

- option 1: use `GRASS commands -> v.generalize` (choose `snake`)
- option 2: use `Vector geometry -> simplify`, set tolerance to `0.01`
