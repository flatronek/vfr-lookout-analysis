from vfr_data_analysis.quaterion_utils import *
from vfr_data_analysis.constants_and_utils import *
from vfr_data_analysis.transition_matrix_utils import *
from vfr_data_analysis.ploting import *
from vfr_data_analysis.realTimeDataAnalysis import *
from vfr_data_analysis.samples import *

vidStartTime = "2017-05-09 16:55:32"
vidEndTime = "2017-05-09 17:25:32"

fileHeaderSubtitleTime = 'Subtitle Time'


def strfdelta(tdelta):
    hours, remainder = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    millis = int(tdelta.microseconds / 1000)
    return '{}:{}:{},{}'.format(hours, minutes, seconds, millis)


def generateSubtitles():
    df = loadData("head_turnings.csv", file_header_real_time)
    headTurnings = df[df[file_header_head_turning] == 1]

    vidDateTime = datetime.datetime.strptime(vidStartTime, '%Y-%m-%d %H:%M:%S')

    vidTimeMapColumn = [fileTime - vidDateTime for fileTime in list(headTurnings[file_header_real_time])]
    # series = pd.to_datetime(vidTimeMapColumn)
    headTurnings.insert(0, fileHeaderSubtitleTime, vidTimeMapColumn)

    # print(headTurnings)

    f = open('subtitles.srt', 'w')
    for index, row in headTurnings.iterrows():
        f.write('{}\n'.format(index))
        f.write('{} --> {}\n'.format(strfdelta(row[fileHeaderSubtitleTime]),
                                     strfdelta(row[fileHeaderSubtitleTime] + pd.Timedelta(milliseconds=150))))
        f.write('1\n\n')

    f.close()


def loadData(filename, dateColName):
    try:
        df = pd.DataFrame.from_csv(filename, index_col=False, parse_dates=[dateColName])
        return df
    except FileNotFoundError:
        print("!!!!!!", filename, "not present in current directory!!!!!!")


if __name__ == "__main__":
    generateSubtitles()
