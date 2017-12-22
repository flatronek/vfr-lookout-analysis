from vfr_data_analysis.quaterion_utils import *
from vfr_data_analysis.constants_and_utils import *
from vfr_data_analysis.transition_matrix_utils import *
from vfr_data_analysis.ploting import *
from vfr_data_analysis.realTimeDataAnalysis import *
from vfr_data_analysis.samples import *

igcHeaderTimestamp = "timestamp"
vidTimeHeader = "VidTime"

igcSyncTimestamp = "2017-05-09 09:14:00"
vidSyncTimestamp = "2017-05-09 17:07:37"
vidSync1Timestamp = "2017-05-09 17:08:51"

# "2017-05-17 11:11:22 CEST"
# k2 "2017-05-09 17:05:00"
# k1 "2017-05-09 17:07:14"
# k1 vidSync2Timestamp = "2017-05-09 17:05:31"
# k2 vidSyncTimestamp = "2017-05-09 17:03:17"

def plot(dataFrame):
	x = dataFrame[file_header_real_time]
	values = list(dataFrame[dataFrame.columns[2]])

	title = "Glider Turnings"

	fig, ax = plt.subplots()
	fig.canvas.set_window_title(title)
	# fig.set_size_inches(24.4, 6)
	fig.set_size_inches(21, 9)
	plt.title(title)
	plt.gcf().autofmt_xdate()
	plt.plot(x, values, marker='.', linestyle='--')

	ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
	plt.grid()
	plt.legend(dataFrame.columns[2])
	plt.show()

def plot2(dataFrame):
	x = dataFrame[igcHeaderTimestamp]
	values = list(dataFrame[dataFrame.columns[8]])

	title = "Glider Turnings"

	fig, ax = plt.subplots()
	fig.canvas.set_window_title(title)
	# fig.set_size_inches(24.4, 6)
	fig.set_size_inches(21, 9)
	plt.title(title)
	plt.gcf().autofmt_xdate()
	plt.plot(x, values, marker='.', linestyle='--')

	ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
	plt.grid()
	plt.legend(dataFrame.columns[8])
	plt.show()

def plot3(igcDf, regDf):
	x = igcDf[vidTimeHeader]
	values = list(igcDf[igcDf.columns[9]])

	x2 = regDf[file_header_real_time]
	values2 = list(regDf[regDf.columns[2]])

	title = "Glider Turnings"

	fig, ax = plt.subplots()
	fig.canvas.set_window_title(title)
	# fig.set_size_inches(24.4, 6)
	fig.set_size_inches(21, 9)
	plt.title(title)
	plt.gcf().autofmt_xdate()
	plt.plot(x, values, marker='.', linestyle='--')

	plt.plot(x2, values2, marker='o', linestyle='-')

	ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
	plt.grid()
	plt.legend(igcDf.columns[9])
	plt.show()

def loadAndPlotIgcTurnings():
	filename_to_find = "igc_turnings.csv"
	try:
	    df = pd.DataFrame.from_csv(filename_to_find, index_col=False, parse_dates=[igcHeaderTimestamp])
	    print(df.columns)
	    print(df.index)

	    plot2(df)
	except FileNotFoundError:
	    print("!!!!!!", filename_to_find, "not present in current directory!!!!!!")

def loadAndPlotGliderTurnings():
    filename_to_find = "glider_turnings" + ".csv"
    try:
        df = pd.DataFrame.from_csv(filename_to_find, index_col=False, parse_dates=[file_header_real_time])
        print(df.columns)
        print(df.index)

        plot(df)
    except FileNotFoundError:
        print("!!!!!!", filename_to_find, "not present in current directory!!!!!!")


def loadAndPlotBoth():
	vidTime = datetime.datetime.strptime(vidSyncTimestamp, '%Y-%m-%d %H:%M:%S')
	igcTime = datetime.datetime.strptime(igcSyncTimestamp, '%Y-%m-%d %H:%M:%S')
	timeDiff = vidTime - igcTime

	print(timeDiff)

	filename_to_find = "igc_turnings.csv"

	igcDf = loadData("igc_turnings.csv", igcHeaderTimestamp)
	regDf = loadData("glider_turnings.csv", file_header_real_time)

	vidTimeMapColumn = [timeDiff + fileTime for fileTime in list(igcDf[igcHeaderTimestamp])]
	series = pd.to_datetime(vidTimeMapColumn)
	igcDf.insert(0, vidTimeHeader, series)

	plot3(igcDf, regDf)

def loadData(filename, dateColName):
	try:
	    df = pd.DataFrame.from_csv(filename, index_col=False, parse_dates=[dateColName])
	    return df
	except FileNotFoundError:
	    print("!!!!!!", filename_to_find, "not present in current directory!!!!!!")


if __name__ == "__main__":
	loadAndPlotBoth()
