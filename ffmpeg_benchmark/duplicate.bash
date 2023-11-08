for i in {1..333}; do
  cp -v file_example_WAV_1MG.wav "file_example_WAV_1MG_copy_$i.wav"
  cp -v file_example_WAV_2MG.wav "file_example_WAV_2MG_copy_$i.wav"
  cp -v file_example_WAV_5MG.wav "file_example_WAV_5MG_copy_$i.wav"
done
