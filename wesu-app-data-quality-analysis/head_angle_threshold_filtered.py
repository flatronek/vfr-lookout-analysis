from vfr_data_analysis.realTimeDataAnalysis import *
from vfr_data_analysis.samples import *

# 2017-05-17
head_neutral_acc_vector = pd.np.array([-1000, -125, 170])
glider_neutral_acc_vector = pd.np.array([-200, -54, 970])

head_gyro_calibration_vector = pd.np.array([0.4, -0.9, -1.6])
glider_gyro_calibration_vector = pd.np.array([1.6, -3.6, -3.3])

# 2017-05-18
# head_neutral_acc_vector = pd.np.array([-850, 500, 0])
# glider_neutral_acc_vector = pd.np.array([240, 20, 1000])
#
# head_gyro_calibration_vector = pd.np.array([0.5, -1.3, -1.1])
# glider_gyro_calibration_vector = pd.np.array([0.3, -3.5, -2.7])

# peak detection params
lag = 20
angleThreshold = 20
influence = 0.05


def plotZAxis(dataFrame1, title = "Gyroscope data"):
    x1 = dataFrame1[file_header_real_time]
    values1 = dataFrame1[file_header_Z_dps]

    fig, ax = plt.subplots()
    fig.canvas.set_window_title(title)
    # fig.set_size_inches(24.4, 6)
    fig.set_size_inches(21, 9)
    plt.title(title)
    plt.gcf().autofmt_xdate()

    plt.plot(x1, values1, marker='.', linestyle='--')

    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.legend(["Z-axis"])
    plt.show()


def plotZAxis2(dataFrame1, dataFrame2, label1="DF1", label2="DF2"):
    x1 = dataFrame1[file_header_real_time]
    values1 = dataFrame1[file_header_Z_dps]

    x2 = dataFrame2[file_header_real_time]
    values2 = dataFrame2[file_header_Z_dps]

    title = "Head gyroscope data"

    fig, ax = plt.subplots()
    fig.canvas.set_window_title(title)
    # fig.set_size_inches(24.4, 6)
    fig.set_size_inches(21, 9)
    plt.title(title)
    plt.gcf().autofmt_xdate()

    plt.plot(x1, values1, marker='.', linestyle='--')
    plt.plot(x2, values2, marker='.', linestyle='--')

    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.legend([label1, label2])
    plt.show()


def prepareGliderGyroData(deviceId, neutralAccVector, axisCalibrationVector, startTimestamp, endTimestamp):
    reorientVector = qt_from_two_vectors(neutralAccVector, z_axis_vector)

    loadedGyrData = load_data_of(deviceId, cat_gyroscope)

    # calibratedGyrData = calibrateDataAxis(loadedGyrData, axisCalibrationVector)

    orientGyrData = orientate_data_using_quaternion(loadedGyrData, reorientVector)

    df = orientGyrData.df
    timeCutDf = df[(df[file_header_hostTimestamp] > startTimestamp) & (df[file_header_hostTimestamp] < endTimestamp)]

    return Data(orientGyrData.device, orientGyrData.category, timeCutDf)


def interpolateDatas(data1, data2):
    startTimestamp = max(data1.df[file_header_hostTimestamp].iloc[0], data2.df[file_header_hostTimestamp].iloc[0])
    endTimestamp = max(data1.df[file_header_hostTimestamp].iloc[-1], data2.df[file_header_hostTimestamp].iloc[-1])

    print("Start timestamp is %d, end timestamp is %d" % (startTimestamp, endTimestamp))

    interpolatedData = interpolate_data(data1, 10, startTimestamp, endTimestamp)

    print("Pre interp")
    print(data1.df.iloc[0:10])
    print("Interpolated data start: \n")
    print(interpolatedData.df.iloc[0:10])

    print("Interp data size is %d" % len(interpolatedData.df.index))
    return interpolatedData


def calibrateDataAxis(data, calibrationVector):
    result = copy.deepcopy(data)

    result.df[result.df.columns[5]] = result.df[result.df.columns[5]] - calibrationVector[0]
    result.df[result.df.columns[6]] = result.df[result.df.columns[6]] - calibrationVector[1]
    result.df[result.df.columns[7]] = result.df[result.df.columns[7]] - calibrationVector[2]

    return result


def cumulateZAxisData(headData):
    headTime = headData.df[file_header_hostTimestamp]
    headZAxis = headData.df[file_header_Z_dps]

    headIntegratedData = integrate.cumtrapz(headZAxis, headTime, initial=0) / 1000

    result = copy.deepcopy(headData)
    result.df[file_header_Z_dps] = headIntegratedData

    return result


def getHeadRelativeAngle(headData, gliderData):
    cumulated = integrate.cumtrapz(headData.df[file_header_Z_dps] - gliderData.df[file_header_Z_dps],
                                   headData.df[file_header_hostTimestamp], initial=0) / 1000

    result = copy.deepcopy(headData)
    result.df[file_header_Z_dps] = cumulated

    return result


def filterAndCumulateData(headData):
    headTime = headData.df[file_header_hostTimestamp]
    headZAxis = headData.df[file_header_Z_dps]

    headIntegratedData = integrate.cumtrapz(headZAxis, headTime, initial=0) / 1000

    result = copy.deepcopy(headData)
    result.df[file_header_Z_dps] = headIntegratedData

    return result


def detectPeaks(headData):
    zData = headData.df[file_header_Z_dps]
    turnings = np.zeros(zData.size)

    avgFilter = np.zeros(zData.size)
    stdFilter = np.zeros(zData.size)
    infFilter = np.zeros(zData.size)

    avgFilter[lag - 1] = np.mean(zData.iloc[0:lag])
    stdFilter[lag - 1] = np.std(zData.iloc[0:lag])

    for i in range(lag, zData.size):
        # print("It: %d, val: %f, avgFilter: %f, stdDev: %f" % (i, zData.iloc[i], avgFilter[i - 1], stdFilter[i - 1]))
        if np.absolute(zData.iloc[i] - avgFilter[i - 1]) > angleThreshold:
            if zData.iloc[i] > avgFilter[i - 1]:
                turnings[i] = 100
            else:
                turnings[i] = -100

            infFilter[i] = influence * zData.iloc[i] + (1 - influence) * infFilter[i - 1]
        else:
            infFilter[i] = zData.iloc[i]

        avgFilter[i] = np.mean(infFilter[(i - lag + 1):(i + 1)])
        stdFilter[i] = np.std(infFilter[(i - lag + 1):(i + 1)])

    result = copy.deepcopy(headData)
    result.df[file_header_X_dps] = stdFilter
    result.df[file_header_Y_dps] = avgFilter
    result.df[file_header_Z_dps] = turnings

    print("Result peaks")
    print(result.df.iloc[25:40])

    return result


def filterDataWithThreshold(headData):
    # headData.df[(headData.df[file_header_Z_dps] < 20) & (headData.df[file_header_Z_dps] > -20)] = 0

    headData.df.ix[(headData.df[file_header_Z_dps] < 30) & (headData.df[file_header_Z_dps] > -30), file_header_Z_dps] = 0
    print("FIltering... \n")
    # print(headData.df)
    print(headData.df.ix[(headData.df[file_header_Z_dps] < 30) & (headData.df[file_header_Z_dps] > -30), file_header_Z_dps])
    return headData


def plotResult(headGyroData, headCumulatedData):
    fig, ax = plt.subplots()
    fig.set_size_inches(24.4, 6)

    plt.plot(headGyroData.df[file_header_real_time], headGyroData.df[file_header_Z_dps], marker='.', linestyle='--')
    plt.plot(headCumulatedData.df[file_header_real_time], headCumulatedData.df[file_header_Z_dps], marker='.', linestyle='--')

    plt.title("Cumulative trapeze integration")
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.legend(["Head data", "Glider data"])
    plt.show()


def plotResult2(originalHeadData, peaksData):
    fig, ax = plt.subplots()
    fig.set_size_inches(24.4, 6)

    # cumulatedData
    plt.plot(originalHeadData.df[file_header_real_time], originalHeadData.df[file_header_Z_dps], marker='.', linestyle='--')
    # moving average
    plt.plot(peaksData.df[file_header_real_time], peaksData.df[file_header_Y_dps], marker='.', linestyle='--')
    # detected peak
    plt.plot(peaksData.df[file_header_real_time], peaksData.df[file_header_Z_dps], marker='.', linestyle='-')

    plt.title("Cumulative trapeze integration")
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.legend(["Head data", "Average", "Lower std", "Upper std", "Peaks"])
    plt.show()


def run():
    startTime = 550000
    endTime = 1400000

    headTimeCutData = prepareGliderGyroData(dev_head, head_neutral_acc_vector, head_gyro_calibration_vector,
                                            startTime, endTime)

    # print("Data \n")
    # print(filteredData.df)

    cumulatedData = filterAndCumulateData(headTimeCutData)
    detectedPeaks = detectPeaks(cumulatedData)

    plotResult2(cumulatedData, detectedPeaks)


if __name__ == "__main__":
    run()
