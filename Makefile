.PHONY: run
run: 
	./getDoc.py && ./parseDoc.py && ./setupDB.py && ./getData.py && ./parseData.py 

proto-mysql/protoc-gen-mysql: 
	cd proto-mysql && make

parsedData/raceinfo.dat: data/* parseData.py parseData/* proto/build/*.py
	python parseData.py

.PHONY: clean
clean:
	rm parsedData/* proto/build/*