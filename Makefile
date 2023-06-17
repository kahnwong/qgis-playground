build:
	QGIS_BACKEND=OGR /Applications/QGIS.app/Contents/MacOS/bin/python3 src/generate_qgis_manifest.py
build-postgis-backend: start-db
	pipenv run python3 src/geojson_to_postgis.py
	QGIS_BACKEND=POSTGIS /Applications/QGIS.app/Contents/MacOS/bin/python3 src/generate_qgis_manifest.py

start:
	docker compose up
start-db:
	docker compose -f docker-compose-postgres.yaml up -d
