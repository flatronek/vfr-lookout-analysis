# vfr-analysis

## Generating video subtitles

Generating subtitles is done with `wesu-app-data-quality-analysis/generate_subtitles.py` script. Beforehand you need to have Head Turnings data generated and saved in a file named `head_turnings.csv` (this can be done with `perform_detection.py` script.

1. Edit the script and change `vidStartTime` variable value to the time displayed at the beginning of the video you want the subtitles for.
2. Go to the folder where you have your `head_turnings.csv` data.
3. Run the script. The result is stored in `subtitles.srt` file.