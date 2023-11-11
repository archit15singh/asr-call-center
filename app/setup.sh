mkdir -p data
mkdir -p converted
mkdir -p transcriptions

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

brew install ffmpeg

git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
bash ./models/generate-coreml-model.sh medium.en
make clean
WHISPER_COREML=1 make -j
