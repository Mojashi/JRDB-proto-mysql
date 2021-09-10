.PHONY: run

run: proto-mysql/protoc-gen-mysql
	./getDoc.py && ./parseDoc.py && ./setupDB.py && ./getData.py && ./parseData.py 

proto-mysql/protoc-gen-mysql: 
	cd proto-mysql && make