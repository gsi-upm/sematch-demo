export DATA_DIR=/tmp/sematch

mkdir -p $DATA_DIR/tfidf_index
mkdir -p $DATA_DIR/lsa_index

docker rm -v sematch 

docker run \
	--name sematch \
	-p 5000:5005 \
	-e SEMATCH_ENDPOINT=http://localhost:5000/api/ \
	-v $DATA_DIR:/sematch-demo/data \
	-ti \
	gsiupm/sematch:0.1 
